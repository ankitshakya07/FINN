"""Deterministic ranking and grouping for the existing FINN intelligence sources."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping


CATEGORY_SIGNIFICANCE = {
    "results": 9, "M&A": 9, "fund_raise": 8, "management_change": 8,
    "litigation": 8, "credit_rating": 7, "capex": 7, "pledging": 7,
    "dividend": 6, "bonus_split": 5, "insider_trading": 5,
    "price_volume_anomaly": 7, "price_anomaly": 6, "volume_anomaly": 6,
    "results_card": 9, "earnings_call": 4, "investor_meetings": 3,
    "agm_egm": 2, "postal_ballot": 2, "press_release": 2,
    "unclassified": 1,
}
ROUTINE_CATEGORIES = {"press_release", "postal_ballot", "agm_egm", "unclassified"}


def parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def _stable_id(prefix: str, *parts: str) -> str:
    return f"{prefix}:{hashlib.sha256('|'.join(parts).encode()).hexdigest()[:24]}"


def rank_event(item: dict[str, Any], *, as_of: datetime, portfolio_tickers: set[str] | None = None) -> dict[str, Any]:
    """Attach a transparent, reproducible rank score without changing source materiality."""
    category = str(item.get("category") or "unclassified")
    significance = CATEGORY_SIGNIFICANCE.get(category, 1)
    reasons: list[str] = [f"Category significance {significance}/9"]
    materiality = item.get("materiality_score")
    score = 0.0
    if materiality is not None:
        materiality = max(0.0, min(10.0, float(materiality)))
        item["materiality_score"] = materiality
        score += materiality * 10
        reasons.insert(0, f"Source materiality {materiality:g}/10")
    score += significance * 5
    if portfolio_tickers and item.get("ticker") in portfolio_tickers:
        score += 15
        reasons.append("Company is marked in the portfolio")
    event_time = parse_timestamp(item.get("occurred_at"))
    if event_time:
        age_days = max(0.0, (as_of - event_time).total_seconds() / 86400)
        recency = round(max(0.0, 10.0 - min(age_days, 90.0) / 9.0), 2)
        score += recency
        reasons.append(f"Recency {recency:g}/10")
    if item.get("source_reference") or item.get("attachment_url"):
        score += 2
        reasons.append("Source reference available")
    if item.get("supporting_details"):
        score += 1
        reasons.append("Supporting details available")
    item["rank_score"] = round(score, 2)
    item["rank_reasons"] = reasons
    if item.get("priority") not in ("high", "medium", "low"):
        item["priority"] = "high" if (materiality is not None and materiality >= 7) or significance >= 7 else "medium" if significance >= 4 else "low"
    return item


def build_source_items(
    *, announcements: Iterable[Mapping[str, Any]], anomalies: Iterable[Mapping[str, Any]],
    management_events: Iterable[Mapping[str, Any]], results_cards: Iterable[Mapping[str, Any]],
    enriched_filings: Iterable[Mapping[str, Any]], company_names: Mapping[str, str],
    portfolio_tickers: set[str], as_of: datetime,
) -> list[dict[str, Any]]:
    """Convert existing module records to a common brief item, preserving provenance."""
    management_by_announcement = {str(e["announcement_id"]): dict(e) for e in management_events}
    items: list[dict[str, Any]] = []
    by_source_ref: dict[tuple[str, str], dict[str, Any]] = {}

    for row in announcements:
        a = dict(row)
        source_time = a.get("timestamp") or a.get("occurred_at")
        event_time = parse_timestamp(source_time)
        if not event_time:
            continue
        raw = a.get("raw_metadata") or {}
        management = management_by_announcement.get(str(a["id"]))
        category = str(a.get("classification") or "unclassified")
        source_ref = a.get("source_identifier") or a.get("attachment_url")
        details: dict[str, Any] = {"raw_category": a.get("raw_category"), "materiality_reason": a.get("materiality_reason")}
        if management:
            details["management_change"] = {
                "person_name": management.get("person_name"), "role_category": management.get("role_category"),
                "change_type": management.get("change_type"), "effective_date": management.get("effective_date"),
                "extraction_status": management.get("extraction_status"),
            }
        item = {
            "id": f"announcement:{a['id']}", "ticker": a["ticker"],
            "company_name": a.get("company_name") or company_names.get(a["ticker"], "Company name unavailable"),
            "kind": "filing", "category": category,
            "headline": str(a.get("headline") or "Announcement headline unavailable"),
            "materiality_score": a.get("materiality_score"), "occurred_at": event_time,
            "summary": (management.get("explanation") if management else None) or a.get("summary") or a.get("materiality_reason") or "No additional explanation was stored with this announcement.",
            "source_reference": source_ref, "attachment_url": a.get("attachment_url"),
            "data_source": str(a.get("source") or "unknown"),
            "source": str(a.get("source") or "unknown"),
            "fetched_at": parse_timestamp(a.get("created_at") or a.get("fetched_at")),
            "demo_mode": bool(
                a.get("source") == "fixture" or raw.get("demo_data") is True or "fixture" in raw.get("duplicate_sources", [])
            ), "citations": [{"document": str(source_ref or a.get("headline") or "Announcement"),
                              "locator": str(source_time), "quote": str(a.get("headline") or "")}],
            "supporting_details": details, "priority": None, "collapsed_count": 1,
        }
        items.append(item)
        for candidate in (a.get("source_identifier"), a.get("attachment_url")):
            if candidate:
                by_source_ref[(str(a["ticker"]), str(candidate))] = item

    # The two anomaly rows from one ticker/session describe one underlying move.
    anomaly_groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in anomalies:
        anomaly = dict(row)
        stamp = parse_timestamp(anomaly.get("detected_at"))
        if not stamp:
            continue
        anomaly_groups.setdefault((str(anomaly["ticker"]), stamp.date().isoformat()), []).append(anomaly)
    for (ticker, session), group in anomaly_groups.items():
        group.sort(key=lambda value: str(value.get("anomaly_type")))
        kinds = {str(x.get("anomaly_type")) for x in group}
        category = "price_volume_anomaly" if len(kinds) > 1 else "volume_anomaly" if "volume_spike" in kinds else "price_anomaly"
        stamp = parse_timestamp(group[0].get("detected_at"))
        explanations = list(dict.fromkeys(str(x.get("explanation")) for x in group if x.get("explanation")))
        details = [{"type": x.get("anomaly_type"), "observed_value": x.get("observed_value"),
                    "threshold_value": x.get("threshold_value"), "unit": x.get("unit")} for x in group]
        items.append({
            "id": _stable_id("anomaly", ticker, session), "ticker": ticker,
            "company_name": company_names.get(ticker, "Company name unavailable"), "kind": "anomaly", "category": category,
            "headline": "Price and volume moved beyond the configured thresholds" if len(kinds) > 1 else "Trading anomaly detected",
            "materiality_score": None, "occurred_at": stamp,
            "summary": "; ".join(explanations) or "Anomaly calculation details are unavailable.",
            "source_reference": f"prices:{session}", "attachment_url": None,
            "data_source": str(group[0].get("data_source") or "price history"),
            "source": str(group[0].get("data_source") or "yfinance"),
            "fetched_at": stamp,
            "demo_mode": any(bool(x.get("demo_mode")) for x in group), "citations": [],
            "supporting_details": {"anomalies": details}, "priority": None, "collapsed_count": 1,
        })

    for row in results_cards:
        result = dict(row)
        card = result.get("card") or {}
        if not card or card.get("parse_failed"):
            continue
        ticker = str(result["ticker"])
        source_ref = card.get("source_url") or result.get("attachment_url") or result.get("raw_url")
        related = by_source_ref.get((ticker, str(source_ref))) if source_ref else None
        observation = card.get("what_stands_out")
        if isinstance(observation, list):
            observation = " ".join(str(line) for line in observation)
        if related:
            related["supporting_details"]["results_card"] = {
                "filing_id": result.get("filing_id"), "reporting_basis": card.get("reporting_basis"),
                "source_url": source_ref, "what_stands_out": observation,
            }
            if observation:
                related["summary"] = str(observation)
            continue
        stamp = parse_timestamp(result.get("filed_at") or result.get("created_at") or card.get("as_of"))
        if not stamp:
            continue
        items.append({
            "id": f"results:{result.get('filing_id')}", "ticker": ticker,
            "company_name": result.get("company_name") or company_names.get(ticker, "Company name unavailable"),
            "kind": "results", "category": "results", "headline": result.get("headline") or "Quarterly results card available",
            "materiality_score": None, "occurred_at": stamp,
            "summary": str(observation or "A results card is available; its observation is not available."),
            "source_reference": source_ref, "attachment_url": source_ref,
            "data_source": str(result.get("source") or "results card"),
            "demo_mode": result.get("source") == "fixture" or bool(card.get("demo_mode")),
            "citations": card.get("source_citations") or [],
            "supporting_details": {"reporting_basis": card.get("reporting_basis"),
                                   "periods": card.get("periods"), "source_citations": card.get("source_citations", [])},
            "priority": None, "collapsed_count": 1,
        })

    # Include already-enriched material filings only when no announcement has the same source/headline.
    seen_headlines = {(x["ticker"], _norm(x["headline"])) for x in items}
    for row in enriched_filings:
        filing = dict(row)
        ticker = str(filing.get("ticker") or "")
        headline = str(filing.get("headline") or "")
        if not ticker or not headline or (ticker, _norm(headline)) in seen_headlines:
            continue
        stamp = parse_timestamp(filing.get("filed_at"))
        if not stamp:
            continue
        try:
            key_points = json.loads(filing.get("key_points_json") or "[]")
            citations = json.loads(filing.get("citations_json") or "[]")
        except (TypeError, json.JSONDecodeError):
            key_points, citations = [], []
        items.append({
            "id": f"filing:{filing['id']}", "ticker": ticker,
            "company_name": filing.get("company_name") or company_names.get(ticker, "Company name unavailable"),
            "kind": "filing", "category": str(filing.get("category") or "unclassified"),
            "headline": headline, "materiality_score": None, "occurred_at": stamp,
            "summary": filing.get("summary") or "Filing summary unavailable.",
            "source_reference": filing.get("filing_ref") or filing.get("raw_url"),
            "attachment_url": filing.get("attachment_url") or filing.get("raw_url"),
            "data_source": str(filing.get("source") or "filing enrichment"),
            "demo_mode": filing.get("source") == "fixture", "citations": citations,
            "supporting_details": {"key_points": key_points, "citations": citations},
            "priority": filing.get("priority"), "collapsed_count": 1,
        })
        seen_headlines.add((ticker, _norm(headline)))

    # Remove exact cross-source duplicates while keeping the best-supported representation.
    unique: dict[tuple[str, str, str], dict[str, Any]] = {}
    duplicates_collapsed = 0
    for item in items:
        key = (item["ticker"], item["category"], _norm(item["headline"]))
        previous = unique.get(key)
        if previous is None:
            unique[key] = item
            continue
        duplicates_collapsed += 1
        previous["demo_mode"] = bool(previous["demo_mode"] or item["demo_mode"])
        refs = list(dict.fromkeys([previous.get("source_reference"), item.get("source_reference")]))
        sources = list(dict.fromkeys([previous.get("data_source"), item.get("data_source")]))
        if len(sources) > 1:
            previous["data_source"] = "mixed"
        previous["supporting_details"].setdefault("duplicate_sources", [x for x in refs if x])
        previous["supporting_details"]["duplicate_count"] = previous.get("supporting_details", {}).get("duplicate_count", 1) + 1
        if item.get("materiality_score") is not None and (previous.get("materiality_score") is None or item["materiality_score"] > previous["materiality_score"]):
            previous["materiality_score"] = item["materiality_score"]
        if item.get("attachment_url") and not previous.get("attachment_url"):
            previous["attachment_url"] = item["attachment_url"]
            previous["source_reference"] = item.get("source_reference")
    unique_items = list(unique.values())

    # Collapse multiple low-materiality routine notices into one company/category card.
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    remaining = []
    for item in unique_items:
        score = item.get("materiality_score")
        if item["category"] in ROUTINE_CATEGORIES and score is not None and float(score) <= 2:
            groups.setdefault((item["ticker"], item["category"]), []).append(item)
        else:
            remaining.append(item)
    collapsed = duplicates_collapsed
    for (ticker, category), group in groups.items():
        if len(group) < 2:
            remaining.extend(group)
            continue
        latest = max(group, key=lambda x: x["occurred_at"])
        source_ids = sorted(x["id"] for x in group)
        base = dict(latest)
        base.update({
            "id": _stable_id("routine", ticker, category, *source_ids),
            "headline": f"{len(group)} routine {category.replace('_', ' ')} disclosures",
            "summary": f"{len(group)} lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
            "materiality_score": max(float(x["materiality_score"]) for x in group),
            "source_reference": None, "attachment_url": None,
            "data_source": "mixed" if len({x["data_source"] for x in group}) > 1 else latest["data_source"],
            "demo_mode": any(x["demo_mode"] for x in group),
            "citations": [citation for x in group for citation in x.get("citations", [])],
            "supporting_details": {"grouped_events": [
                {"id": x["id"], "headline": x["headline"], "occurred_at": x["occurred_at"],
                 "source_reference": x.get("source_reference"), "attachment_url": x.get("attachment_url")}
                for x in sorted(group, key=lambda x: x["occurred_at"], reverse=True)
            ]}, "collapsed_count": len(group),
        })
        remaining.append(base)
        collapsed += len(group) - 1

    for item in remaining:
        rank_event(item, as_of=as_of, portfolio_tickers=portfolio_tickers)
    return remaining, collapsed


def select_digest_items(
    items: Iterable[dict[str, Any]], *, start: datetime, end: datetime,
    ticker: str | None = None, category: str | None = None,
    min_materiality: float | None = None, sort: str = "relevance",
    limit: int = 50, offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    selected = []
    for item in items:
        stamp = parse_timestamp(item.get("occurred_at"))
        if not stamp or stamp < start or stamp > end:
            continue
        if ticker and item.get("ticker", "").upper() != ticker.upper():
            continue
        if category and item.get("category") != category:
            continue
        if min_materiality is not None and (item.get("materiality_score") is None or float(item["materiality_score"]) < min_materiality):
            continue
        selected.append(item)
    if sort == "recency":
        selected.sort(key=lambda x: (parse_timestamp(x["occurred_at"]), x.get("rank_score", 0), x["id"]), reverse=True)
    else:
        selected.sort(key=lambda x: (x.get("rank_score", 0), parse_timestamp(x["occurred_at"]), x["id"]), reverse=True)
    return selected[offset:offset + limit], len(selected)
