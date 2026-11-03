from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .db import connect

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parents[1]
FIXTURE_PATH = ROOT_DIR / "data" / "fixtures" / "commitments.json"
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def calculate_track_record(commitments: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate executive delivery rate and credibility breakdown."""
    total = len(commitments)
    beat = sum(1 for c in commitments if c.get("status") == "beat")
    met = sum(1 for c in commitments if c.get("status") == "met")
    missed = sum(1 for c in commitments if c.get("status") == "missed")
    in_progress = sum(1 for c in commitments if c.get("status") in ("in_progress", "delayed"))

    delivered = beat + met
    evaluated = delivered + missed
    delivery_score_pct = round((delivered / evaluated) * 100.0, 1) if evaluated > 0 else (100.0 if total > 0 else 0.0)

    by_category: dict[str, dict[str, Any]] = {}
    for c in commitments:
        cat = c.get("category", "operational")
        cat_stat = by_category.setdefault(
            cat, {"total": 0, "beat": 0, "met": 0, "missed": 0, "in_progress": 0, "delivery_score_pct": 0.0}
        )
        cat_stat["total"] += 1
        st = c.get("status")
        if st in ("beat", "met", "missed", "in_progress", "delayed"):
            if st == "delayed":
                st = "in_progress"
            cat_stat[st] += 1

    for cat, cat_stat in by_category.items():
        cat_delivered = cat_stat["beat"] + cat_stat["met"]
        cat_eval = cat_delivered + cat_stat["missed"]
        cat_stat["delivery_score_pct"] = (
            round((cat_delivered / cat_eval) * 100.0, 1) if cat_eval > 0 else (100.0 if cat_stat["total"] > 0 else 0.0)
        )

    return {
        "total_commitments": total,
        "delivered_count": delivered,
        "beat_count": beat,
        "met_count": met,
        "missed_count": missed,
        "in_progress_count": in_progress,
        "delivery_score_pct": delivery_score_pct,
        "category_breakdown": by_category,
    }


def save_commitments(commitments: list[dict[str, Any]], db_path: str | None = None) -> int:
    """Insert or update corporate commitments with duplicate prevention."""
    inserted = 0
    with connect(db_path) as conn:
        for c in commitments:
            ticker = c["ticker"].strip().upper()
            c_id = c.get("id") or f"promise:{ticker}:{c['category']}:{c['promised_at'][:10]}"

            conn.execute(
                "INSERT OR IGNORE INTO companies(ticker, name) VALUES (?, ?)",
                (ticker, c.get("company_name", ticker)),
            )

            conn.execute(
                """INSERT INTO company_commitments (
                    id, ticker, category, promise_headline, promised_by,
                    promised_at, promised_period, promised_document, promised_quote, promised_locator,
                    target_metric, target_date, status, delivered_at, delivered_document,
                    delivered_quote, delivered_locator, delivered_metric, variance_pct,
                    delivery_assessment, management_explanation, source, source_url, demo_mode, updated_at
                ) VALUES (
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
                ) ON CONFLICT(ticker, promise_headline, promised_at) DO UPDATE SET
                    category=excluded.category,
                    promised_by=excluded.promised_by,
                    promised_period=excluded.promised_period,
                    promised_document=excluded.promised_document,
                    promised_quote=excluded.promised_quote,
                    promised_locator=excluded.promised_locator,
                    target_metric=excluded.target_metric,
                    target_date=excluded.target_date,
                    status=excluded.status,
                    delivered_at=excluded.delivered_at,
                    delivered_document=excluded.delivered_document,
                    delivered_quote=excluded.delivered_quote,
                    delivered_locator=excluded.delivered_locator,
                    delivered_metric=excluded.delivered_metric,
                    variance_pct=excluded.variance_pct,
                    delivery_assessment=excluded.delivery_assessment,
                    management_explanation=excluded.management_explanation,
                    source=excluded.source,
                    source_url=excluded.source_url,
                    demo_mode=excluded.demo_mode,
                    updated_at=CURRENT_TIMESTAMP""",
                (
                    c_id, ticker, c["category"], c["promise_headline"], c.get("promised_by"),
                    c["promised_at"], c.get("promised_period", ""), c.get("promised_document", ""),
                    c.get("promised_quote", ""), c.get("promised_locator"), c.get("target_metric"),
                    c.get("target_date"), c.get("status", "in_progress"), c.get("delivered_at"),
                    c.get("delivered_document"), c.get("delivered_quote"), c.get("delivered_locator"),
                    c.get("delivered_metric"), c.get("variance_pct"), c.get("delivery_assessment", ""),
                    c.get("management_explanation"), c.get("source", "primary_filing"), c.get("source_url"),
                    1 if c.get("demo_mode", True) else 0,
                ),
            )
            inserted += 1
        conn.commit()
    return inserted


def load_commitments_fixture(db_path: str | None = None) -> int:
    """Load commitments fixture into SQLite if fixture exists."""
    if not FIXTURE_PATH.exists():
        return 0
    try:
        data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        commitments = data.get("commitments", [])
        return save_commitments(commitments, db_path=db_path)
    except (OSError, json.JSONDecodeError):
        return 0


def get_company_commitments(
    ticker: str,
    category: str | None = None,
    status: str | None = None,
    db_path: str | None = None,
) -> dict[str, Any] | None:
    """Return commitments and management track record for a ticker."""
    ticker_clean = ticker.strip().upper()

    with connect(db_path) as conn:
        company = conn.execute(
            "SELECT name FROM companies WHERE ticker = ?",
            (ticker_clean,),
        ).fetchone()

        query = "SELECT * FROM company_commitments WHERE ticker = ?"
        params: list[Any] = [ticker_clean]

        if category:
            query += " AND category = ?"
            params.append(category)
        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY promised_at DESC"
        rows = conn.execute(query, params).fetchall()

        if not rows:
            # Try loading fixture if database is fresh
            load_commitments_fixture(db_path)
            rows = conn.execute(query, params).fetchall()
            if not company:
                company = conn.execute(
                    "SELECT name FROM companies WHERE ticker = ?",
                    (ticker_clean,),
                ).fetchone()

    if not rows and not company:
        return None

    company_name = company["name"] if company else ticker_clean
    commitments = [dict(r) for r in rows]
    track_record = calculate_track_record(commitments)

    return {
        "ticker": ticker_clean,
        "company_name": company_name,
        "track_record": track_record,
        "count": len(commitments),
        "commitments": commitments,
        "as_of": now_utc(),
        "demo_mode": DEMO_MODE or all(c.get("demo_mode", 1) == 1 for c in commitments),
    }


def get_commitment_summary(ticker: str, db_path: str | None = None) -> dict[str, Any] | None:
    """Return concise credibility scorecard for a company."""
    data = get_company_commitments(ticker=ticker, db_path=db_path)
    if not data:
        return None
    return {
        "ticker": data["ticker"],
        "company_name": data["company_name"],
        "delivery_score_pct": data["track_record"]["delivery_score_pct"],
        "total_commitments": data["track_record"]["total_commitments"],
        "beat_count": data["track_record"]["beat_count"],
        "met_count": data["track_record"]["met_count"],
        "missed_count": data["track_record"]["missed_count"],
        "in_progress_count": data["track_record"]["in_progress_count"],
        "as_of": data["as_of"],
        "demo_mode": data["demo_mode"],
    }
