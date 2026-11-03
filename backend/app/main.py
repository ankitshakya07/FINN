from __future__ import annotations

import asyncio
import json
import logging
import os
import sqlite3
from collections import defaultdict
from datetime import date, datetime, time as day_time, timedelta, timezone
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .db import connect, init_db
from .announcements import (
    announcement_demo_mode,
    announcement_snapshot_as_of,
    ingest_announcements,
    list_announcements,
    load_demo_announcements_fixture,
)
from .prices import price_data_source, refresh_anomalies, refresh_prices
from .results_card import ResultExtractionError, get_or_generate_results_card, list_results_filings
from .management_changes import list_management_changes, process_management_changes
from .digest import build_source_items, parse_timestamp, rank_event, select_digest_items
from .fundamentals import (
    get_fundamentals,
    get_fundamentals_history,
    get_fundamentals_ratios,
    load_fundamentals_fixture,
)
from .promised_vs_delivered import (
    get_commitment_summary,
    get_company_commitments,
    load_commitments_fixture,
)
from .research import list_research_modules, synthesize_research
from .ask import get_conversation_history, get_suggested_questions, process_ask_query
from .schemas import (
    Alert, AlertConfigInput, AlertConfigResponse, AlertsResponse, AnomaliesResponse,
    AnnouncementCategory, AnnouncementListResponse, AnnouncementRefreshRequest,
    AnnouncementRefreshResponse,
    AskRequest, AskResponse, Citation, CommitmentCategory, CommitmentRecord,
    CommitmentStatus, CommitmentSummaryResponse, CompanyCommitmentsResponse,
    DigestItem, DigestResponse, FilingCardResponse,
    FundamentalsHistoryResponse, FundamentalsOverview, FundamentalsRatiosResponse,
    PortfolioItem, PortfolioResponse, ResearchRequest,
)

logger = logging.getLogger("finn.main")

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parents[1]
FIXTURE_DIR = Path(os.getenv("FIXTURE_DIR", ROOT_DIR / "data" / "fixtures"))
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("true", "1")

refresh_lock = asyncio.Lock()
last_refresh_source_failure: bool = False

app = FastAPI(title="FINN API", version="0.1.0")
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
if cors_origins_env == "*":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=r"^https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def fixture(name: str, default: dict) -> dict:
    path = FIXTURE_DIR / name
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
    except (OSError, json.JSONDecodeError):
        return default


async def _check_and_trigger_startup_refresh() -> None:
    stale_hours = float(os.getenv("REFRESH_STALE_HOURS", "12"))
    cutoff = datetime.now(timezone.utc) - timedelta(hours=stale_hours)
    needs_refresh = False
    with connect() as conn:
        newest_price = conn.execute("SELECT MAX(fetched_at) FROM prices WHERE source NOT LIKE 'fixture%'").fetchone()[0]
        newest_ann = conn.execute("SELECT MAX(created_at) FROM announcements WHERE COALESCE(demo_data, 0)=0 AND source != 'fixture'").fetchone()[0]

    p_stamp = parse_timestamp(newest_price) if newest_price else None
    a_stamp = parse_timestamp(newest_ann) if newest_ann else None

    if p_stamp is None or p_stamp < cutoff or a_stamp is None or a_stamp < cutoff:
        needs_refresh = True

    if needs_refresh and not refresh_lock.locked():
        async with refresh_lock:
            await _run_live_refresh()


