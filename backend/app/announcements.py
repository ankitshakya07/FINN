"""Corporate announcement collection, normalization, classification and storage.

Exchange endpoints are public web interfaces rather than supported paid APIs;
callers should keep date windows narrow and configure a polite request interval.
Access-denied responses are treated as a source failure and are never bypassed.
"""
from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import logging
import math
import os
import re
import time
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from datetime import date, datetime, time as day_time, timedelta, timezone
from difflib import SequenceMatcher
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import httpx
from pydantic import BaseModel, Field, ValidationError

from .db import connect, init_db
from .llm import generate_json
from .prices import normalize_ticker

logger = logging.getLogger("finn.announcements")

TAXONOMY = (
    "results", "M&A", "fund_raise", "management_change", "litigation",
    "insider_trading", "earnings_call", "investor_meetings", "credit_rating",
    "dividend", "bonus_split", "capex", "press_release", "postal_ballot",
    "agm_egm", "pledging", "unclassified",
)
TAXONOMY_SET = frozenset(TAXONOMY)
IST = ZoneInfo("Asia/Kolkata")
UTC = timezone.utc
DEFAULT_FIXTURE = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "announcements.json"
BSE_API = "https://api.bseindia.com/BseIndiaAPI/api"
BSE_ANNOUNCEMENT_URL = f"{BSE_API}/AnnSubCategoryGetData/w"
BSE_SECURITY_MASTER_URL = f"{BSE_API}/ListofScripData/w"
BSE_ATTACHMENT_ROOT = "https://www.bseindia.com/xml-data/corpfiling/AttachLive/"
NSE_HOME_URL = "https://www.nseindia.com/"
NSE_ANNOUNCEMENT_URL = "https://www.nseindia.com/api/corporate-announcements"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en;q=0.9",
    "Cache-Control": "no-cache",
    "DNT": "1",
}
_BSE_HEADERS = {
    **_HEADERS,
    "Origin": "https://www.bseindia.com",
    "Referer": "https://www.bseindia.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}
_NSE_HEADERS = {
    **_HEADERS,
    "Origin": "https://www.nseindia.com",
    "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-announcements",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


class AnnouncementSourceError(RuntimeError):
    """A source could not be used without crossing an access restriction."""


class MappingNotFound(LookupError):
    """No verified, unambiguous BSE scrip mapping exists for this NSE ticker."""


def _env_int(name: str, default: int, minimum: int = 0) -> int:
    try:
        return max(minimum, int(os.getenv(name, str(default))))
    except ValueError:
        return default


def _env_float(name: str, default: float, minimum: float = 0.0) -> float:
    try:
        value = float(os.getenv(name, str(default)))
        return value if math.isfinite(value) and value >= minimum else default
    except ValueError:
        return default


class ModelAssessment(BaseModel):
    index: int = Field(ge=0)
    classification: str
    confidence: float = Field(ge=0, le=1)
    materiality_adjustment: float = Field(default=0, ge=-10, le=10)
    reason: str = ""


class ModelBatch(BaseModel):
    results: list[ModelAssessment]


def parse_timestamp(value: Any, *, assume_timezone: ZoneInfo = IST) -> datetime:
    """Parse exchange timestamps and return an aware UTC datetime."""
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, day_time.min)
    elif isinstance(value, (int, float)) and math.isfinite(float(value)):
        epoch = float(value)
        if abs(epoch) > 10**12:
            epoch /= 1000
        parsed = datetime.fromtimestamp(epoch, UTC)
    elif isinstance(value, str):
        raw = value.strip()
        if not raw:
            raise ValueError("announcement timestamp is empty")
        parsed = None
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            pass
        if parsed is None:
            for fmt in (
                "%d %b %Y %H:%M:%S", "%d-%b-%Y %H:%M:%S", "%d-%m-%Y %H:%M:%S",
                "%d/%m/%Y %H:%M:%S", "%d-%m-%Y %H:%M", "%d/%m/%Y %H:%M",
                "%d-%m-%Y", "%d/%m/%Y", "%Y%m%d", "%b %d %Y %I:%M%p",
                "%b %d, %Y %I:%M %p", "%Y-%m-%d", "%d%m%Y%H%M%S", "%Y%m%d%H%M%S",
            ):
                try:
                    parsed = datetime.strptime(raw, fmt)
                    break
                except ValueError:
                    continue
        if parsed is None:
            raise ValueError(f"unrecognised announcement timestamp: {value!r}")
    else:
        raise ValueError(f"unsupported announcement timestamp: {value!r}")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=assume_timezone)
    return parsed.astimezone(UTC)


def _key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).casefold())


def _pick(row: Mapping[str, Any], *names: str) -> Any:
    normalized = {_key(k): v for k, v in row.items()}
    for name in names:
        value = normalized.get(_key(name))
        if value is not None and str(value).strip() != "":
            return value
    return None


def normalized_headline(value: str) -> str:
    text = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(re.findall(r"[a-z0-9]+", text))


def announcement_fingerprint(
    ticker: str, timestamp: datetime | str, headline: str, source: str | None = None
) -> str:
    normalized_time = parse_timestamp(timestamp).isoformat(timespec="seconds")
    parts = [normalize_ticker(ticker), normalized_time, normalized_headline(headline)]
    if source:
        parts.append(source.casefold())
    content = "|".join(parts)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _source_id(raw: Mapping[str, Any]) -> str | None:
    value = _pick(
        raw, "NEWSID", "ANNOUNCEMENTID", "ANN_ID", "SEQ_ID", "SEQID", "SOURCE_ID", "SOURCE_IDENTIFIER", "ID",
        "ANNOUNCEMENT_ID", "NEWS_ID",
    )
    return str(value).strip() if value is not None else None


def _attachment(raw: Mapping[str, Any], source: str) -> str | None:
    value = _pick(
        raw, "ATTACHMENTNAME", "ATTACHMENTURL", "ATTCHMNTFILE", "ATTACHMENT_FILE",
        "PDF_URL", "PDFURL", "DOCUMENT_URL", "DOCUMENTURL",
    )
    if not value:
        return None
    value = str(value).strip()
    if value.startswith(("https://", "http://")):
        return value
    if source == "bse":
        return urljoin(BSE_ATTACHMENT_ROOT, value.lstrip("/"))
    if source == "nse":
        return urljoin("https://www.nseindia.com/", value.lstrip("/"))
    return value


