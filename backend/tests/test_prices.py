from __future__ import annotations

import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import connect, init_db
from app.prices import (
    DEFAULT_PORTFOLIO_TICKERS, _store_records, calculate_anomalies,
    download_history, normalize_ticker, refresh_anomalies, refresh_prices,
)


def sessions(*, latest_volume: int = 1_000, previous_close: float = 100.0, latest_close: float = 100.0):
    start = date(2026, 1, 1)
    rows = [
        {
            "trading_date": (start + timedelta(days=index)).isoformat(),
            "close": previous_close,
            "volume": 1_000,
        }
        for index in range(21)
    ]
    rows.append({
        "trading_date": (start + timedelta(days=21)).isoformat(),
        "close": latest_close,
        "volume": latest_volume,
    })
    return rows


def test_both_thresholds_return_both_anomalies_and_combined_reason():
    found = calculate_anomalies("SAMPLE.NS", sessions(latest_volume=3_400, latest_close=105.2))

    assert {item["anomaly_type"] for item in found} == {"volume_spike", "price_move"}
    assert all(item["explanation"] == "Volume 3.4x its 20-day average; price +5.2%" for item in found)
    assert found[0]["ticker"] == "SAMPLE"


def test_volume_anomaly_is_inclusive_at_configured_threshold():
    found = calculate_anomalies("ABC", sessions(latest_volume=2_000), vol_x=2.0, pct=3.0)

    assert [item["anomaly_type"] for item in found] == ["volume_spike"]
    assert found[0]["observed_value"] == 2.0
    assert found[0]["threshold_value"] == 2.0


def test_price_anomaly_supports_negative_change():
    found = calculate_anomalies("ABC", sessions(previous_close=100, latest_close=96.5))

    assert [item["anomaly_type"] for item in found] == ["price_move"]
    assert found[0]["observed_value"] == pytest.approx(-3.5)
    assert found[0]["explanation"] == "price -3.5%"


def test_request_thresholds_control_both_rules():
    rows = sessions(latest_volume=3_400, latest_close=105.2)

    assert calculate_anomalies("ABC", rows, vol_x=3.5, pct=5.3) == []
    found = calculate_anomalies("ABC", rows, vol_x=3.0, pct=6.0)
    assert [item["anomaly_type"] for item in found] == ["volume_spike"]


def test_price_check_works_without_twenty_prior_sessions():
    found = calculate_anomalies(
        "ABC",
        [
            {"trading_date": "2026-01-01", "close": 100, "volume": 1_000},
            {"trading_date": "2026-01-02", "close": 104, "volume": 5_000},
        ],
    )

    assert [item["anomaly_type"] for item in found] == ["price_move"]
    assert found[0]["explanation"] == "price +4.0%"


@pytest.mark.parametrize("vol_x,pct", [(0, 3), (-1, 3), (2, 0), (2, float("nan"))])
def test_thresholds_must_be_positive_finite_request_values(vol_x, pct):
    with pytest.raises(ValueError):
        calculate_anomalies("ABC", sessions(), vol_x=vol_x, pct=pct)


def test_offline_fixture_import_and_database_persistence(tmp_path):
    db_path = str(tmp_path / "prices.db")
    init_db(db_path)

    result = refresh_prices(["SAMPLE"], offline=True, db_path=db_path)
    anomalies, as_of, demo_mode = refresh_anomalies(db_path=db_path)

    assert result["tickers"]["SAMPLE"]["status"] == "updated"
    assert result["tickers"]["SAMPLE"]["rows"] >= 21
    assert as_of.date().isoformat() == "2026-09-30"
    assert demo_mode is True
    assert len(anomalies) == 2
    assert all(item["explanation"] == "Volume 3.4x its 20-day average; price +5.2%" for item in anomalies)
    with connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM prices WHERE ticker='SAMPLE'").fetchone()[0] == result["tickers"]["SAMPLE"]["rows"]
        assert conn.execute("SELECT COUNT(*) FROM anomalies WHERE id LIKE 'price-anomaly:SAMPLE:%'").fetchone()[0] == 2


def test_offline_refresh_reports_tickers_missing_from_fixture(tmp_path):
    db_path = str(tmp_path / "prices.db")
    init_db(db_path)

    result = refresh_prices(["NOTINCSV"], offline=True, db_path=db_path)

    assert result["tickers"]["NOTINCSV"]["status"] == "missing"
    assert result["tickers"]["NOTINCSV"]["rows"] == 0


def test_insufficient_history_and_missing_or_zero_volumes_are_safe():
    assert calculate_anomalies("ABC", sessions()[:1]) == []

    missing = sessions(latest_volume=10_000)
    for row in missing[-21:-1]:
        row["volume"] = None
    assert calculate_anomalies("ABC", missing) == []

    zero = sessions(latest_volume=10_000)
    for row in zero[-21:-1]:
        row["volume"] = 0
    assert calculate_anomalies("ABC", zero) == []


def test_ticker_and_date_upsert_prevents_duplicates_and_keeps_history(tmp_path):
    db_path = str(tmp_path / "prices.db")
    init_db(db_path)
    first = {
        "ticker": "ABC", "trading_date": "2026-09-29", "open": 99.0,
        "high": 102.0, "low": 98.0, "close": 100.0,
        "adjusted_close": 100.0, "volume": 1_000, "source": "fixture-csv",
    }
    _store_records([first], db_path)
    revised = {**first, "close": 101.0, "source": "yfinance:NS"}
    newer = {**first, "trading_date": "2026-09-30", "close": 102.0, "source": "yfinance:NS"}
    _store_records([revised, newer], db_path)

    with connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM prices").fetchone()[0] == 2
        row = conn.execute("SELECT close,source FROM prices WHERE trading_date='2026-09-29'").fetchone()
        assert row["close"] == 101.0
        assert row["source"] == "yfinance:NS"
        assert conn.execute("SELECT COUNT(*) FROM prices WHERE trading_date='2026-09-30'").fetchone()[0] == 1