async def _run_live_refresh() -> dict[str, Any]:
    global last_refresh_source_failure
    logger.info("Starting background refresh of prices and announcements...")
    try:
        loop = asyncio.get_event_loop()
        p_res = await loop.run_in_executor(None, refresh_prices)
    except Exception as exc:
        logger.error("Price refresh error: %s", exc)
        p_res = {"updated": 0, "error": str(exc)}

    lookback = int(os.getenv("ANNOUNCEMENT_LOOKBACK_DAYS", "30"))
    to_date = date.today()
    from_date = to_date - timedelta(days=lookback)
    with connect() as conn:
        tickers = [row[0] for row in conn.execute("SELECT ticker FROM companies WHERE is_portfolio=1 ORDER BY ticker").fetchall()]

    ann_results = {}
    for t in tickers:
        try:
            res = await ingest_announcements(t, from_date=from_date, to_date=to_date, demo_mode=DEMO_MODE, fallback_to_fixture=DEMO_MODE)
            ann_results[t] = res
        except Exception as exc:
            logger.warning("Announcement ingest error for %s: %s", t, exc)
            ann_results[t] = {"ticker": t, "error": str(exc)}

    try:
        process_management_changes()
    except Exception as exc:
        logger.warning("Management changes process error: %s", exc)

    all_prices_failed = p_res.get("updated", 0) == 0
    all_ann_failed = all(r.get("inserted", 0) == 0 for r in ann_results.values() if isinstance(r, dict))
    last_refresh_source_failure = all_prices_failed and all_ann_failed
    return {"prices": p_res, "announcements": ann_results}


@app.on_event("startup")
async def startup() -> None:
    init_db()
    if DEMO_MODE:
        try:
            load_demo_announcements_fixture()
        except Exception as exc:
            logger.warning("Failed to load demo announcements fixture: %s", exc)
    try:
        load_fundamentals_fixture()
    except Exception:
        pass
    try:
        load_commitments_fixture()
    except Exception:
        pass
    if not DEMO_MODE:
        asyncio.create_task(_check_and_trigger_startup_refresh())


@app.get("/health")
def health() -> dict:
    db_ok = False
    table_count = 0
    price_info = {"rows": 0, "tickers": 0, "latest_date": None, "last_fetched_at": None}
    ann_info = {"rows": 0, "live_rows": 0, "demo_rows": 0, "latest": None, "last_fetched_at": None}
    try:
        with connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()
            if row:
                table_count = row[0]
                db_ok = True

            p_stats = conn.execute(
                """SELECT COUNT(*), COUNT(DISTINCT ticker), MAX(trading_date), MAX(fetched_at)
                   FROM prices WHERE source NOT LIKE 'fixture%'"""
                if not DEMO_MODE else
                """SELECT COUNT(*), COUNT(DISTINCT ticker), MAX(trading_date), MAX(fetched_at)
                   FROM prices"""
            ).fetchone()
            if p_stats:
                price_info = {
                    "rows": p_stats[0] or 0,
                    "tickers": p_stats[1] or 0,
                    "latest_date": p_stats[2],
                    "last_fetched_at": p_stats[3],
                }

            a_stats = conn.execute(
                """SELECT COUNT(*),
                          SUM(CASE WHEN COALESCE(demo_data, 0)=0 AND source != 'fixture' THEN 1 ELSE 0 END),
                          SUM(CASE WHEN COALESCE(demo_data, 0)=1 OR source = 'fixture' THEN 1 ELSE 0 END),
                          MAX(timestamp),
                          MAX(created_at)
                   FROM announcements"""
            ).fetchone()
            if a_stats:
                ann_info = {
                    "rows": a_stats[0] or 0,
                    "live_rows": a_stats[1] or 0,
                    "demo_rows": a_stats[2] or 0,
                    "latest": a_stats[3],
                    "last_fetched_at": a_stats[4],
                }
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "service": "finn-api",
        "demo_mode": DEMO_MODE,
        "database_connected": db_ok,
        "tables_count": table_count,
        "timestamp": now_utc().isoformat(),
        "version": "1.0.0",
        "datasets": {
            "prices": price_info,
            "announcements": ann_info,
            "mode": "demo" if DEMO_MODE else "live",
            "refresh_in_progress": refresh_lock.locked(),
        },
    }