def normalize_announcement(raw: Mapping[str, Any], ticker: str, source: str) -> dict[str, Any]:
    """Convert BSE/NSE/fixture records to FINN's stable announcement shape."""
    canonical_ticker = normalize_ticker(ticker)
    headline = _pick(
        raw, "NEWSSUB", "NEWS_SUB", "HEADLINE", "SUBJECT", "DESC", "DESCRIPTION",
        "ANNOUNCEMENT", "TITLE", "SUMMARY",
    )
    if headline is None:
        raise ValueError("announcement headline is missing")
    headline = " ".join(str(headline).split())
    stamp = _pick(
        raw, "DT_TM", "DT", "ANN_DT", "AN_DT", "ANN_DATE", "ANN_TSTAMP", "SORT_DATE",
        "TIMESTAMP", "FILED_AT", "FILEDDATE", "DATE",
    )
    timestamp = parse_timestamp(stamp)
    raw_category = _pick(raw, "CATEGORYNAME", "CATEGORY", "SUBCATEGORY", "SUB_CAT", "TYPE", "ANN_TYPE")
    source_id = _source_id(raw)
    fingerprint = announcement_fingerprint(canonical_ticker, timestamp, headline, source)
    cross_source_fingerprint = announcement_fingerprint(canonical_ticker, timestamp, headline)
    identifier = source_id or fingerprint
    id_source = source.casefold()
    normalized_id = hashlib.sha256(f"{id_source}|{canonical_ticker}|{identifier}".encode()).hexdigest()
    return {
        "id": normalized_id,
        "ticker": canonical_ticker,
        "timestamp": timestamp.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "headline": headline,
        "raw_category": str(raw_category).strip() if raw_category is not None else None,
        "attachment_url": _attachment(raw, source.casefold()),
        "source": source.casefold(),
        "source_identifier": source_id,
        "raw_metadata": dict(raw),
        "fingerprint": fingerprint,
        "cross_source_fingerprint": cross_source_fingerprint,
    }


_RULES: tuple[tuple[str, tuple[str, ...], float], ...] = (
    ("results", (r"\bquarterly\s+(?:and\s+)?(?:annual\s+)?results?\b", r"\bfinancial results?\b", r"\bunaudited results?\b", r"\baudited results?\b", r"\bresults for (?:the )?(?:quarter|year|half year)\b", r"\bresults?\b"), .99),
    # Person-level share dealings must not be mistaken for corporate M&A.
    ("insider_trading", (r"\b(?:insider trading|trading window|structured digital database|regulation 29|regulation 30|sast disclosure|acquisition or disposal of shares by promoter|acquisition of shares by (?:a )?(?:promoter|designated person|insider)|trades by designated persons)\b",), .95),
    ("M&A", (r"\bM\s*&\s*A\b", r"\b(?:merger|amalgamation|acquisition|acquire[sd]?|takeover|scheme of arrangement|business transfer|divest(?:ment|iture))\b", r"\bjoint venture\b"), .97),
    ("fund_raise", (r"\b(?:qualified institutional placement|\bqip\b|fund raising|fund raise|rights issue|preferential issue|preferential allotment|public issue|private placement|issuance of (?:bonds|debentures|non convertible)\b|issue of shares for cash)\b",), .96),
    ("management_change", (r"\bmanagement change\b", r"\b(?:chief executive officer|\bceo\b|chief financial officer|\bcfo\b|managing director|\bmd\b).{0,45}\b(?:appoint|resign|resignat|ceas|retir|transition|reappoint|cessation)\w*\b", r"\b(?:appoint|resign|resignat|ceas|retir|reappoint|cessation)\w*.{0,45}\b(?:chief executive officer|\bceo\b|chief financial officer|\bcfo\b|managing director|\bmd\b)\b", r"\b(?:director|independent director|whole time director|non executive director).{0,45}\b(?:appoint|resign|resignat|ceas|retir|reappoint|cessation)\w*\b", r"\b(?:appoint|resign|resignat|ceas|retir|reappoint|cessation)\w*.{0,45}\b(?:director|independent director|whole time director|non executive director)\b"), .97),
    ("litigation", (r"\b(?:court|tribunal|nclt|nclat|sebi|regulator|regulatory).{0,50}\b(?:order|penalty|fine|notice|judg|proceeding|direction|adjudicat)\w*\b", r"\b(?:penalty|fine|show cause notice|legal proceeding|litigation|search and seizure|tax demand|regulatory order)\b"), .95),
    ("earnings_call", (r"\b(?:earnings|investor|analyst) (?:conference )?call\b", r"\bcon[- ]?call\b", r"\bconference call transcript\b"), .96),
    ("investor_meetings", (r"\b(?:investor|analyst) (?:meeting|meet|conference|presentation)\b", r"\broadshow\b"), .94),
    ("credit_rating", (r"\b(?:credit )?rating\b", r"\brating action\b"), .94),
    ("dividend", (r"\b(?:interim|final|special|proposed|declared|declar\w*) dividend\b", r"\bdividend on equity shares\b"), .96),
    ("bonus_split", (r"\bbonus issue\b", r"\bstock split\b", r"\bsub[- ]?division of shares\b", r"\bsplit of equity shares\b"), .96),
    ("capex", (r"\b(?:capital expenditure|capex|new plant|manufacturing facility|capacity expansion|investment in (?:a )?plant|commission(?:ing|ed) of plant|project commissioning)\b",), .94),
    ("postal_ballot", (r"\bpostal ballot\b",), .98),
    ("agm_egm", (r"\b(?:annual general meeting|extraordinary general meeting|\bagm\b|\begm\b)\b",), .97),
    ("pledging", (r"\b(?:pledge|pledging|release of pledge|invocation of pledge|encumbrance of shares)\b",), .95),
    ("press_release", (r"\bpress release\b", r"\bmedia release\b"), .9),
)