def test_refresh_prices_is_incremental_and_does_not_delete_older_sessions(tmp_path):
    db_path = str(tmp_path / "prices.db")
    init_db(db_path)

    class Frame:
        empty = False
        def __init__(self, records): self.records = records
        def iterrows(self): return iter(self.records)

    def bar(day, close, volume=1_000):
        return (day, {"Open": close, "High": close + 1, "Low": close - 1,
                      "Close": close, "Adj Close": close, "Volume": volume})

    batches = [
        Frame([bar("2026-09-29", 100), bar("2026-09-30", 101)]),
        Frame([bar("2026-09-30", 102)]),
    ]
    for _ in range(2):
        result = refresh_prices(
            ["ABC"], db_path=db_path, request_interval=0, sleep=lambda _: None,
            history_loader=lambda _symbol: batches.pop(0),
        )
        assert result["tickers"]["ABC"]["status"] == "updated"

    with connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM prices WHERE ticker='ABC'").fetchone()[0] == 2
        assert conn.execute("SELECT close FROM prices WHERE trading_date='2026-09-29'").fetchone()[0] == 100
        assert conn.execute("SELECT close FROM prices WHERE trading_date='2026-09-30'").fetchone()[0] == 102


def test_fixture_has_sixty_deterministic_sessions_for_all_playbook_tickers(tmp_path):
    db_path = str(tmp_path / "prices.db")
    init_db(db_path)
    result = refresh_prices(DEFAULT_PORTFOLIO_TICKERS, offline=True, db_path=db_path)
    assert set(result["tickers"]) == set(DEFAULT_PORTFOLIO_TICKERS)
    assert all(row["status"] == "updated" and row["rows"] == 60 for row in result["tickers"].values())
    assert len(DEFAULT_PORTFOLIO_TICKERS) == 20


def test_invalid_tickers_are_rejected_without_provider_calls():
    with pytest.raises(ValueError, match="Invalid ticker"):
        normalize_ticker("BAD!")
    with pytest.raises(ValueError, match="Invalid ticker"):
        refresh_prices(["BAD!"], offline=True)


def test_anomalies_api_supports_ticker_thresholds_and_fixture_schema(monkeypatch):
    from fastapi.testclient import TestClient
    from app import main as main_module

    observed = {}

    def fake_refresh_anomalies(*, vol_x, pct, ticker):
        observed.update(vol_x=vol_x, pct=pct, ticker=ticker)
        rows = sessions(latest_volume=3_400, latest_close=105.2)
        return calculate_anomalies("RELIANCE", rows, vol_x=vol_x, pct=pct), datetime(2026, 10, 30, tzinfo=timezone.utc), True

    monkeypatch.setattr(main_module, "refresh_anomalies", fake_refresh_anomalies)
    monkeypatch.setattr(main_module, "price_data_source", lambda *, ticker=None: "fixture-csv")
    with TestClient(main_module.app) as client:
        response = client.get("/anomalies?ticker=RELIANCE&vol_x=3.2&pct=5")
        assert response.status_code == 200
        body = response.json()
        assert body["demo_mode"] is True
        assert body["data_source"] == "fixture-csv"
        assert body["as_of"] == "2026-10-30T00:00:00Z"
        assert {row["anomaly_type"] for row in body["anomalies"]} == {"volume_spike", "price_move"}
        assert observed == {"vol_x": 3.2, "pct": 5.0, "ticker": "RELIANCE"}
        invalid = client.get("/anomalies?ticker=BAD!")
        assert invalid.status_code == 422


def test_refresh_retries_rate_error_then_falls_back_to_bse(tmp_path):
    db_path = str(tmp_path / "prices.db")
    init_db(db_path)
    calls = []
    waits = []

    class HistoryFrame:
        empty = False

        def iterrows(self):
            return iter([("2026-09-30", {
                "Open": 100, "High": 102, "Low": 99, "Close": 101,
                "Adj Close": 101, "Volume": 1_200,
            })])

    def loader(symbol):
        calls.append(symbol)
        if symbol.endswith(".NS"):
            raise RuntimeError("rate limited")
        return HistoryFrame()

    result = refresh_prices(
        ["SAMPLE"], db_path=db_path, retries=2, request_interval=0,
        sleep=waits.append, history_loader=loader,
    )

    assert calls == ["SAMPLE.NS", "SAMPLE.NS", "SAMPLE.BO"]
    assert waits == [1]
    assert result["tickers"]["SAMPLE"]["symbol"] == "SAMPLE.BO"
    assert result["tickers"]["SAMPLE"]["rows"] == 1
    with connect(db_path) as conn:
        assert conn.execute("SELECT source FROM prices").fetchone()[0] == "yfinance:BO"


def test_yfinance_request_uses_configured_timeout(monkeypatch):
    import yfinance
    captured = {}

    class FakeData:
        def _get_cookie_and_crumb(self, *, timeout): captured["cookie_timeout"] = timeout

    class FakeTicker:
        def __init__(self, symbol):
            captured["symbol"] = symbol
            self._data = FakeData()
        def history(self, **kwargs): captured.update(kwargs); return []

    monkeypatch.setattr(yfinance, "Ticker", FakeTicker)
    monkeypatch.setenv("FINN_YFINANCE_TIMEOUT", "7")
    download_history("RELIANCE.NS")

    assert captured["symbol"] == "RELIANCE.NS"
    assert captured["cookie_timeout"] == 7
    assert captured["timeout"] == 7