@app.get("/portfolio", response_model=PortfolioResponse)
def get_portfolio() -> PortfolioResponse:
    today = date.today()
    with connect() as conn:
        companies = conn.execute(
            "SELECT ticker, name, sector FROM companies WHERE is_portfolio=1 ORDER BY ticker"
        ).fetchall()

        price_rows = conn.execute(
            """SELECT ticker, trading_date, close, volume, source, fetched_at
               FROM prices
               WHERE source NOT LIKE 'fixture%'
               ORDER BY ticker, trading_date ASC"""
            if not DEMO_MODE else
            """SELECT ticker, trading_date, close, volume, source, fetched_at
               FROM prices
               ORDER BY ticker, trading_date ASC"""
        ).fetchall()

    by_ticker: dict[str, list[sqlite3.Row]] = defaultdict(list)
    for row in price_rows:
        by_ticker[row["ticker"]].append(row)

    portfolio_items: list[PortfolioItem] = []
    for comp in companies:
        ticker = comp["ticker"]
        rows = by_ticker.get(ticker, [])
        if not rows:
            portfolio_items.append(PortfolioItem(
                ticker=ticker,
                name=comp["name"],
                sector=comp["sector"],
                latest_close=None,
                prev_close=None,
                change_pct=None,
                latest_volume=None,
                vol_ratio_20d=None,
                as_of_date=None,
                source=None,
                fetched_at=None,
                is_stale=False,
                status="no_data",
            ))
            continue

        latest = rows[-1]
        latest_close = float(latest["close"])
        as_of_date_str = str(latest["trading_date"])
        try:
            as_of_d = date.fromisoformat(as_of_date_str)
            is_stale = (today - as_of_d).days > 4
        except ValueError:
            is_stale = False
        source = str(latest["source"])
        fetched_at = str(latest["fetched_at"]) if latest["fetched_at"] else None
        latest_vol = int(latest["volume"]) if latest["volume"] is not None else None

        prev_close = None
        change_pct = None
        vol_ratio = None
        if len(rows) >= 2:
            prev = rows[-2]
            prev_close = float(prev["close"])
            if prev_close > 0:
                change_pct = round(((latest_close - prev_close) / prev_close) * 100, 2)

            prior_20 = [r["volume"] for r in rows[-21:-1]]
            if len(prior_20) == 20 and latest_vol is not None and all(v is not None for v in prior_20):
                avg_vol = sum(prior_20) / 20.0
                if avg_vol > 0:
                    vol_ratio = round(latest_vol / avg_vol, 2)

        portfolio_items.append(PortfolioItem(
            ticker=ticker,
            name=comp["name"],
            sector=comp["sector"],
            latest_close=latest_close,
            prev_close=prev_close,
            change_pct=change_pct,
            latest_volume=latest_vol,
            vol_ratio_20d=vol_ratio,
            as_of_date=as_of_date_str,
            source=source,
            fetched_at=fetched_at,
            is_stale=is_stale,
            status="ok",
        ))

    return PortfolioResponse(
        as_of=now_utc(),
        demo_mode=DEMO_MODE,
        data_source=price_data_source(),
        companies=portfolio_items,
    )


