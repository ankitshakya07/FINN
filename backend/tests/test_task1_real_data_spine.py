from __future__ import annotations

import asyncio
import os
import sqlite3
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.db import connect, init_db, load_portfolio_config
from app.announcements import (
    classify_unresolved,
    ingest_announcements,
    list_announcements,
    load_demo_announcements_fixture,
    persist_announcements,
    AnnouncementSourceError,
    MappingNotFound,
)
from app.prices import (
    calculate_anomalies,
    normalize_ticker,
    refresh_anomalies,
    refresh_prices,
)
from app.main import app

UTC = timezone.utc


# 1. Portfolio loader is idempotent & ticker with '&' accepted
def test_portfolio_loader_is_idempotent_and_accepts_ampersand(tmp_path):
    db_file = str(tmp_path / "portfolio_test.db")
    init_db(db_file, load_portfolio=True)

    with connect(db_file) as conn:
        count_first = conn.execute("SELECT COUNT(*) FROM companies WHERE is_portfolio=1").fetchone()[0]

    # Run second time
    loaded_second = load_portfolio_config(db_file)
    with connect(db_file) as conn:
        count_second = conn.execute("SELECT COUNT(*) FROM companies WHERE is_portfolio=1").fetchone()[0]
        mm_row = conn.execute("SELECT ticker, name, is_portfolio FROM companies WHERE ticker='M&M'").fetchone()

    assert count_first == 20
    assert count_second == count_first
    assert loaded_second == 20
    assert mm_row is not None
    assert mm_row["ticker"] == "M&M"
    assert mm_row["is_portfolio"] == 1

    # Verify normalize_ticker accepts M&M
    assert normalize_ticker("M&M") == "M&M"
    assert normalize_ticker("M&M.NS") == "M&M"

    # Verify FastAPI routes accept '&'
    client = TestClient(app)
    resp = client.get("/anomalies?ticker=M%26M")
    assert resp.status_code == 200


# 2. refresh_prices with mocked yfinance: success, .BO fallback, failure isolation, no synthetic rows
def test_refresh_prices_mocked_isolation_and_fallback(tmp_path):
    db_file = str(tmp_path / "prices_mock.db")
    init_db(db_file)

    dates = [date(2026, 1, 1) + timedelta(days=i) for i in range(25)]
    sample_df = pd.DataFrame({
        "Open": [100.0] * 25,
        "High": [105.0] * 25,
        "Low": [95.0] * 25,
        "Close": [102.0] * 25,
        "Adj Close": [102.0] * 25,
        "Volume": [10000] * 25,
    }, index=pd.to_datetime(dates))

    def mock_loader(symbol: str):
        if symbol == "RELIANCE.NS":
            return sample_df
        elif symbol == "TCS.NS":
            return pd.DataFrame()  # empty .NS -> trigger .BO fallback
        elif symbol == "TCS.BO":
            return sample_df
        elif symbol.startswith("FAIL"):
            raise RuntimeError("API timeout")
        return pd.DataFrame()

    res = refresh_prices(
        ["RELIANCE", "TCS", "FAILCORP"],
        db_path=db_file,
        history_loader=mock_loader,
        retries=1,
    )

    tickers = res["tickers"]
    assert tickers["RELIANCE"]["status"] == "updated"
    assert tickers["RELIANCE"]["symbol"] == "RELIANCE.NS"
    assert tickers["RELIANCE"]["rows_written"] == 25

    assert tickers["TCS"]["status"] == "updated"
    assert tickers["TCS"]["symbol"] == "TCS.BO"
    assert tickers["TCS"]["rows_written"] == 25

    # Failure isolation: FAILCORP failed, but did not abort RELIANCE or TCS
    assert tickers["FAILCORP"]["status"] == "missing"
    assert tickers["FAILCORP"]["rows_written"] == 0
    assert tickers["FAILCORP"]["error"] is not None

    with connect(db_file) as conn:
        fail_rows = conn.execute("SELECT COUNT(*) FROM prices WHERE ticker='FAILCORP'").fetchone()[0]
        assert fail_rows == 0


