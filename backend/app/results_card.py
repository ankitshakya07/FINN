"""Source-cited quarterly-results PDF extraction and deterministic calculations."""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Literal
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .db import connect
from .llm import generate_json, model_config

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parents[1]
PROMPT_PATH = ROOT_DIR / "prompts" / "results_extract.txt"
PDF_CACHE = Path(os.getenv("RESULTS_PDF_CACHE", ROOT_DIR / "data" / "cache" / "results_pdfs"))
FIELDS = (
    "revenue_from_operations", "other_income", "total_expenses", "finance_costs",
    "depreciation", "profit_before_tax", "tax_expense", "profit_after_tax",
)
PERIODS = ("current", "preceding_quarter", "corresponding_previous_year")
RELEVANCE_TERMS = ("total income", "revenue from operations", "profit before tax", "finance costs", "depreciation", "statement of profit", "statement of income", "total expenses")


class ResultExtractionError(RuntimeError):
    pass


class CitationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    field: str
    period_role: Literal["current", "preceding_quarter", "corresponding_previous_year"]
    page: int = Field(ge=1)
    quote: str = Field(min_length=1)


class ExtractedPeriod(BaseModel):
    model_config = ConfigDict(extra="forbid")
    period_label: str = Field(min_length=1)
    unit_as_printed: str = Field(min_length=1)
    values: dict[str, float | str | None]
    ebitda: float | str | None = None


class Extraction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reporting_basis: Literal["consolidated", "standalone"]
    periods: dict[Literal["current", "preceding_quarter", "corresponding_previous_year"], ExtractedPeriod]
    citations: list[CitationInput]
    confidence: float = Field(ge=0, le=1)