@app.get("/digest", response_model=DigestResponse)
def get_digest(
    window: Literal["24h", "3d", "7d", "custom"] = "24h",
    from_at: datetime | None = Query(default=None, alias="from"),
    to: datetime | None = Query(default=None),
    to_at: datetime | None = None,
    ticker: str | None = Query(default=None, pattern=r"^[A-Za-z0-9&._-]{1,24}$"),
    category: str | None = Query(default=None, pattern=r"^[A-Za-z0-9_& -]{1,48}$"),
    min_materiality: float | None = Query(default=None, ge=0, le=10),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort: Literal["relevance", "recency"] = "relevance",
) -> DigestResponse:
    allowed_categories = {
        "results", "M&A", "fund_raise", "management_change", "litigation", "insider_trading",
        "earnings_call", "investor_meetings", "credit_rating", "dividend", "bonus_split", "capex",
        "press_release", "postal_ballot", "agm_egm", "pledging", "unclassified",
        "price_volume_anomaly", "price_anomaly", "volume_anomaly", "results_card",
    }
    if category is not None and category not in allowed_categories:
        raise HTTPException(422, "unsupported digest category")
    announcements = list_announcements(limit=500, exclude_demo=not DEMO_MODE)
    anomalies, anomaly_as_of, anomaly_demo = refresh_anomalies(exclude_fixtures=not DEMO_MODE)
    anomaly_source = price_data_source()
    with connect() as conn:
        company_rows = conn.execute("SELECT ticker,name,is_portfolio FROM companies").fetchall()
        result_rows = conn.execute("""SELECT e.extraction_key AS filing_id,e.value_json,
            COALESCE(f.ticker,e.ticker) AS ticker,f.headline,f.filed_at,f.attachment_url,f.raw_url,f.source,c.name AS company_name
            FROM extractions e LEFT JOIN filings f ON f.id=e.extraction_key
            LEFT JOIN companies c ON c.ticker=f.ticker WHERE e.module='results_card'
            ORDER BY e.created_at DESC""").fetchall()
        filing_rows = conn.execute("""SELECT f.id,f.ticker,c.name AS company_name,f.filed_at,f.category,
            f.headline,f.raw_url,f.attachment_url,f.filing_ref,f.source,e.summary,e.priority,
            e.key_points_json,e.citations_json FROM filings f JOIN companies c ON c.ticker=f.ticker
            JOIN filing_enrichment e ON e.filing_id=f.id WHERE e.priority IN ('high','medium')
            ORDER BY f.filed_at DESC LIMIT 500""").fetchall()
        last_price_fetch = conn.execute("SELECT MAX(fetched_at) FROM prices").fetchone()[0]
        last_ann_fetch = conn.execute("SELECT MAX(created_at) FROM announcements").fetchone()[0]
        total_live_prices = conn.execute("SELECT COUNT(*) FROM prices WHERE source NOT LIKE 'fixture%'").fetchone()[0]
        total_live_ann = conn.execute("SELECT COUNT(*) FROM announcements WHERE COALESCE(demo_data, 0)=0 AND source != 'fixture'").fetchone()[0]

    company_names = {row["ticker"]: row["name"] for row in company_rows}
    portfolio_tickers = {row["ticker"] for row in company_rows if row["is_portfolio"]}
    for anomaly in anomalies:
        anomaly["data_source"] = anomaly_source
        anomaly["demo_mode"] = anomaly_demo or anomaly_source in ("fixture-csv", "mixed")
    result_cards = []
    for row in result_rows:
        value = dict(row)
        try:
            value["card"] = json.loads(value.pop("value_json"))
        except (TypeError, json.JSONDecodeError):
            continue
        value["company_name"] = value.get("company_name") or value["card"].get("company_name")
        value["source"] = value.get("source") or value["card"].get("source_type")
        if value.get("ticker"):
            result_cards.append(value)
    management_events = list_management_changes(limit=500, exclude_demo=not DEMO_MODE)
    all_items, collapsed_total = build_source_items(
        announcements=announcements, anomalies=anomalies, management_events=management_events,
        results_cards=result_cards, enriched_filings=[dict(row) for row in filing_rows],
        company_names=company_names, portfolio_tickers=portfolio_tickers,
        as_of=anomaly_as_of if anomaly_as_of else now_utc(),
    )
    demo_mode = DEMO_MODE or anomaly_demo or any(item["demo_mode"] for item in all_items)
    announcement_as_of = announcement_snapshot_as_of(announcements, DEMO_MODE)
    snapshot_candidates = []
    if DEMO_MODE or any(item.get("source") == "fixture" for item in announcements):
        snapshot_candidates.append(announcement_as_of)
    if anomaly_source == "fixture-csv":
        snapshot_candidates.append(anomaly_as_of)
    snapshot_candidates.extend(stamp for item in all_items if item.get("demo_mode") and (stamp := parse_timestamp(item.get("occurred_at"))))
    as_of = max(snapshot_candidates) if demo_mode and snapshot_candidates else announcement_as_of if demo_mode else now_utc()
    end = to or to_at or (as_of if demo_mode else now_utc())
    end = end.replace(tzinfo=timezone.utc) if end.tzinfo is None else end.astimezone(timezone.utc)
    if window == "custom":
        if not from_at or not (to or to_at):
            raise HTTPException(422, "custom window requires valid from and to timestamps")
        start = from_at.replace(tzinfo=timezone.utc) if from_at.tzinfo is None else from_at.astimezone(timezone.utc)
        if start >= end:
            raise HTTPException(422, "custom window requires valid from and to timestamps")
    else:
        start = end - {"24h": timedelta(hours=24), "3d": timedelta(days=3), "7d": timedelta(days=7)}[window]
    for item in all_items:
        rank_event(item, as_of=end, portfolio_tickers=portfolio_tickers)
    selected, total = select_digest_items(
        all_items, start=start, end=end, ticker=ticker, category=category,
        min_materiality=min_materiality, sort=sort, limit=limit, offset=offset,
    )

    last_refresh_str = last_price_fetch or last_ann_fetch
    last_refresh_dt = parse_timestamp(last_refresh_str) if last_refresh_str else None

    if last_refresh_source_failure and len(selected) == 0:
        digest_status = "source_unavailable"
    elif not DEMO_MODE and total_live_prices == 0 and total_live_ann == 0:
        digest_status = "never_refreshed"
    elif len(selected) == 0:
        digest_status = "no_data_in_window"
    else:
        digest_status = "ok"

    return DigestResponse(
        window=window, from_at=start, to_at=end,
        as_of=as_of, demo_mode=demo_mode,
        status=digest_status, last_refresh=last_refresh_dt,
        items=selected, collapsed_count=collapsed_total, total_count=total,
        limit=limit, offset=offset, sort=sort,
    )