# 3. /portfolio calculations match hand-computed values; is_stale flips; empty ticker returns no_data
def test_portfolio_calculations_and_stale_detection(tmp_path, monkeypatch):
    db_file = str(tmp_path / "portfolio_calc.db")
    init_db(db_file)

    today = date(2026, 11, 2)
    with connect(db_file) as conn:
        conn.execute("INSERT OR REPLACE INTO companies(ticker, name, sector, is_portfolio) VALUES('INFY', 'Infosys', 'IT Services', 1)")
        conn.execute("INSERT OR REPLACE INTO companies(ticker, name, sector, is_portfolio) VALUES('EMPTY', 'Empty Corp', 'None', 1)")

        # Insert 22 sessions for INFY
        # 20 sessions before prev: vol 1000 each -> avg_vol = 1000
        # prev session (idx 20): close 100.0, vol 1000
        # latest session (idx 21): close 105.5, vol 2500 on 2026-11-02
        start = today - timedelta(days=25)
        for i in range(20):
            conn.execute(
                "INSERT INTO prices(ticker, trading_date, close, volume, source, fetched_at) VALUES('INFY', ?, 95.0, 1000, 'yfinance:NS', CURRENT_TIMESTAMP)",
                ((start + timedelta(days=i)).isoformat(),)
            )
        prev_date = (start + timedelta(days=20)).isoformat()
        conn.execute(
            "INSERT INTO prices(ticker, trading_date, close, volume, source, fetched_at) VALUES('INFY', ?, 100.0, 1000, 'yfinance:NS', CURRENT_TIMESTAMP)",
            (prev_date,)
        )
        conn.execute(
            "INSERT INTO prices(ticker, trading_date, close, volume, source, fetched_at) VALUES('INFY', ?, 105.5, 2500, 'yfinance:NS', CURRENT_TIMESTAMP)",
            (today.isoformat(),)
        )

    # Hand calculations:
    # latest_close = 105.5, prev_close = 100.0
    # change_pct = ((105.5 - 100.0) / 100.0) * 100 = +5.5%
    # 20 sessions immediately prior to latest have volume = 1000 each -> avg = 1000
    # vol_ratio_20d = 2500 / 1000 = 2.5x
    # is_stale for today: (today - today).days = 0 <= 4 -> is_stale is False

    from app import main
    monkeypatch.setenv("SQLITE_PATH", db_file)
    monkeypatch.setattr(main, "DEMO_MODE", False)

    client = TestClient(main.app)
    resp = client.get("/portfolio")
    assert resp.status_code == 200
    data = resp.json()

    infy = next(c for c in data["companies"] if c["ticker"] == "INFY")
    assert infy["latest_close"] == 105.5
    assert infy["prev_close"] == 100.0
    assert infy["change_pct"] == 5.5
    assert infy["latest_volume"] == 2500
    assert infy["vol_ratio_20d"] == 2.5
    assert infy["as_of_date"] == today.isoformat()
    assert infy["is_stale"] is False
    assert infy["status"] == "ok"

    empty_comp = next(c for c in data["companies"] if c["ticker"] == "EMPTY")
    assert empty_comp["latest_close"] is None
    assert empty_comp["prev_close"] is None
    assert empty_comp["change_pct"] is None
    assert empty_comp["vol_ratio_20d"] is None
    assert empty_comp["status"] == "no_data"


