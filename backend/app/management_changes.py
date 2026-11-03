"""Structured management-change events derived from stored announcements."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime
from typing import Any

from .db import connect, init_db

_NAME = re.compile(r"\b(?:Mr\.?|Ms\.?|Mrs\.?|Dr\.?|Shri|Smt\.?)\s+[A-Z][A-Za-z.'-]*(?:\s+[A-Z][A-Za-z.'-]+){0,3}")
_DATE_PATTERNS = (
    re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"),
    re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b"),
    re.compile(r"\b(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})\b"),
)

def _date(text: str) -> str | None:
    for pattern in _DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        value = match.group(1)
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d %B %Y", "%d %b %Y"):
            try:
                return datetime.strptime(value, fmt).date().isoformat()
            except ValueError:
                pass
    return None

def _extract(announcement: dict[str, Any]) -> dict[str, Any]:
    headline = str(announcement.get("headline") or "")
    metadata = announcement.get("raw_metadata") or {}
    # Only use human-readable source fields; raw metadata remains the source of truth.
    text = " ".join([headline] + [str(metadata[k]) for k in ("details", "desc", "subject", "purpose", "remarks", "reason") if metadata.get(k)])
    low = text.lower()
    if re.search(r"\bre-?appoint(?:ed|ment|s)?\b", low):
        change = "reappointment"
    elif re.search(r"\b(resign(?:s|ed|ation)?|steps? down|stepped down|relinquish(?:es|ed)?)\b", low):
        change = "resignation"
    elif re.search(r"\b(retir(?:e|es|ed|ement))\b", low):
        change = "retirement"
    elif re.search(r"\b(appoint(?:s|ed|ment)?|joins? as|named as)\b", low):
        change = "appointment"
    elif re.search(r"\b(cessation|ceases? to be|vacates?)\b", low):
        change = "cessation"
    elif re.search(r"\b(transition|designated as|redesignated)\b", low):
        change = "role_change"
    else:
        change = "unknown"

    if re.search(r"\b(chief executive|\bceo\b|managing director|\bmd\b)\b", low):
        role = "md_ceo"
    elif re.search(r"\b(chief financial|\bcfo\b)\b", low):
        role = "cfo"
    elif re.search(r"\b(chairman|chairperson)\b", low):
        role = "chairman"
    elif re.search(r"\bindependent director\b", low):
        role = "independent_director"
    elif re.search(r"\b(board|director)\b", low):
        role = "director"
    elif re.search(r"\b(key managerial|company secretary|chief operating|\bcoo\b|whole.time director)\b", low):
        role = "other_kmp"
    else:
        role = "other"

    names = list(dict.fromkeys(m.group(0).strip() for m in _NAME.finditer(text)))
    person = names[0] if len(names) == 1 else None
    date_value = _date(text)
    reason_match = re.search(r"\b(?:due to|owing to|on account of|reason(?:s)? (?:is|are))\s+([^.;,]+)", text, re.I)
    reason = reason_match.group(1).strip() if reason_match else None
    designation_match = re.search(
        r"\b(?:Managing Director|Chief Executive Officer|CEO|MD|Chief Financial Officer|CFO|"
        r"Chief Operating Officer|COO|Independent Director|Non-Executive Director|Executive Director|"
        r"Whole-Time Director|Chairman|Chairperson|Company Secretary|Director|Key Managerial Personnel)\b",
        text, re.I,
    )
    designation = designation_match.group(0) if designation_match else None
    transition = re.search(r"\bfrom\s+(.{2,60}?)\s+to\s+(.{2,60}?)(?:\s+(?:with effect|effective|on)\b|[.;,]|$)", text, re.I)
    previous_designation = transition.group(1).strip() if transition else None
    new_designation = transition.group(2).strip() if transition else (designation if change in ("appointment", "reappointment", "role_change") else None)
    if len(names) > 1 or (change == "unknown" and not person):
        status = "ambiguous"
    elif not person or change == "unknown":
        status = "incomplete"
    else:
        status = "complete"
    score = float(announcement.get("materiality_score") or 0)
    floors = {"md_ceo": 8, "chairman": 7, "cfo": 7, "other_kmp": 6, "independent_director": 5, "director": 5}
    score = min(10.0, max(0.0, score, floors.get(role, 0)))
    verb = {"appointment": "appointed", "resignation": "resigned", "retirement": "retired", "reappointment": "reappointed", "cessation": "ceased", "role_change": "changed role", "unknown": "management change reported"}[change]
    subject = person or "The filing does not identify a person's name in the available text"
    role_text = designation or role.replace("_", " ")
    explanation = f"{subject}: {verb} as {role_text}."
    if date_value:
        explanation += f" Effective {date_value}."
    if reason:
        explanation += f" Disclosed reason: {reason}."
    return {"person_name": person, "role_category": role, "previous_designation": previous_designation,
            "new_designation": new_designation, "change_type": change, "effective_date": date_value,
            "reason": reason, "materiality_score": score, "explanation": explanation,
            "extraction_status": status}

def process_management_changes(*, ticker: str | None = None, limit: int = 200, db_path: str | None = None) -> dict[str, int]:
    """Process existing management-change announcements idempotently; no refetching."""
    init_db(db_path)
    clauses = ["a.classification='management_change'"]
    params: list[Any] = []
    if ticker:
        clauses.append("a.ticker=?")
        params.append(ticker.strip().upper())
    params.append(max(1, min(limit, 500)))
    with connect(db_path) as conn:
        rows = conn.execute(f"SELECT a.*,c.name company_name FROM announcements a JOIN companies c ON c.ticker=a.ticker WHERE {' AND '.join(clauses)} ORDER BY a.timestamp DESC LIMIT ?", params).fetchall()
        inserted = 0
        for row in rows:
            announcement = dict(row)
            if conn.execute("SELECT 1 FROM management_change_events WHERE announcement_id=?", (announcement["id"],)).fetchone():
                continue
            try:
                announcement["raw_metadata"] = json.loads(announcement.get("raw_metadata_json") or "{}")
            except json.JSONDecodeError:
                announcement["raw_metadata"] = {}
            event = _extract(announcement)
            event_id = hashlib.sha256(announcement["id"].encode()).hexdigest()
            conn.execute("""INSERT OR IGNORE INTO management_change_events
                (id,announcement_id,ticker,company_name,person_name,role_category,previous_designation,new_designation,
                 change_type,effective_date,reason,announced_at,filing_reference,attachment_url,materiality_score,
                 explanation,extraction_status,source)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (event_id, announcement["id"], announcement["ticker"], announcement["company_name"],
                 event["person_name"], event["role_category"], event["previous_designation"], event["new_designation"],
                 event["change_type"], event["effective_date"], event["reason"], announcement["timestamp"],
                 announcement.get("source_identifier"), announcement.get("attachment_url"), event["materiality_score"],
                 event["explanation"], event["extraction_status"], announcement["source"]))
            inserted += conn.execute("SELECT changes()").fetchone()[0]
        return {"scanned": len(rows), "inserted": inserted}

def list_management_changes(*, ticker: str | None = None, change_type: str | None = None,
                            min_materiality: float | None = None, limit: int = 100,
                            offset: int = 0, db_path: str | None = None,
                            exclude_demo: bool = False) -> list[dict[str, Any]]:
    clauses, params = [], []
    if ticker:
        clauses.append("e.ticker=?"); params.append(ticker.strip().upper())
    if change_type:
        clauses.append("e.change_type=?"); params.append(change_type)
    if min_materiality is not None:
        clauses.append("e.materiality_score>=?"); params.append(min_materiality)
    if exclude_demo:
        clauses.append("(COALESCE(a.demo_data, 0)=0 AND a.source != 'fixture')")
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    with connect(db_path) as conn:
        rows = conn.execute(f"SELECT e.*,a.headline FROM management_change_events e JOIN announcements a ON a.id=e.announcement_id{where} ORDER BY announced_at DESC,e.id LIMIT ? OFFSET ?", (*params, limit, offset)).fetchall()
    return [dict(row) for row in rows]