@app.get("/management-changes")
def get_management_changes(
    ticker: str | None = Query(default=None, pattern=r"^[A-Za-z0-9&._-]{1,24}$"),
    change_type: str | None = Query(default=None, pattern=r"^(appointment|resignation|retirement|reappointment|cessation|role_change|unknown)$"),
    min_materiality: float | None = Query(default=None, ge=0, le=10),
    limit: int = Query(default=100, ge=1, le=500), offset: int = Query(default=0, ge=0),
):
    events = list_management_changes(ticker=ticker, change_type=change_type,
                                     min_materiality=min_materiality, limit=limit, offset=offset,
                                     exclude_demo=not DEMO_MODE)
    return {"count": len(events), "demo_mode": all(x["source"] == "fixture" for x in events) if events else DEMO_MODE,
            "events": events}


@app.post("/management-changes/process")
def process_existing_management_announcements(
    ticker: str | None = Query(default=None, pattern=r"^[A-Za-z0-9&._-]{1,24}$"),
    limit: int = Query(default=200, ge=1, le=500),
):
    return process_management_changes(ticker=ticker, limit=limit)


@app.get("/alerts", response_model=AlertsResponse)
def get_alerts() -> AlertsResponse:
    with connect() as conn:
        configs = conn.execute("SELECT * FROM alert_config WHERE enabled=1").fetchall()

    vol_x = 2.0
    pct = 3.0
    categories = {"management_change", "results", "M&A", "dividend"}
    min_mat = 7.0

    ticker_configs: dict[str, dict[str, Any]] = {}
    for cfg in configs:
        c_dict = dict(cfg)
        try:
            c_dict["announcement_categories"] = json.loads(c_dict.get("announcement_categories_json") or "[]")
        except Exception:
            c_dict["announcement_categories"] = []
        if c_dict.get("ticker"):
            ticker_configs[c_dict["ticker"]] = c_dict
        else:
            if c_dict.get("volume_multiple"):
                vol_x = float(c_dict["volume_multiple"])
            if c_dict.get("price_move_pct"):
                pct = float(c_dict["price_move_pct"])
            if c_dict.get("announcement_categories"):
                categories = set(c_dict["announcement_categories"])

    anomalies, _, _ = refresh_anomalies(vol_x=vol_x, pct=pct, exclude_fixtures=not DEMO_MODE)
    alerts: list[Alert] = []
    for anom in anomalies:
        t = anom["ticker"]
        if t in ticker_configs:
            tc = ticker_configs[t]
            if tc.get("volume_multiple") and anom["anomaly_type"] == "volume_spike" and anom["observed_value"] < tc["volume_multiple"]:
                continue
            if tc.get("price_move_pct") and anom["anomaly_type"] == "price_move" and abs(anom["observed_value"]) < tc["price_move_pct"]:
                continue

        kind = "price" if anom["anomaly_type"] == "price_move" else "volume"
        det_date = date.fromisoformat(anom["detected_at"])
        alerts.append(Alert(
            id=f"alert:{kind}:{t}:{anom['detected_at']}",
            kind=kind,
            alert_type=anom["anomaly_type"],
            ticker=t,
            title=f"{t} {anom['anomaly_type'].replace('_', ' ').title()}",
            reason=anom["explanation"],
            message=anom["explanation"],
            triggered_at=datetime.combine(det_date, day_time.min, tzinfo=timezone.utc),
            source="yfinance" if not DEMO_MODE else "fixture-csv",
            read=False,
        ))

    ann_rows = list_announcements(limit=200, exclude_demo=not DEMO_MODE)
    now = now_utc()
    window_start = now - timedelta(hours=24)
    for ann_item in ann_rows:
        t = ann_item["ticker"]
        cat = ann_item.get("classification", "unclassified")
        mat = float(ann_item.get("materiality_score") or 0)

        cat_match = cat in categories
        mat_match = mat >= min_mat
        if not (cat_match or mat_match):
            continue

        stamp = parse_timestamp(ann_item.get("timestamp"))
        if stamp:
            stamp_utc = stamp.replace(tzinfo=timezone.utc) if stamp.tzinfo is None else stamp.astimezone(timezone.utc)
            if not DEMO_MODE and stamp_utc < window_start:
                continue

        alerts.append(Alert(
            id=f"alert:announcement:{ann_item['id']}",
            kind="announcement",
            alert_type="announcement",
            ticker=t,
            title=f"{t}: {cat.replace('_', ' ').title()}",
            reason=ann_item.get("summary") or ann_item.get("headline", ""),
            message=ann_item.get("summary") or ann_item.get("headline", ""),
            triggered_at=stamp_utc if stamp else now,
            source=ann_item.get("source", "system"),
            read=False,
        ))

    return AlertsResponse(
        as_of=now_utc(),
        demo_mode=DEMO_MODE,
        alerts=alerts,
    )