_ROUTINE_RE = re.compile(r"\b(?:compliance certificate|regulation 30 compliance|secretarial compliance|shareholding pattern|investor grievance|corporate governance report|reconciliation of share capital|newspaper publication|trading window closure)\b", re.I)
_ESOP_RE = re.compile(r"\b(?:esop|employee stock option).{0,50}\b(?:allot|allotment|exercise|vest)\w*\b", re.I)
_SENIOR_ROLE_RE = re.compile(r"\b(?:chief executive officer|\bceo\b|chief financial officer|\bcfo\b|managing director|\bmd\b)\b", re.I)
_RATING_DOWN_RE = re.compile(r"\b(?:downgrad\w*|negative outlook|rating lowered|rating revised down|reduced to)\b", re.I)
_RATING_UP_RE = re.compile(r"\b(?:upgrad\w*|positive outlook|rating enhanced|rating revised up|improved to)\b", re.I)
_RATING_REAFFIRM_RE = re.compile(r"\b(?:reaffirm\w*|affirm\w*|maintain\w*|unchanged|no change in rating)\b", re.I)


def classify_rules(headline: str, raw_category: str | None = None) -> dict[str, Any]:
    text = f"{headline} {raw_category or ''}".casefold()
    if _ROUTINE_RE.search(text) or _ESOP_RE.search(text):
        return {"classification": "unclassified", "classification_method": "rules", "classification_confidence": .98}
    for category, patterns, confidence in _RULES:
        if any(re.search(pattern, text, re.I) for pattern in patterns):
            return {"classification": category, "classification_method": "rules", "classification_confidence": confidence}
    return {"classification": "unclassified", "classification_method": "rules", "classification_confidence": 0.0}


def materiality_base_score(classification: str, headline: str = "", raw_category: str | None = None) -> tuple[float, str]:
    text = f"{headline} {raw_category or ''}"
    if _ROUTINE_RE.search(text) or _ESOP_RE.search(text):
        return 1.0, "Routine compliance or ESOP allotment"
    if classification == "results":
        return 9.0, "Quarterly or annual results"
    if classification == "M&A":
        return 8.0, "Merger, acquisition or material business combination"
    if classification == "management_change":
        if _SENIOR_ROLE_RE.search(text):
            return 8.0, "CEO, CFO or managing director change"
        return 5.0, "Other director or management change"
    if classification == "litigation":
        return 7.0, "Litigation, regulatory order or penalty"
    if classification == "fund_raise":
        return 7.0, "Fund raising or securities issuance"
    if classification == "credit_rating":
        if _RATING_DOWN_RE.search(text):
            return 7.0, "Credit rating downgrade or negative outlook"
        if _RATING_UP_RE.search(text):
            return 6.0, "Credit rating upgrade or positive outlook"
        if _RATING_REAFFIRM_RE.search(text):
            return 3.0, "Credit rating reaffirmed or maintained"
        return 5.0, "Credit rating action; direction not stated"
    defaults = {
        "capex": (6.0, "Capital expenditure or capacity expansion"),
        "dividend": (5.0, "Dividend action"),
        "pledging": (6.0, "Promoter pledge or encumbrance change"),
        "insider_trading": (4.0, "Insider or designated-person trading disclosure"),
        "earnings_call": (3.0, "Earnings call or transcript notice"),
        "investor_meetings": (2.0, "Investor or analyst meeting notice"),
        "postal_ballot": (1.0, "Postal ballot notice"),
        "agm_egm": (1.0, "AGM or EGM notice"),
        "bonus_split": (4.0, "Bonus issue or share split; conservative default"),
        "press_release": (2.0, "General press or media release; conservative default"),
        "unclassified": (0.0, "No supported materiality category"),
    }
    return defaults.get(classification, (0.0, "No supported materiality category"))


def calculate_materiality(
    classification: str,
    headline: str,
    raw_category: str | None = None,
    model_adjustment: float = 0.0,
) -> dict[str, Any]:
    if classification not in TAXONOMY_SET:
        classification = "unclassified"
    base, reason = materiality_base_score(classification, headline, raw_category)
    requested = float(model_adjustment)
    if not math.isfinite(requested):
        requested = 0.0
    adjustment = max(-2.0, min(2.0, requested))
    score = max(0.0, min(10.0, base + adjustment))
    detail = reason
    if adjustment:
        detail += f"; model adjustment {adjustment:+g}"
    return {
        "materiality_base_score": base,
        "materiality_score": score,
        "materiality_reason": detail,
        "model_adjustment": adjustment,
    }


def _clean_summary(headline: str, score: float) -> str | None:
    if score < 5:
        return None
    # The headline itself is source-grounded; do not manufacture details absent from it.
    one_line = " ".join(headline.split())
    return one_line[:277].rstrip() + "..." if len(one_line) > 280 else one_line


def enrich_announcement(item: Mapping[str, Any], model_adjustment: float = 0.0) -> dict[str, Any]:
    enriched = dict(item)
    classification = classify_rules(str(item["headline"]), item.get("raw_category"))
    enriched.update(classification)
    if classification["classification"] == "unclassified":
        enriched["classification_method"] = "unclassified"
    scores = calculate_materiality(
        enriched["classification"], str(item["headline"]), item.get("raw_category"), model_adjustment
    )
    enriched.update(scores)
    enriched["summary"] = _clean_summary(str(item["headline"]), scores["materiality_score"])
    return enriched


def _frame_enrichment(item: Mapping[str, Any], assessment: ModelAssessment) -> dict[str, Any]:
    enriched = dict(item)
    category = assessment.classification if assessment.classification in TAXONOMY_SET else "unclassified"
    if category == "unclassified":
        enriched["classification"] = category
        enriched["classification_method"] = "unclassified"
        enriched["classification_confidence"] = 0.0
        adjustment = 0.0
    else:
        enriched["classification"] = category
        enriched["classification_method"] = "model"
        enriched["classification_confidence"] = assessment.confidence
        adjustment = assessment.materiality_adjustment
    scores = calculate_materiality(category, str(item["headline"]), item.get("raw_category"), adjustment)
    enriched.update(scores)
    enriched["summary"] = _clean_summary(str(item["headline"]), scores["materiality_score"])
    return enriched