class Observations(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lines: list[str] = Field(min_length=2, max_length=2)


def unit_factor(unit: str) -> float:
    normalized = unit.lower().replace("₹", "inr").replace("rs.", "inr").replace("rupees", "inr")
    if "crore" in normalized or "crores" in normalized:
        return 1.0
    if "lakh" in normalized or "lakhs" in normalized:
        return 0.01
    if "million" in normalized or "millions" in normalized or re.search(r"\binr\s*m\b", normalized):
        return 0.1
    if "inr" in normalized or "rupee" in normalized:
        return 1 / 10_000_000
    raise ValueError(f"Unsupported or ambiguous monetary unit: {unit!r}")


def amount(value: float | str | None) -> float | None:
    if value is None or (isinstance(value, str) and value.strip().lower() in {"", "-", "—", "n/a", "null"}):
        return None
    if isinstance(value, (int, float)):
        result = float(value)
    else:
        raw = value.strip().replace(",", "").replace("₹", "")
        negative = raw.startswith("(") and raw.endswith(")")
        raw = raw.strip("() ")
        try:
            result = float(raw)
        except ValueError as exc:
            raise ValueError(f"Invalid financial value: {value!r}") from exc
        if negative:
            result = -result
    if not math.isfinite(result):
        raise ValueError("Financial values must be finite")
    return result


def percent_change(current: float | None, prior: float | None) -> float | None:
    if current is None or prior in (None, 0):
        return None
    return (current - prior) / abs(prior) * 100


def margin(value: float | None, revenue: float | None) -> float | None:
    if value is None or revenue in (None, 0):
        return None
    return value / revenue * 100


def relevant_pages(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = []
    for page in pages:
        # Include pdfplumber tables as well as PyMuPDF text: some statement pages
        # are represented primarily as table cells by one of the two parsers.
        text = (str(page.get("text", "")) + " " + json.dumps(page.get("tables", []), ensure_ascii=False)).lower()
        matched = sum(term in text for term in RELEVANCE_TERMS)
        if matched >= 2 or ("revenue from operations" in text and "profit before tax" in text):
            selected.append(page)
    return selected


def extract_pdf(path: str | Path) -> list[dict[str, Any]]:
    """Extract text and tables page-by-page; page references are one-based."""
    try:
        import fitz
        import pdfplumber
    except ImportError as exc:
        raise ResultExtractionError("PDF parsing requires PyMuPDF and pdfplumber; install backend requirements") from exc
    pages: list[dict[str, Any]] = []
    try:
        doc = fitz.open(str(path))
        with pdfplumber.open(str(path)) as table_pdf:
            for index, page in enumerate(doc):
                tables = table_pdf.pages[index].extract_tables() if index < len(table_pdf.pages) else []
                pages.append({"page": index + 1, "text": page.get_text("text"), "tables": tables})
        doc.close()
    except Exception as exc:
        raise ResultExtractionError(f"Unable to parse filing PDF: {exc}") from exc
    if not pages or not any(p["text"].strip() or p["tables"] for p in pages):
        raise ResultExtractionError("PDF contains no extractable text or tables")
    return pages


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("source_url must be an absolute HTTP(S) URL")


def download_pdf(url: str, *, cache_dir: str | Path | None = None, retries: int = 2, timeout: float = 20) -> tuple[Path, str]:
    _validate_url(url)
    directory = Path(cache_dir) if cache_dir else PDF_CACHE
    directory.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()
    target = directory / f"{key}.pdf"
    if target.exists() and target.stat().st_size > 5 and target.read_bytes()[:5] == b"%PDF-":
        return target, hashlib.sha256(target.read_bytes()).hexdigest()
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            response = httpx.get(url, timeout=timeout, follow_redirects=True, headers={"User-Agent": "FINN research client/1.0"})
            response.raise_for_status()
            content = response.content
            if not content.startswith(b"%PDF-"):
                raise ResultExtractionError("URL did not return a PDF document")
            temp = target.with_suffix(".tmp")
            temp.write_bytes(content)
            temp.replace(target)
            return target, hashlib.sha256(content).hexdigest()
        except (httpx.HTTPError, OSError, ResultExtractionError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(0.5 * (2 ** attempt), 3))
    raise ResultExtractionError(f"PDF download failed: {last_error}") from last_error


def _period_payload(extraction: Extraction, citations: dict[tuple[str, str], dict[str, Any]]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for role in PERIODS:
        p = extraction.periods.get(role)
        if p is None:
            raise ValueError(f"Missing required period: {role}")
        factor = unit_factor(p.unit_as_printed)
        metrics: dict[str, Any] = {}
        for field in FIELDS:
            raw = p.values.get(field)
            value = amount(raw)
            citation = citations.get((role, field))
            if raw is not None and citation is None:
                raise ValueError(f"Missing source citation for {role}.{field}")
            metrics[field] = {"raw_value": raw, "unit_as_printed": p.unit_as_printed,
                              "value_inr_crore": value * factor if value is not None else None,
                              "derived": False, "citation": citation}
        explicit = amount(p.ebitda)
        if explicit is not None:
            if (role, "ebitda") not in citations:
                raise ValueError(f"Missing source citation for reported {role} EBITDA")
            ebitda = {"raw_value": p.ebitda, "unit_as_printed": p.unit_as_printed,
                      "value_inr_crore": explicit * factor, "derived": False,
                      "citation": citations[(role, "ebitda")]}
        else:
            pieces = [metrics[x]["value_inr_crore"] for x in ("profit_before_tax", "finance_costs", "depreciation", "other_income")]
            calculated = pieces[0] + pieces[1] + pieces[2] - pieces[3] if all(x is not None for x in pieces) else None
            ebitda = {"raw_value": None, "unit_as_printed": p.unit_as_printed,
                      "value_inr_crore": calculated, "derived": calculated is not None,
                      "citation": [metrics[x]["citation"] for x in ("profit_before_tax", "finance_costs", "depreciation", "other_income")] if calculated is not None else None}
        metrics["ebitda"] = ebitda
        normalized[role] = {"period_label": p.period_label, "unit_as_printed": p.unit_as_printed, **metrics}
    current, preceding, previous_year = (normalized[x] for x in PERIODS)
    comparisons = {}
    for metric in ("revenue_from_operations", "ebitda", "profit_before_tax", "profit_after_tax"):
        current_val = current[metric]["value_inr_crore"]
        prior_q = preceding[metric]["value_inr_crore"]
        prior_y = previous_year[metric]["value_inr_crore"]
        comparisons[metric] = {"qoq_pct": percent_change(current_val, prior_q), "yoy_pct": percent_change(current_val, prior_y)}
    revenue = current["revenue_from_operations"]["value_inr_crore"]
    current["ebitda_margin_pct"] = margin(current["ebitda"]["value_inr_crore"], revenue)
    current["pat_margin_pct"] = margin(current["profit_after_tax"]["value_inr_crore"], revenue)
    return {"periods": normalized, "changes": comparisons}


def validate_extraction(extraction: Extraction, pages: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    by_page = {p["page"]: p for p in pages}
    page_nums = sorted(by_page)
    for citation in extraction.citations:
        page = by_page.get(citation.page)
        if not page:
            errors.append(f"Citation points to missing page {citation.page}")
        elif citation.quote.lower() not in (str(page["text"]) + " " + json.dumps(page.get("tables", []))).lower():
            errors.append(f"Citation quote is not present on page {citation.page}")
        if citation.period_role in extraction.periods:
            period = extraction.periods[citation.period_role]
            raw = period.ebitda if citation.field == "ebitda" else period.values.get(citation.field)
            if raw is not None:
                quoted = citation.quote.replace(",", "").replace(" ", "")
                printed = str(raw).replace(",", "").replace(" ", "")
                if printed.casefold() not in quoted.casefold():
                    errors.append(f"Citation for {citation.period_role}.{citation.field} does not contain the extracted value")
    try:
        by_key = {(c.period_role, c.field): c.model_dump() for c in extraction.citations}
        payload = _period_payload(extraction, by_key)
        current = payload["periods"]["current"]
        revenue = current["revenue_from_operations"]["value_inr_crore"]
        if revenue is None or revenue <= 0:
            errors.append("Current-period revenue must be printed and positive")
        pbt = current["profit_before_tax"]["value_inr_crore"]
        pat = current["profit_after_tax"]["value_inr_crore"]
        tax = current["tax_expense"]["value_inr_crore"]
        if pbt is not None and pat is not None and pat > pbt and not (tax is not None and tax < 0):
            errors.append("PAT exceeds PBT without a tax credit")
    except (ValueError, TypeError) as exc:
        errors.append(str(exc))
    labels = [extraction.periods[r].period_label for r in PERIODS if r in extraction.periods]
    if len(labels) != 3:
        errors.append("Exactly three reporting periods are required")
    # Only enforce chronology where month/year labels can be parsed unambiguously.
    if len(labels) == 3:
        current_key, preceding_key, prior_year_key = (_period_key(extraction.periods[r].period_label) for r in PERIODS)
        if all(x is not None for x in (current_key, preceding_key, prior_year_key)):
            if not (current_key > preceding_key > prior_year_key):
                errors.append("Reporting periods are not in plausible chronological order")
            if current_key - preceding_key not in (1, 2, 3):
                errors.append("Preceding quarter label is not within three months of the current quarter")
            if current_key - prior_year_key != 12:
                errors.append("Corresponding previous-year quarter is not twelve months before the current quarter")
    if not page_nums:
        errors.append("No source pages available for validation")
    return errors


def _period_key(label: str) -> int | None:
    months = {m.lower(): i for i, m in enumerate(("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"), 1)}
    match = re.search(r"(\d{1,2})\s+([A-Za-z]+)[, ]+((?:19|20)\d{2})", label)
    if not match:
        return None
    month = months.get(match.group(2).lower())
    return int(match.group(3)) * 12 + month if month else None


def _page_payload(pages: list[dict[str, Any]]) -> str:
    relevant = relevant_pages(pages)
    if not relevant:
        raise ResultExtractionError("No statement of profit and loss pages were identified")
    return json.dumps(relevant, ensure_ascii=False)


async def _call_model(model_call: Callable[..., Any], *, tier: str, user: str, schema: Any, db_path: str | None):
    return await model_call(system=PROMPT_PATH.read_text(encoding="utf-8"), user=user, schema=schema, tier=tier, temperature=0.0, db_path=db_path)


def _persist(ticker: str, filing_id: str, payload: dict[str, Any], content_hash: str, model_name: str, db_path: str | None) -> None:
    with connect(db_path) as conn:
        row = conn.execute("SELECT id FROM filings WHERE id=?", (filing_id,)).fetchone()
        if not row:
            raise ResultExtractionError("Filing record was not found; cannot persist results card")
        conn.execute("""INSERT OR REPLACE INTO extractions
            (id,ticker,document_id,module,extraction_key,value_json,citations_json,model,content_hash)
            VALUES(?,?,NULL,'results_card',?,?,?, ?,?)""",
            (hashlib.sha256(f"{filing_id}:{content_hash}".encode()).hexdigest(), ticker, filing_id,
             json.dumps(payload, ensure_ascii=False), json.dumps(payload.get("citations", []), ensure_ascii=False), model_name, content_hash))


def get_cached_card(filing_id: str, *, db_path: str | None = None) -> dict[str, Any] | None:
    with connect(db_path) as conn:
        row = conn.execute("SELECT value_json FROM extractions WHERE module='results_card' AND extraction_key=? ORDER BY created_at DESC LIMIT 1", (filing_id,)).fetchone()
    return json.loads(row["value_json"]) if row else None


def list_results_filings(*, ticker: str | None = None, limit: int = 100, db_path: str | None = None) -> list[dict[str, Any]]:
    """List persisted results filings for the research UI, newest first."""
    params: list[Any] = []
    where = "lower(f.category) LIKE '%result%' AND f.attachment_url IS NOT NULL AND f.attachment_url != ''"
    if ticker:
        where += " AND f.ticker=?"
        params.append(ticker.strip().upper())
    params.append(limit)
    with connect(db_path) as conn:
        rows = conn.execute(f"""SELECT f.id AS filing_id,f.ticker,c.name AS company_name,f.headline,
            f.filed_at,f.attachment_url,f.raw_url,f.source,
            e.extraction_key IS NOT NULL AS card_available
            FROM filings f JOIN companies c ON c.ticker=f.ticker
            LEFT JOIN (SELECT DISTINCT extraction_key FROM extractions WHERE module='results_card') e
              ON e.extraction_key=f.id
            WHERE {where} ORDER BY f.filed_at DESC LIMIT ?""", params).fetchall()
    return [dict(row) for row in rows]


async def generate_results_card(*, ticker: str, company_name: str, filing_id: str, source_url: str,
                                cache_dir: str | Path | None = None, db_path: str | None = None,
                                model_call: Callable[..., Any] = generate_json, demo_mode: bool = False,
                                source_type: Literal["live", "fixture"] = "live") -> dict[str, Any]:
    """Download, extract, validate once with strong tier, calculate, and persist a card."""
    result: dict[str, Any] = {"ticker": ticker.upper(), "company_name": company_name, "filing_id": filing_id,
        "source_url": source_url, "reporting_basis": None, "periods": {}, "changes": {}, "extraction_confidence": None,
        "source_citations": [], "what_stands_out": None, "parse_failed": False, "validation_errors": [],
        "demo_mode": demo_mode, "source_type": source_type, "as_of": datetime.now(timezone.utc).isoformat()}
    try:
        pdf_path, digest = download_pdf(source_url, cache_dir=cache_dir)
        pages = extract_pdf(pdf_path)
        page_data = _page_payload(pages)
        prompt = f"Source URL: {source_url}\nTicker: {ticker}\nCompany: {company_name}\nRelevant source pages and tables (JSON):\n{page_data}"
        extraction: Extraction | None = None
        errors: list[str] = []
        for tier in ("small", "strong"):
            try:
                raw = await _call_model(model_call, tier=tier, user=prompt + ("\nFix these validation issues: " + "; ".join(errors) if errors else ""), schema=Extraction, db_path=db_path)
                extraction = Extraction.model_validate(raw)
                errors = validate_extraction(extraction, pages)
                if not errors:
                    break
            except Exception as exc:
                errors = [str(exc)]
            if tier == "strong":
                break
        if extraction is None or errors:
            result["parse_failed"] = True
            result["validation_errors"] = errors or ["No valid extraction returned"]
            return result
        citations = {(c.period_role, c.field): c.model_dump() for c in extraction.citations}
        calc = _period_payload(extraction, citations)
        current = calc["periods"]["current"]
        if current["ebitda"]["value_inr_crore"] is not None:
            current["ebitda_margin_pct"] = margin(current["ebitda"]["value_inr_crore"], current["revenue_from_operations"]["value_inr_crore"])
        result.update({"reporting_basis": extraction.reporting_basis, **calc,
            "extraction_confidence": extraction.confidence, "source_citations": [c.model_dump() for c in extraction.citations],
            "validation_errors": [], "content_hash": digest})
        try:
            observation = await _call_model(model_call, tier="small", user="Write exactly two concise observation lines based only on these computed figures. Do not add external facts.\n" + json.dumps(calc, ensure_ascii=False), schema=Observations, db_path=db_path)
            result["what_stands_out"] = Observations.model_validate(observation).lines
        except Exception:
            result["what_stands_out"] = None
        _persist(ticker.upper(), filing_id, result, digest, model_config("small").name, db_path)
        return result
    except Exception as exc:
        result["parse_failed"] = True
        result["validation_errors"] = [str(exc)]
        return result


async def get_or_generate_results_card(filing_id: str, *, db_path: str | None = None, demo_mode: bool = False) -> dict[str, Any] | None:
    cached = get_cached_card(filing_id, db_path=db_path)
    if cached:
        return cached
    with connect(db_path) as conn:
        row = conn.execute("""SELECT f.id,f.ticker,f.category,f.headline,f.attachment_url,f.raw_url,f.source,c.name
            FROM filings f JOIN companies c ON c.ticker=f.ticker WHERE f.id=?""", (filing_id,)).fetchone()
    if not row:
        return None
    if "result" not in (row["category"] or "").lower():
        raise ResultExtractionError("Filing does not have a results attachment")
    url = row["attachment_url"] or row["raw_url"]
    is_fixture = row["source"] == "fixture"
    return await generate_results_card(ticker=row["ticker"], company_name=row["name"], filing_id=row["id"], source_url=url,
                                       db_path=db_path, demo_mode=is_fixture, source_type="fixture" if is_fixture else "live")