@app.post("/alerts/config", response_model=AlertConfigResponse)
def save_alert_config(payload: AlertConfigInput) -> AlertConfigResponse:
    with connect() as conn:
        if payload.ticker:
            exists = conn.execute("SELECT 1 FROM companies WHERE ticker=?", (payload.ticker.upper(),)).fetchone()
            if not exists:
                conn.execute(
                    "INSERT INTO companies(ticker,name) VALUES(?,?)",
                    (payload.ticker.upper(), payload.ticker.upper()),
                )
        cursor = conn.execute(
            """INSERT INTO alert_config
            (ticker,enabled,announcement_categories_json,price_move_pct,volume_multiple,notify_on_high_priority)
            VALUES (?,?,?,?,?,?)""",
            (payload.ticker.upper() if payload.ticker else None, int(payload.enabled),
             json.dumps(payload.announcement_categories), payload.price_move_pct,
             payload.volume_multiple, int(payload.notify_on_high_priority)),
        )
        row = conn.execute("SELECT * FROM alert_config WHERE id=?", (cursor.lastrowid,)).fetchone()
    return AlertConfigResponse(
        id=row["id"], ticker=row["ticker"], enabled=bool(row["enabled"]),
        announcement_categories=json.loads(row["announcement_categories_json"]),
        price_move_pct=row["price_move_pct"], volume_multiple=row["volume_multiple"],
        notify_on_high_priority=bool(row["notify_on_high_priority"]),
        updated_at=row["updated_at"],
    )


@app.get("/anomalies", response_model=AnomaliesResponse)
def get_anomalies(
    ticker: str | None = Query(default=None, pattern=r"^[A-Za-z0-9&._-]{1,24}$"),
    vol_x: float = Query(default=2.0, gt=0, allow_inf_nan=False, description="Volume anomaly threshold as a multiple of the previous 20-session average"),
    pct: float = Query(default=3.0, gt=0, allow_inf_nan=False, description="Absolute close-to-close price change threshold in percent"),
) -> AnomaliesResponse:
    import inspect
    sig = inspect.signature(refresh_anomalies)
    kwargs = {"vol_x": vol_x, "pct": pct, "ticker": ticker}
    if "exclude_fixtures" in sig.parameters:
        kwargs["exclude_fixtures"] = not DEMO_MODE
    anomalies, as_of, demo_mode = refresh_anomalies(**kwargs)
    return AnomaliesResponse(
        as_of=as_of, demo_mode=demo_mode, data_source=price_data_source(ticker=ticker),
        anomalies=anomalies,
    )