async def classify_unresolved(
    items: Sequence[Mapping[str, Any]],
    *,
    db_path: str | None = None,
    model_call: Callable[..., Any] | None = None,
) -> list[dict[str, Any]]:
    """Classify rule-unresolved records in requests of at most 20 rows.

    Existing `generate_json` supplies deterministic prompt hashing, SQLite cache,
    schema validation, retry limits and token-cost logging. No model key is
    required for the deterministic or fixture paths.
    """
    enriched = [enrich_announcement(item) for item in items]
    unresolved = [
        i for i, item in enumerate(enriched)
        if item["classification"] == "unclassified" and item["classification_confidence"] < .8
    ]
    if not unresolved:
        return enriched
    caller = model_call or generate_json
    system = (
        "Classify Indian listed-company exchange announcements conservatively. "
        "Use only the provided headline and raw category. Return only the supplied taxonomy. "
        "Never infer facts. If uncertain, use unclassified. Score adjustment must be contextual and small."
    )
    _llm_logged = False
    for start in range(0, len(unresolved), 20):
        batch_indices = unresolved[start:start + 20]
        rows = [{
            "index": local_index,
            "ticker": enriched[global_index]["ticker"],
            "headline": enriched[global_index]["headline"],
            "raw_category": enriched[global_index].get("raw_category"),
            "taxonomy": list(TAXONOMY),
        } for local_index, global_index in enumerate(batch_indices)]
        user = json.dumps({"announcements": rows}, ensure_ascii=False, sort_keys=True)
        try:
            if not os.getenv("LLM_API_KEY") and model_call is None:
                if not _llm_logged:
                    logger.info("LLM_API_KEY is not configured; leaving unresolved announcements unclassified")
                    _llm_logged = True
                continue
            response = caller(
                system=system, user=user, schema=ModelBatch, tier="small", temperature=0,
                db_path=db_path,
            )
            if asyncio.iscoroutine(response):
                response = await response
            validated = ModelBatch.model_validate(response)
            by_index = {result.index: result for result in validated.results}
            for local_index, global_index in enumerate(batch_indices):
                assessment = by_index.get(local_index)
                if assessment is None:
                    continue
                enriched[global_index] = _frame_enrichment(enriched[global_index], assessment)
        except (Exception, ValidationError) as exc:
            # Model outage or malformed data must never create invented labels.
            if not _llm_logged:
                logger.warning("announcement_model_unavailable: %s", exc)
                _llm_logged = True
    return enriched


def _ensure_company(ticker: str, name: str | None, isin: str | None, db_path: str | None) -> None:
    with connect(db_path) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO companies(ticker,name,isin) VALUES(?,?,?)",
            (ticker, (name or ticker).strip(), isin),
        )
        if name and isin:
            conn.execute(
                "UPDATE companies SET isin=COALESCE(isin, ?) WHERE ticker=?", (isin, ticker)
            )


def _merge_metadata(existing_json: str, incoming: Mapping[str, Any], source: str, source_id: str | None) -> str:
    try:
        metadata = json.loads(existing_json)
    except (TypeError, json.JSONDecodeError):
        metadata = {}
    sources = set(metadata.get("duplicate_sources", []))
    sources.add(source)
    ids = set(metadata.get("duplicate_source_identifiers", []))
    if source_id:
        ids.add(f"{source}:{source_id}")
    metadata["duplicate_sources"] = sorted(sources)
    metadata["duplicate_source_identifiers"] = sorted(ids)
    # Keep the first raw payload intact and append cross-source evidence.
    observations = metadata.get("duplicate_raw_metadata", [])
    observations.append(dict(incoming))
    metadata["duplicate_raw_metadata"] = observations[-10:]
    return json.dumps(metadata, ensure_ascii=False, default=str, sort_keys=True)