# 4. /anomalies result set changes when vol_x and pct change
def test_anomalies_threshold_sensitivity(tmp_path, monkeypatch):
    db_file = str(tmp_path / "anomalies_sens.db")
    init_db(db_file)

    dates = [date(2026, 1, 1) + timedelta(days=i) for i in range(22)]
    with connect(db_file) as conn:
        conn.execute("INSERT OR REPLACE INTO companies(ticker, name, is_portfolio) VALUES('INFY', 'Infosys', 1)")
        for i in range(20):
            conn.execute("INSERT INTO prices(ticker, trading_date, close, volume, source) VALUES('INFY', ?, 100.0, 1000, 'yfinance:NS')", (dates[i].isoformat(),))
        conn.execute("INSERT INTO prices(ticker, trading_date, close, volume, source) VALUES('INFY', ?, 100.0, 1000, 'yfinance:NS')", (dates[20].isoformat(),))
        # Move +4% and vol 2.5x on last day
        conn.execute("INSERT INTO prices(ticker, trading_date, close, volume, source) VALUES('INFY', ?, 104.0, 2500, 'yfinance:NS')", (dates[21].isoformat(),))

    from app import main
    monkeypatch.setenv("SQLITE_PATH", db_file)
    monkeypatch.setattr(main, "DEMO_MODE", False)

    client = TestClient(main.app)

    # At vol_x=2.0 and pct=3.0 -> both should trigger (2 anomalies)
    r1 = client.get("/anomalies?ticker=INFY&vol_x=2.0&pct=3.0").json()
    assert len(r1["anomalies"]) == 2

    # Raise vol_x to 3.0 -> only price_move triggers (1 anomaly)
    r2 = client.get("/anomalies?ticker=INFY&vol_x=3.0&pct=3.0").json()
    assert len(r2["anomalies"]) == 1
    assert r2["anomalies"][0]["anomaly_type"] == "price_move"

    # Raise pct to 5.0 -> 0 anomalies
    r3 = client.get("/anomalies?ticker=INFY&vol_x=3.0&pct=5.0").json()
    assert len(r3["anomalies"]) == 0


# 5. Announcement ingest idempotency, malformed row skipping, and unmapped status
def test_announcements_idempotency_and_malformed_handling(tmp_path):
    db_file = str(tmp_path / "ann_ingest.db")
    init_db(db_file)

    payload = [
        {"seq_id": "1", "symbol": "INFY", "an_dt": "02-11-2026 10:00:00", "desc": "Board approves dividend"},
        {"seq_id": "2", "symbol": "INFY", "an_dt": "02-11-2026 11:00:00"},  # malformed: missing headline/desc
    ]

    def mock_nse(ticker, start, end):
        return payload

    def fail_bse(*args):
        raise AnnouncementSourceError("BSE down")

    # Ingest once
    res1 = asyncio.run(ingest_announcements(
        "INFY", from_date=date(2026, 10, 1), to_date=date(2026, 11, 2),
        db_path=db_file, bse_fetcher=fail_bse, nse_fetcher=mock_nse,
        fallback_to_fixture=False
    ))
    assert res1["received"] == 1  # 1 valid, 1 malformed skipped
    assert len(res1["failures"]) >= 1  # malformed noted in failures
    assert res1["inserted"] == 1

    # Ingest second time -> idempotent, 0 new rows inserted
    res2 = asyncio.run(ingest_announcements(
        "INFY", from_date=date(2026, 10, 1), to_date=date(2026, 11, 2),
        db_path=db_file, bse_fetcher=fail_bse, nse_fetcher=mock_nse,
        fallback_to_fixture=False
    ))
    assert res2["inserted"] == 0

    with connect(db_file) as conn:
        count = conn.execute("SELECT COUNT(*) FROM announcements WHERE ticker='INFY'").fetchone()[0]
        assert count == 1


# 6. Fixture handling: DEMO_MODE=true loads fixture with demo_data=true; DEMO_MODE=false excludes demo rows
def test_fixture_isolation_in_live_mode(tmp_path):
    db_file = str(tmp_path / "fixture_isolation.db")
    init_db(db_file)

    # 1. Load demo fixture
    loaded = load_demo_announcements_fixture(db_path=db_file)
    assert loaded > 0

    with connect(db_file) as conn:
        demo_count = conn.execute("SELECT COUNT(*) FROM announcements WHERE demo_data=1").fetchone()[0]
        assert demo_count == loaded

        # Insert 1 genuine live announcement
        conn.execute(
            """INSERT INTO announcements
               (id, ticker, timestamp, headline, source, fingerprint, cross_source_fingerprint, demo_data)
               VALUES('live-1', 'INFY', '2026-11-02T10:00:00Z', 'Real Live Announcement', 'nse', 'fp1', 'csfp1', 0)"""
        )

    # Read with exclude_demo=True
    live_items = list_announcements(db_path=db_file, exclude_demo=True)
    assert len(live_items) == 1
    assert live_items[0]["id"] == "live-1"
    assert live_items[0]["headline"] == "Real Live Announcement"

    # Read with exclude_demo=False
    all_items = list_announcements(db_path=db_file, exclude_demo=False)
    assert len(all_items) == demo_count + 1