@app.get("/announcements", response_model=AnnouncementListResponse)
def get_announcements(
    ticker: str | None = Query(default=None, pattern=r"^[A-Za-z0-9&._-]{1,24}$"),
    category: AnnouncementCategory | None = None,
    min_materiality: float | None = Query(default=None, ge=0, le=10),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> AnnouncementListResponse:
    items = list_announcements(
        ticker=ticker, category=category, min_materiality=min_materiality,
        limit=limit, offset=offset, exclude_demo=not DEMO_MODE,
    )
    return AnnouncementListResponse(
        as_of=announcement_snapshot_as_of(items, DEMO_MODE), demo_mode=announcement_demo_mode(items, DEMO_MODE),
        count=len(items), announcements=items,
    )


@app.get("/announcements/high-materiality", response_model=AnnouncementListResponse)
def get_high_materiality_announcements(
    ticker: str | None = Query(default=None, pattern=r"^[A-Za-z0-9&._-]{1,24}$"),
    min_materiality: float = Query(default=5, ge=0, le=10),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> AnnouncementListResponse:
    items = list_announcements(
        ticker=ticker, min_materiality=min_materiality, limit=limit, offset=offset,
        exclude_demo=not DEMO_MODE,
    )
    return AnnouncementListResponse(
        as_of=announcement_snapshot_as_of(items, DEMO_MODE), demo_mode=announcement_demo_mode(items, DEMO_MODE),
        count=len(items), announcements=items,
    )


@app.post("/announcements/refresh", response_model=AnnouncementRefreshResponse)
def refresh_company_announcements(payload: AnnouncementRefreshRequest) -> AnnouncementRefreshResponse:
    end = payload.to_date or date.today()
    start = payload.from_date or (end - timedelta(days=30))
    if start > end:
        raise HTTPException(422, "from_date must not be after to_date")
    report = asyncio.run(ingest_announcements(
        payload.ticker, from_date=start, to_date=end, demo_mode=DEMO_MODE,
    ))
    return AnnouncementRefreshResponse(**report)


@app.get("/filing/{filing_id}/card", response_model=FilingCardResponse)
def get_filing_card(filing_id: str) -> FilingCardResponse:
    data = fixture("filings.json", {"items": []})
    item = next((x for x in data["items"] if x["id"] == filing_id), None)
    if not item:
        raise HTTPException(404, "Filing not found; use the raw filing link if available")
    item.setdefault("as_of", now_utc().isoformat())
    item.setdefault("demo_mode", DEMO_MODE)
    return FilingCardResponse(**item)


@app.get("/filing/{filing_id}/results-card")
async def get_results_card(filing_id: str):
    """Return a cached results card or generate it from the filing PDF on first access."""
    try:
        card = await get_or_generate_results_card(filing_id, demo_mode=DEMO_MODE)
    except ResultExtractionError as exc:
        raise HTTPException(422, str(exc)) from exc
    if card is None:
        raise HTTPException(404, "Filing not found")
    return card


@app.get("/results-filings")
def get_results_filings(
    ticker: str | None = Query(default=None, pattern=r"^[A-Za-z0-9&._-]{1,24}$"),
    limit: int = Query(default=100, ge=1, le=500),
):
    """List stored results filings available to generate or reopen a results card."""
    filings = list_results_filings(ticker=ticker, limit=limit)
    return {
        "count": len(filings),
        "demo_mode": all(item["source"] == "fixture" for item in filings) if filings else DEMO_MODE,
        "filings": filings,
    }


@app.get("/research/modules")
def get_research_modules() -> dict[str, Any]:
    return {"modules": list_research_modules(), "count": len(list_research_modules())}


@app.get("/research/{ticker}/{module}")
def get_research_module_result(ticker: str, module: str) -> dict[str, Any]:
    result = synthesize_research(ticker, module)  # type: ignore[arg-type]
    return result.model_dump(mode="json")


@app.post("/research")
async def research(payload: ResearchRequest):
    """SSE: event: progress|result|error; data: JSON object."""
    ticker = payload.ticker.upper()
    module = payload.module

    async def events():
        yield f"event: progress\ndata: {json.dumps({'stage':'source_discovery','message':f'Discovering primary filings and statements for {ticker}'})}\n\n"
        await asyncio.sleep(0.08)
        yield f"event: progress\ndata: {json.dumps({'stage':'data_retrieval','message':f'Querying reported financial records and commitments for {ticker}'})}\n\n"
        await asyncio.sleep(0.08)
        result = synthesize_research(ticker, module)
        yield f"event: progress\ndata: {json.dumps({'stage':'synthesis','message':f'Synthesizing evidence-backed findings for {module}'})}\n\n"
        await asyncio.sleep(0.05)
        yield f"event: result\ndata: {json.dumps(result.model_dump(mode='json'))}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/ask/suggestions/{ticker}")
def get_ask_suggestions(ticker: str) -> dict[str, Any]:
    suggestions = get_suggested_questions(ticker)
    return {"ticker": ticker.upper(), "suggestions": suggestions, "count": len(suggestions)}


@app.get("/ask/history/{conversation_id}")
def get_ask_history(conversation_id: str) -> dict[str, Any]:
    messages = get_conversation_history(conversation_id)
    return {"conversation_id": conversation_id, "messages": messages, "count": len(messages)}


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    return process_ask_query(
        ticker=payload.ticker,
        question=payload.question,
        conversation_id=payload.conversation_id,
    )



@app.get("/fundamentals/{ticker}", response_model=FundamentalsOverview)
def get_company_fundamentals(
    ticker: str,
    basis: Literal["consolidated", "standalone"] = "consolidated",
) -> FundamentalsOverview:
    data = get_fundamentals(ticker=ticker, basis=basis)
    if data is None:
        raise HTTPException(404, f"Fundamentals not found for ticker '{ticker}'")
    return FundamentalsOverview(**data)


@app.get("/fundamentals/{ticker}/history", response_model=FundamentalsHistoryResponse)
def get_company_fundamentals_history(
    ticker: str,
    period_type: Literal["annual", "quarterly"] = "annual",
    basis: Literal["consolidated", "standalone"] = "consolidated",
    limit: int = Query(default=12, ge=1, le=50),
) -> FundamentalsHistoryResponse:
    data = get_fundamentals_history(ticker=ticker, period_type=period_type, basis=basis, limit=limit)
    if not data["periods"]:
        # Check if ticker exists
        with connect() as conn:
            exists = conn.execute("SELECT 1 FROM companies WHERE ticker = ?", (ticker.upper(),)).fetchone()
        if not exists:
            raise HTTPException(404, f"Company '{ticker}' not found")
    return FundamentalsHistoryResponse(**data)


@app.get("/fundamentals/{ticker}/ratios", response_model=FundamentalsRatiosResponse)
def get_company_fundamentals_ratios(
    ticker: str,
    basis: Literal["consolidated", "standalone"] = "consolidated",
) -> FundamentalsRatiosResponse:
    data = get_fundamentals_ratios(ticker=ticker, basis=basis)
    if not data["trends"]:
        with connect() as conn:
            exists = conn.execute("SELECT 1 FROM companies WHERE ticker = ?", (ticker.upper(),)).fetchone()
        if not exists:
            raise HTTPException(404, f"Company '{ticker}' not found")
    return FundamentalsRatiosResponse(**data)


@app.get("/commitments/{ticker}", response_model=CompanyCommitmentsResponse)
def get_commitments_for_company(
    ticker: str,
    category: CommitmentCategory | None = None,
    status: CommitmentStatus | None = None,
) -> CompanyCommitmentsResponse:
    data = get_company_commitments(ticker=ticker, category=category, status=status)
    if data is None:
        raise HTTPException(404, f"No commitment records found for ticker '{ticker}'")
    return CompanyCommitmentsResponse(**data)


@app.get("/commitments/{ticker}/summary", response_model=CommitmentSummaryResponse)
def get_company_commitment_summary(ticker: str) -> CommitmentSummaryResponse:
    data = get_commitment_summary(ticker=ticker)
    if data is None:
        raise HTTPException(404, f"No commitment summary found for ticker '{ticker}'")
    return CommitmentSummaryResponse(**data)