def persist_announcements(items: Iterable[Mapping[str, Any]], *, db_path: str | None = None) -> int:
    """Idempotently store normalized/enriched records; return newly inserted count."""
    init_db(db_path)
    inserted = 0
    for item in items:
        _ensure_company(str(item["ticker"]), item.get("company_name"), item.get("isin"), db_path)
        raw_json = json.dumps(item.get("raw_metadata", {}), ensure_ascii=False, default=str, sort_keys=True)
        source_identity = (
            f"{item['source']}:{item['ticker']}:{item['source_identifier']}"
            if item.get("source_identifier") else None
        )
        is_demo_data = 1 if (
            str(item.get("source", "")).startswith("fixture")
            or bool(item.get("demo_data"))
            or bool(item.get("raw_metadata", {}).get("demo_data"))
        ) else 0
        with connect(db_path) as conn:
            before = conn.total_changes
            conn.execute(
                """INSERT OR IGNORE INTO announcements
                   (id,ticker,timestamp,headline,raw_category,attachment_url,source,source_identifier,source_identity,
                   raw_metadata_json,fingerprint,cross_source_fingerprint,classification,classification_method,
                    classification_confidence,materiality_base_score,materiality_score,
                    materiality_reason,summary,demo_data)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    item["id"], item["ticker"], item["timestamp"], item["headline"], item.get("raw_category"),
                    item.get("attachment_url"), item["source"], item.get("source_identifier"), source_identity, raw_json,
                    item["fingerprint"], item["cross_source_fingerprint"], item.get("classification", "unclassified"),
                    item.get("classification_method", "unclassified"),
                    float(item.get("classification_confidence", 0)),
                    float(item.get("materiality_base_score", 0)), float(item.get("materiality_score", 0)),
                    item.get("materiality_reason", ""), item.get("summary"), is_demo_data,
                ),
            )
            inserted += int(conn.total_changes > before)
            if conn.total_changes == before:
                existing = conn.execute(
                    """SELECT id,raw_metadata_json FROM announcements
                       WHERE fingerprint=? OR cross_source_fingerprint=? OR (? IS NOT NULL AND source_identity=?)""",
                    (item["fingerprint"], item["cross_source_fingerprint"], source_identity, source_identity),
                ).fetchone()
                if existing:
                    merged = _merge_metadata(
                        existing["raw_metadata_json"], item.get("raw_metadata", {}),
                        str(item["source"]), item.get("source_identifier"),
                    )
                    conn.execute("UPDATE announcements SET raw_metadata_json=?, demo_data=MAX(COALESCE(demo_data, 0), ?) WHERE id=?", (merged, is_demo_data, existing["id"]))
    return inserted
    return inserted


def _rows_from_payload(payload: Any) -> list[Mapping[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, Mapping)]
    if isinstance(payload, Mapping):
        for key in ("Table", "data", "announcements", "rows", "records"):
            value = payload.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, Mapping)]
    return []


def _request_delay(response: httpx.Response | None, attempt: int) -> float:
    if response is not None:
        value = response.headers.get("Retry-After")
        if value:
            try:
                return max(0, min(float(value), 30))
            except ValueError:
                try:
                    return max(0, min((parsedate_to_datetime(value) - datetime.now(UTC)).total_seconds(), 30))
                except (TypeError, ValueError, OverflowError):
                    pass
    return float(min(2**attempt, 30))


def _get_with_retries(
    client: httpx.Client,
    url: str,
    *,
    params: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
    retries: int = 3,
    sleep: Callable[[float], None] = time.sleep,
) -> httpx.Response:
    last: Exception | None = None
    for attempt in range(retries + 1):
        response: httpx.Response | None = None
        try:
            response = client.get(url, params=params, headers=headers)
            if response.status_code in (401, 403):
                raise AnnouncementSourceError(
                    f"Source denied access (HTTP {response.status_code}); no access-control bypass attempted"
                )
            if response.status_code in (408, 425, 429) or response.status_code >= 500:
                last = AnnouncementSourceError(f"Source temporarily unavailable (HTTP {response.status_code})")
                if attempt < retries:
                    sleep(_request_delay(response, attempt))
                    continue
                break
            response.raise_for_status()
            return response
        except AnnouncementSourceError:
            raise
        except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError, httpx.HTTPStatusError) as exc:
            last = exc
            if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code < 500:
                raise AnnouncementSourceError(f"Source returned HTTP {exc.response.status_code}") from exc
            if attempt < retries:
                sleep(_request_delay(response, attempt))
    raise AnnouncementSourceError(f"Source request failed after {retries + 1} attempts: {last}") from last


def _managed_client(
    client: httpx.Client | None, headers: Mapping[str, str], timeout: float
) -> tuple[httpx.Client, bool]:
    return (client, False) if client is not None else (httpx.Client(headers=headers, timeout=timeout, follow_redirects=True), True)


def _check_dates(from_date: date, to_date: date) -> None:
    if from_date > to_date:
        raise ValueError("from_date must not be after to_date")


def fetch_bse_announcements(
    scrip_code: str,
    from_date: date,
    to_date: date,
    *,
    client: httpx.Client | None = None,
    retries: int | None = None,
    request_interval: float | None = None,
    sleep: Callable[[float], None] = time.sleep,
    max_pages: int = 500,
) -> list[Mapping[str, Any]]:
    """Fetch paginated BSE announcements for one verified scrip code."""
    _check_dates(from_date, to_date)
    retries = _env_int("ANNOUNCEMENT_RETRIES", 3, 0) if retries is None else retries
    request_interval = _env_float("ANNOUNCEMENT_REQUEST_INTERVAL_SECONDS", 1.0) if request_interval is None else request_interval
    if retries < 0 or not math.isfinite(request_interval) or request_interval < 0:
        raise ValueError("retries must be non-negative and request_interval must be finite and non-negative")
    if not scrip_code or not re.fullmatch(r"\d{1,8}", str(scrip_code)):
        raise MappingNotFound("BSE requests require a verified numeric scrip code")
    managed, owned = _managed_client(client, _BSE_HEADERS, _env_float("ANNOUNCEMENT_TIMEOUT_SECONDS", 15, .1))
    found: list[Mapping[str, Any]] = []
    last_request = 0.0
    try:
        total_rows: int | None = None
        for page_no in range(1, max_pages + 1):
            if last_request:
                delay = request_interval - (time.monotonic() - last_request)
                if delay > 0:
                    sleep(delay)
            params = {
                "pageno": page_no,
                "strCat": "-1",
                "subcategory": "-1",
                "strPrevDate": from_date.strftime("%Y%m%d"),
                "strToDate": to_date.strftime("%Y%m%d"),
                "strSearch": "P",
                "strscrip": str(scrip_code),
                "strType": "C",
            }
            response = _get_with_retries(managed, BSE_ANNOUNCEMENT_URL, params=params, headers=_BSE_HEADERS, retries=retries, sleep=sleep)
            last_request = time.monotonic()
            try:
                payload = response.json()
            except ValueError as exc:
                raise AnnouncementSourceError("BSE returned invalid JSON") from exc
            found.extend(_rows_from_payload(payload))
            if isinstance(payload, Mapping):
                meta = payload.get("Table1") or payload.get("table1") or []
                if meta and isinstance(meta[0], Mapping):
                    try:
                        total_rows = int(_pick(meta[0], "ROWCNT", "total", "count") or 0)
                    except (ValueError, TypeError):
                        total_rows = None
            if total_rows is not None and len(found) >= total_rows:
                break
            rows = _rows_from_payload(payload)
            if not rows or (total_rows is None and len(rows) < 50):
                break
        else:
            logger.warning("BSE announcement pagination stopped at max_pages=%d", max_pages)
        return found
    finally:
        if owned:
            managed.close()


def fetch_nse_announcements(
    ticker: str,
    from_date: date,
    to_date: date,
    *,
    client: httpx.Client | None = None,
    retries: int | None = None,
    request_interval: float | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> list[Mapping[str, Any]]:
    """Warm an NSE session, then request announcements with the same cookie jar."""
    _check_dates(from_date, to_date)
    retries = _env_int("ANNOUNCEMENT_RETRIES", 3, 0) if retries is None else retries
    request_interval = _env_float("ANNOUNCEMENT_REQUEST_INTERVAL_SECONDS", 1.0) if request_interval is None else request_interval
    if retries < 0 or not math.isfinite(request_interval) or request_interval < 0:
        raise ValueError("retries must be non-negative and request_interval must be finite and non-negative")
    symbol = normalize_ticker(ticker)
    managed, owned = _managed_client(client, _NSE_HEADERS, _env_float("ANNOUNCEMENT_TIMEOUT_SECONDS", 15, .1))
    try:
        warm = _get_with_retries(managed, NSE_HOME_URL, headers={**_HEADERS, "Accept": "text/html,application/xhtml+xml"}, retries=retries, sleep=sleep)
        if warm.status_code >= 400:
            raise AnnouncementSourceError(f"NSE cookie handshake failed (HTTP {warm.status_code})")
        if request_interval:
            sleep(request_interval)
        params = {
            "index": "equities",
            "symbol": symbol,
            "from_date": from_date.strftime("%d-%m-%Y"),
            "to_date": to_date.strftime("%d-%m-%Y"),
        }
        response = _get_with_retries(managed, NSE_ANNOUNCEMENT_URL, params=params, headers=_NSE_HEADERS, retries=retries, sleep=sleep)
        try:
            payload = response.json()
        except ValueError as exc:
            raise AnnouncementSourceError("NSE returned invalid JSON") from exc
        return _rows_from_payload(payload)
    finally:
        if owned:
            managed.close()


def _security_record_fields(record: Mapping[str, Any]) -> dict[str, str | None]:
    code = _pick(record, "scrip_code", "scripcode", "scrip_cd", "security_code", "securitycode", "sc_code")
    isin = _pick(record, "isin", "isin_code", "isinno")
    name = _pick(record, "company_name", "security_name", "scrip_name", "scripname", "name", "security_desc", "company")
    nse_symbol = _pick(record, "nse_symbol", "nse_ticker", "nse_symbol_code")
    return {
        "bse_scrip_code": str(code).strip() if code is not None else None,
        "isin": str(isin).strip().upper() if isin is not None else None,
        "company_name": " ".join(str(name).split()) if name is not None else None,
        "nse_symbol": str(nse_symbol).strip().upper() if nse_symbol is not None else None,
    }


def parse_security_master(payload: Any) -> list[Mapping[str, Any]]:
    """Accept the BSE JSON list or a CSV security-master download."""
    if isinstance(payload, bytes):
        text = payload.decode("utf-8-sig", errors="replace")
        return list(csv.DictReader(text.splitlines()))
    if isinstance(payload, str):
        return list(csv.DictReader(payload.lstrip("\ufeff").splitlines()))
    return _rows_from_payload(payload)


def fetch_bse_security_master(
    *, client: httpx.Client | None = None, retries: int | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> list[Mapping[str, Any]]:
    configured = os.getenv("BSE_SECURITY_MASTER_URL", BSE_SECURITY_MASTER_URL)
    retries = _env_int("ANNOUNCEMENT_RETRIES", 3, 0) if retries is None else retries
    managed, owned = _managed_client(client, _BSE_HEADERS, _env_float("ANNOUNCEMENT_TIMEOUT_SECONDS", 15, .1))
    try:
        response = _get_with_retries(managed, configured, headers=_BSE_HEADERS, retries=retries, sleep=sleep)
        content_type = response.headers.get("content-type", "")
        if "json" in content_type or response.text.lstrip().startswith(("{", "[")):
            return parse_security_master(response.json())
        return parse_security_master(response.content)
    finally:
        if owned:
            managed.close()


def _normal_name(value: str | None) -> str:
    if not value:
        return ""
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().casefold()
    text = re.sub(r"\b(?:limited|ltd|private|pvt|company|co|the)\b", " ", text)
    return " ".join(re.findall(r"[a-z0-9]+", text))


def _invalidate_cached_mapping(ticker: str, reason: str, verified_at: str, db_path: str | None) -> None:
    """Keep historical mapping details but make an unsafe cache entry unusable."""
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT source_metadata_json FROM announcement_mappings WHERE ticker=?", (ticker,)
        ).fetchone()
        if not row:
            return
        try:
            metadata = json.loads(row["source_metadata_json"])
        except (TypeError, json.JSONDecodeError):
            metadata = {}
        metadata["invalidated_reason"] = reason
        metadata["invalidated_at"] = verified_at
        conn.execute(
            """UPDATE announcement_mappings SET mapping_source=?,mapping_confidence=0,
               last_verified_at=?,source_metadata_json=? WHERE ticker=?""",
            (f"invalidated:{reason}", verified_at,
             json.dumps(metadata, ensure_ascii=False, sort_keys=True), ticker),
        )


def refresh_bse_mappings(
    records: Sequence[Mapping[str, Any]] | None = None,
    *,
    db_path: str | None = None,
    client: httpx.Client | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Refresh cached ticker→BSE code mappings from a verified BSE master.

    Matching is ISIN first, explicit NSE symbol second, then unique exact/strong
    company-name matching. Ambiguous or weak name matches are reported, never saved.
    """
    init_db(db_path)
    master = list(records) if records is not None else fetch_bse_security_master(client=client)
    normalized_master = [(_security_record_fields(row), dict(row)) for row in master]
    with connect(db_path) as conn:
        companies = [dict(row) for row in conn.execute("SELECT ticker,name,isin FROM companies ORDER BY ticker")]
    verified_at = (now or datetime.now(UTC)).astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    report: dict[str, Any] = {"updated": 0, "ambiguous": {}, "missing": []}
    for company in companies:
        ticker = str(company["ticker"]).upper()
        name = str(company.get("name") or ticker)
        isin = (company.get("isin") or "").strip().upper()
        reason: str | None = None
        candidates: list[tuple[dict[str, str | None], dict[str, Any], float]] = []
        if isin:
            candidates = [(fields, raw, 1.0) for fields, raw in normalized_master if fields["isin"] == isin]
            if len(candidates) == 1:
                reason = "bse_security_master:isin"
        if not candidates:
            candidates = [(fields, raw, 1.0) for fields, raw in normalized_master if fields["nse_symbol"] == ticker]
            if len(candidates) == 1:
                reason = "bse_security_master:nse_symbol"
        if not candidates:
            target = _normal_name(name)
            scored = [
                (fields, raw, SequenceMatcher(None, target, _normal_name(fields["company_name"])).ratio())
                for fields, raw in normalized_master if fields["company_name"]
            ]
            scored.sort(key=lambda item: item[2], reverse=True)
            exact = [item for item in scored if _normal_name(item[0]["company_name"]) == target and target]
            if exact:
                candidates = exact
                reason = "bse_security_master:company_name_exact"
            elif scored and scored[0][2] >= .96 and (len(scored) == 1 or scored[0][2] - scored[1][2] >= .08):
                candidates = [scored[0]]
                reason = "bse_security_master:company_name_strong"
            elif scored and scored[0][2] >= .85:
                report["ambiguous"][ticker] = [
                    {"name": item[0]["company_name"], "score": round(item[2], 3)} for item in scored[:3]
                ]
                _invalidate_cached_mapping(ticker, "ambiguous_master_name", verified_at, db_path)
                continue
        valid = [item for item in candidates if item[0]["bse_scrip_code"] and re.fullmatch(r"\d{1,8}", item[0]["bse_scrip_code"] or "")]
        unique_codes = {item[0]["bse_scrip_code"] for item in valid}
        if len(valid) != 1 or len(unique_codes) != 1:
            if len(valid) > 1:
                report["ambiguous"].setdefault(ticker, [
                    {"name": item[0]["company_name"], "bse_scrip_code": item[0]["bse_scrip_code"]}
                    for item in valid[:3]
                ])
                _invalidate_cached_mapping(ticker, "ambiguous_master_code", verified_at, db_path)
            else:
                report["missing"].append(ticker)
                _invalidate_cached_mapping(ticker, "missing_from_master", verified_at, db_path)
            continue
        fields, raw, confidence = valid[0]
        with connect(db_path) as conn:
            conn.execute(
                """INSERT INTO announcement_mappings
                   (ticker,nse_symbol,company_name,bse_scrip_code,isin,mapping_source,mapping_confidence,last_verified_at,source_metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(ticker) DO UPDATE SET nse_symbol=excluded.nse_symbol,company_name=excluded.company_name,
                    bse_scrip_code=excluded.bse_scrip_code,isin=excluded.isin,
                    mapping_source=excluded.mapping_source,mapping_confidence=excluded.mapping_confidence,
                    last_verified_at=excluded.last_verified_at,source_metadata_json=excluded.source_metadata_json""",
                (ticker, ticker, name, fields["bse_scrip_code"], fields["isin"] or isin or None,
                 reason or "bse_security_master", confidence, verified_at,
                 json.dumps(raw, ensure_ascii=False, default=str, sort_keys=True)),
            )
        report["updated"] += 1
    return report


def get_bse_mapping(ticker: str, *, db_path: str | None = None) -> dict[str, Any]:
    canonical = normalize_ticker(ticker)
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM announcement_mappings WHERE ticker=?", (canonical,)).fetchone()
    if not row:
        raise MappingNotFound(f"No verified BSE scrip mapping for {canonical}; refresh the security master")
    mapping = dict(row)
    if mapping["mapping_confidence"] < .9 or str(mapping["mapping_source"]).startswith("invalidated:"):
        raise MappingNotFound(f"BSE mapping for {canonical} is ambiguous or invalidated; refresh the security master")
    freshness_days = _env_int("ANNOUNCEMENT_MAPPING_MAX_AGE_DAYS", 30, 1)
    verified_at = parse_timestamp(mapping["last_verified_at"])
    if datetime.now(UTC) - verified_at > timedelta(days=freshness_days):
        raise MappingNotFound(
            f"BSE mapping for {canonical} was last verified {mapping['last_verified_at']}; refresh the security master"
        )
    return mapping


def load_fixture_announcements(
    ticker: str | None = None,
    *,
    from_date: date | None = None,
    to_date: date | None = None,
    fixture_path: str | Path = DEFAULT_FIXTURE,
) -> list[dict[str, Any]]:
    data = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    rows = data.get("announcements", [])
    selected = []
    wanted = normalize_ticker(ticker) if ticker else None
    for row in rows:
        row_ticker = normalize_ticker(str(row.get("ticker", "")))
        if wanted and row_ticker != wanted:
            continue
        normalized = normalize_announcement(row, row_ticker, "fixture")
        stamp_date = parse_timestamp(normalized["timestamp"]).date()
        if from_date and stamp_date < from_date or to_date and stamp_date > to_date:
            continue
        normalized["raw_metadata"]["demo_data"] = True
        normalized["company_name"] = row.get("company_name")
        selected.append(normalized)
    return selected


def fixture_as_of(fixture_path: str | Path = DEFAULT_FIXTURE) -> datetime:
    try:
        data = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
        return parse_timestamp(data["as_of"])
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return datetime.now(UTC)


def company_info(ticker: str, *, db_path: str | None = None) -> dict[str, Any] | None:
    with connect(db_path) as conn:
        row = conn.execute("SELECT ticker,name,isin FROM companies WHERE ticker=?", (normalize_ticker(ticker),)).fetchone()
    return dict(row) if row else None


async def ingest_announcements(
    ticker: str,
    *,
    from_date: date,
    to_date: date,
    db_path: str | None = None,
    fixture_path: str | Path = DEFAULT_FIXTURE,
    demo_mode: bool = False,
    fallback_to_fixture: bool = True,
    bse_fetcher: Callable[..., list[Mapping[str, Any]]] = fetch_bse_announcements,
    nse_fetcher: Callable[..., list[Mapping[str, Any]]] = fetch_nse_announcements,
    model_call: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Fetch BSE→NSE→fixture, normalize, classify and idempotently persist."""
    canonical = normalize_ticker(ticker)
    _check_dates(from_date, to_date)
    info = company_info(canonical, db_path=db_path) or {"ticker": canonical, "name": canonical, "isin": None}
    source = ""
    failures: list[str] = []
    if demo_mode:
        normalized = load_fixture_announcements(canonical, from_date=from_date, to_date=to_date, fixture_path=fixture_path)
        source = "fixture"
    else:
        normalized = []
        try:
            mapping = get_bse_mapping(canonical, db_path=db_path)
            bse_rows = bse_fetcher(mapping["bse_scrip_code"], from_date, to_date)
            for raw_item in bse_rows:
                try:
                    normalized.append(normalize_announcement(raw_item, canonical, "bse"))
                except (TypeError, ValueError, KeyError) as exc:
                    failures.append(f"bse row ignored: {exc}")
            if normalized:
                source = "bse"
        except Exception as exc:
            failures.append(f"bse: {exc}")
            logger.info("BSE unavailable for %s: %s", canonical, exc)
        if not normalized:
            try:
                nse_rows = nse_fetcher(canonical, from_date, to_date)
                for raw_item in nse_rows:
                    try:
                        normalized.append(normalize_announcement(raw_item, canonical, "nse"))
                    except (TypeError, ValueError, KeyError) as exc:
                        failures.append(f"nse row ignored: {exc}")
                if normalized:
                    source = "nse"
            except Exception as exc:
                failures.append(f"nse: {exc}")
                logger.info("NSE unavailable for %s: %s", canonical, exc)
        if not normalized:
            if fallback_to_fixture or demo_mode:
                normalized = load_fixture_announcements(canonical, from_date=from_date, to_date=to_date, fixture_path=fixture_path)
                source = "fixture"
            else:
                source = "unavailable"
    for item in normalized:
        item.setdefault("company_name", info.get("name"))
        item.setdefault("isin", info.get("isin"))
    if source == "fixture":
        enriched = [enrich_announcement(item) for item in normalized]
        for item in enriched:
            item["classification_method"] = "rules" if item["classification"] != "unclassified" else "unclassified"
    else:
        enriched = await classify_unresolved(normalized, db_path=db_path, model_call=model_call)
    inserted = persist_announcements(enriched, db_path=db_path) if enriched else 0
    stored_items = get_announcements_by_fingerprints(enriched, db_path=db_path) if enriched else []
    return {
        "ticker": canonical,
        "source": source,
        "demo_mode": announcement_demo_mode(stored_items, source == "fixture"),
        "as_of": fixture_as_of(fixture_path) if source == "fixture" else datetime.now(UTC),
        "received": len(normalized),
        "inserted": inserted,
        "announcements": stored_items,
        "failures": failures,
    }


def list_announcements(
    *, ticker: str | None = None, category: str | None = None,
    min_materiality: float | None = None, limit: int = 100, offset: int = 0,
    db_path: str | None = None,
    exclude_demo: bool = False,
) -> list[dict[str, Any]]:
    if limit < 1 or limit > 500 or offset < 0:
        raise ValueError("limit must be 1..500 and offset must be non-negative")
    if category is not None and category not in TAXONOMY_SET:
        raise ValueError(f"category must be one of {', '.join(TAXONOMY)}")
    clauses: list[str] = []
    params: list[Any] = []
    if ticker:
        clauses.append("a.ticker=?")
        params.append(normalize_ticker(ticker))
    if category:
        clauses.append("a.classification=?")
        params.append(category)
    if min_materiality is not None:
        clauses.append("a.materiality_score>=?")
        params.append(min_materiality)
    if exclude_demo:
        clauses.append("(COALESCE(a.demo_data, 0) = 0 AND a.source != 'fixture')")
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    with connect(db_path) as conn:
        rows = conn.execute(
            f"SELECT a.*,c.name AS company_name FROM announcements a JOIN companies c ON c.ticker=a.ticker{where} ORDER BY a.timestamp DESC,a.id LIMIT ? OFFSET ?",
            (*params, limit, offset),
        ).fetchall()
    return [_serialize_row(row) for row in rows]


def load_demo_announcements_fixture(
    *, db_path: str | None = None, fixture_path: str | Path = DEFAULT_FIXTURE
) -> int:
    """Load announcements fixture into DB idempotently when DEMO_MODE=true."""
    init_db(db_path)
    items = load_fixture_announcements(fixture_path=fixture_path)
    enriched = [enrich_announcement(item) for item in items]
    for item in enriched:
        item["classification_method"] = "rules" if item["classification"] != "unclassified" else "unclassified"
        item["demo_data"] = True
    return persist_announcements(enriched, db_path=db_path)


def _serialize_row(row: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(row)
    try:
        result["raw_metadata"] = json.loads(result.pop("raw_metadata_json"))
    except (TypeError, json.JSONDecodeError):
        result["raw_metadata"] = {}
    created_at = result.get("created_at")
    if isinstance(created_at, str) and created_at and not re.search(r"(?:Z|[+-]\d{2}:?\d{2})$", created_at):
        result["created_at"] = created_at.replace(" ", "T", 1) + "Z"
    return result


def get_announcement(announcement_id: str, *, db_path: str | None = None) -> dict[str, Any] | None:
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT a.*,c.name AS company_name FROM announcements a JOIN companies c ON c.ticker=a.ticker WHERE a.id=?",
            (announcement_id,),
        ).fetchone()
    return _serialize_row(row) if row else None


def get_announcements_by_fingerprints(
    items: Sequence[Mapping[str, Any]], *, db_path: str | None = None
) -> list[dict[str, Any]]:
    fingerprints = list(dict.fromkeys(str(item["cross_source_fingerprint"]) for item in items))
    if not fingerprints:
        return []
    placeholders = ",".join("?" for _ in fingerprints)
    with connect(db_path) as conn:
        rows = conn.execute(
            f"SELECT a.*,c.name AS company_name FROM announcements a JOIN companies c ON c.ticker=a.ticker "
            f"WHERE a.cross_source_fingerprint IN ({placeholders}) ORDER BY a.timestamp DESC,a.id",
            fingerprints,
        ).fetchall()
    return [_serialize_row(row) for row in rows]


def announcement_demo_mode(items: Sequence[Mapping[str, Any]], configured_demo: bool = False) -> bool:
    return configured_demo or any(
        item.get("source") == "fixture"
        or item.get("raw_metadata", {}).get("demo_data") is True
        or "fixture" in item.get("raw_metadata", {}).get("duplicate_sources", [])
        for item in items
    )


def announcement_snapshot_as_of(
    items: Sequence[Mapping[str, Any]], configured_demo: bool = False,
    fixture_path: str | Path = DEFAULT_FIXTURE,
) -> datetime:
    if configured_demo or (items and all(item.get("source") == "fixture" for item in items)):
        return fixture_as_of(fixture_path)
    return datetime.now(UTC)