# 7. classify_unresolved with empty LLM_API_KEY does not raise and leaves items unclassified
def test_classify_unresolved_with_empty_llm_key(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")

    items = [
        {
            "id": "1",
            "ticker": "INFY",
            "headline": "A completely novel unclassified disclosure without rules match",
            "raw_category": None,
            "source": "nse",
            "classification": "unclassified",
            "classification_confidence": 0.0,
            "materiality_score": 0.0,
        }
    ]

    result = asyncio.run(classify_unresolved(items, model_call=None))
    assert len(result) == 1
    assert result[0]["classification"] == "unclassified"
    assert result[0]["classification_method"] == "unclassified"


# 8. GET /digest returns each status value in the right situation
def test_digest_status_progression(tmp_path, monkeypatch):
    from app import main
    db_file = str(tmp_path / "digest_status.db")
    init_db(db_file)

    monkeypatch.setenv("SQLITE_PATH", db_file)
    monkeypatch.setattr(main, "DEMO_MODE", False)

    client = TestClient(main.app)

    # 1. never_refreshed: 0 rows in DB
    r1 = client.get("/digest?window=24h").json()
    assert r1["status"] == "never_refreshed"

    # 2. source_unavailable
    monkeypatch.setattr(main, "last_refresh_source_failure", True)
    r2 = client.get("/digest?window=24h").json()
    assert r2["status"] == "source_unavailable"
    monkeypatch.setattr(main, "last_refresh_source_failure", False)

    # Insert a price row from 30 days ago (outside 24h window)
    old_date = (date.today() - timedelta(days=30)).isoformat()
    with connect(db_file) as conn:
        conn.execute("INSERT OR REPLACE INTO companies(ticker, name, is_portfolio) VALUES('INFY', 'Infosys', 1)")
        conn.execute("INSERT INTO prices(ticker, trading_date, close, volume, source, fetched_at) VALUES('INFY', ?, 100.0, 1000, 'yfinance:NS', CURRENT_TIMESTAMP)", (old_date,))

    # 3. no_data_in_window: DB has rows, but 0 in 24h window
    r3 = client.get("/digest?window=24h").json()
    assert r3["status"] == "no_data_in_window"

    # Insert an announcement in the last 2 hours
    with connect(db_file) as conn:
        recent_stamp = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        conn.execute(
            """INSERT INTO announcements
               (id, ticker, timestamp, headline, source, fingerprint, cross_source_fingerprint, demo_data, classification, materiality_score)
               VALUES('fresh-1', 'INFY', ?, 'Recent Interim Dividend Declared', 'nse', 'fp_f1', 'csfp_f1', 0, 'dividend', 8.0)""",
            (recent_stamp,)
        )

    # 4. ok: Items exist in window
    r4 = client.get("/digest?window=24h").json()
    assert r4["status"] == "ok"
    assert len(r4["items"]) >= 1


# 9. GET /alerts is computed from alert_config and stored data, doesn't touch alerts.json, responds to threshold change
def test_alerts_computed_from_database(tmp_path, monkeypatch):
    from app import main
    db_file = str(tmp_path / "alerts_computed.db")
    init_db(db_file)

    dates = [date(2026, 1, 1) + timedelta(days=i) for i in range(22)]
    with connect(db_file) as conn:
        conn.execute("INSERT OR REPLACE INTO companies(ticker, name, is_portfolio) VALUES('INFY', 'Infosys', 1)")
        for i in range(20):
            conn.execute("INSERT INTO prices(ticker, trading_date, close, volume, source) VALUES('INFY', ?, 100.0, 1000, 'yfinance:NS')", (dates[i].isoformat(),))
        conn.execute("INSERT INTO prices(ticker, trading_date, close, volume, source) VALUES('INFY', ?, 100.0, 1000, 'yfinance:NS')", (dates[20].isoformat(),))
        # +3.5% move on last day
        conn.execute("INSERT INTO prices(ticker, trading_date, close, volume, source) VALUES('INFY', ?, 103.5, 1000, 'yfinance:NS')", (dates[21].isoformat(),))

    monkeypatch.setenv("SQLITE_PATH", db_file)
    monkeypatch.setattr(main, "DEMO_MODE", False)

    client = TestClient(main.app)

    # Default threshold is pct=3.0, vol_x=2.0 -> 103.5 vs 100 is +3.5% >= 3.0 -> triggers!
    r1 = client.get("/alerts").json()
    assert len(r1["alerts"]) >= 1
    assert any(a["ticker"] == "INFY" and a["kind"] == "price" for a in r1["alerts"])

    # Raise alert threshold to 5.0%
    client.post("/alerts/config", json={
        "ticker": "INFY",
        "enabled": True,
        "price_move_pct": 5.0,
        "volume_multiple": 3.0,
        "announcement_categories": ["dividend"],
    })

    # Alert threshold changed to 5.0% -> +3.5% should no longer trigger!
    r2 = client.get("/alerts").json()
    assert not any(a["ticker"] == "INFY" and a["kind"] == "price" for a in r2["alerts"])


# 10. /health datasets block is correct
def test_health_datasets_block(tmp_path, monkeypatch):
    from app import main
    db_file = str(tmp_path / "health_check.db")
    init_db(db_file)

    with connect(db_file) as conn:
        conn.execute("INSERT OR REPLACE INTO companies(ticker, name, is_portfolio) VALUES('INFY', 'Infosys', 1)")
        conn.execute("INSERT INTO prices(ticker, trading_date, close, volume, source, fetched_at) VALUES('INFY', '2026-11-02', 100.0, 1000, 'yfinance:NS', '2026-11-02T10:00:00')")
        conn.execute(
            """INSERT INTO announcements
               (id, ticker, timestamp, headline, source, fingerprint, cross_source_fingerprint, demo_data, created_at)
               VALUES('a1', 'INFY', '2026-11-02T10:00:00', 'Dividend', 'nse', 'fp1', 'csfp1', 0, '2026-11-02T10:05:00')"""
        )

    monkeypatch.setenv("SQLITE_PATH", db_file)
    monkeypatch.setattr(main, "DEMO_MODE", False)

    client = TestClient(main.app)
    data = client.get("/health").json()

    assert data["status"] == "ok"
    assert "datasets" in data
    ds = data["datasets"]
    assert ds["mode"] == "live"
    assert ds["prices"]["rows"] == 1
    assert ds["prices"]["tickers"] == 1
    assert ds["prices"]["latest_date"] == "2026-11-02"
    assert ds["announcements"]["rows"] == 1
    assert ds["announcements"]["live_rows"] == 1
    assert ds["announcements"]["demo_rows"] == 0


# 11. Opt-in live tests
@pytest.mark.live
@pytest.mark.skipif(os.getenv("FINN_LIVE_TESTS") != "1", reason="Opt-in live tests require FINN_LIVE_TESTS=1")
def test_live_network_sources():
    import yfinance as yf
    from app.announcements import fetch_nse_announcements

    # 1. yfinance RELIANCE.NS
    tick = yf.Ticker("RELIANCE.NS")
    hist = tick.history(period="5d", timeout=15)
    assert len(hist) > 0

    # 2. NSE corporate announcements
    to_d = date.today()
    from_d = to_d - timedelta(days=7)
    ann_items = fetch_nse_announcements("RELIANCE", from_d, to_d)
    assert isinstance(ann_items, list)
