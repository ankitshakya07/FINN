from __future__ import annotations

import csv
import math
import os
import re
import time
from collections import defaultdict
from datetime import date, datetime, time as day_time, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from zoneinfo import ZoneInfo

from .db import connect

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parents[1]
DEFAULT_FIXTURE = ROOT_DIR / "data" / "fixtures" / "prices.csv"
TICKER_PATTERN = re.compile(r"^[A-Z0-9&._-]{1,24}$")
DEFAULT_PORTFOLIO_TICKERS = (
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "BAJFINANCE",
    "SUNPHARMA", "MARUTI", "M&M", "LT", "ITC", "HINDUNILVR", "TITAN", "TRENT",
    "APOLLOHOSP", "DIXON", "POLYCAB", "PERSISTENT", "SUZLON",
)


def normalize_ticker(value: str) -> str:
    """Return the canonical ticker without Yahoo's exchange suffix."""
    ticker = value.strip().upper()
    for suffix in (".NS", ".BO"):
        if ticker.endswith(suffix):
            ticker = ticker[: -len(suffix)]
            break
    if not TICKER_PATTERN.fullmatch(ticker):
        raise ValueError(f"Invalid ticker: {value!r}")
    return ticker


def _number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def calculate_anomalies(
    ticker: str,
    sessions: Iterable[Mapping[str, Any]],
    vol_x: float = 2.0,
    pct: float = 3.0,
) -> list[dict[str, Any]]:
    """Calculate latest-session volume and price anomalies.

    Volume compares the latest session with the 20 sessions immediately before it.
    A price anomaly compares the latest close with the immediately previous close.
    """
    if not math.isfinite(vol_x) or vol_x <= 0:
        raise ValueError("vol_x must be a finite number greater than zero")
    if not math.isfinite(pct) or pct <= 0:
        raise ValueError("pct must be a finite number greater than zero")

    rows = sorted(sessions, key=lambda row: str(row["trading_date"]))
    if len(rows) < 2:
        return []

    latest = rows[-1]
    previous = rows[-2]
    latest_volume = _number(latest.get("volume"))
    previous_volumes = [_number(row.get("volume")) for row in rows[-21:-1]]
    volume_ratio: float | None = None
    if (
        len(previous_volumes) == 20
        and latest_volume is not None
        and all(value is not None for value in previous_volumes)
    ):
        average_volume = sum(value for value in previous_volumes if value is not None) / 20
        if average_volume > 0:
            volume_ratio = latest_volume / average_volume

    latest_close = _number(latest.get("close"))
    previous_close = _number(previous.get("close"))
    pct_change: float | None = None
    if latest_close is not None and previous_close is not None and previous_close > 0:
        pct_change = (latest_close / previous_close - 1) * 100

    volume_triggered = volume_ratio is not None and volume_ratio >= vol_x
    price_triggered = pct_change is not None and abs(pct_change) >= pct
    if not volume_triggered and not price_triggered:
        return []

    reasons: list[str] = []
    if volume_triggered:
        reasons.append(f"Volume {volume_ratio:.1f}x its 20-day average")
    if price_triggered:
        reasons.append(f"price {pct_change:+.1f}%")
    reason = "; ".join(reasons)
    detected_at = str(latest["trading_date"])
    result: list[dict[str, Any]] = []
    if volume_triggered:
        result.append({
            "id": f"price-anomaly:{normalize_ticker(ticker)}:{detected_at}:volume_spike",
            "ticker": normalize_ticker(ticker),
            "anomaly_type": "volume_spike",
            "observed_value": volume_ratio,
            "threshold_value": vol_x,
            "unit": "multiple",
            "detected_at": detected_at,
            "explanation": reason,
        })
    if price_triggered:
        result.append({
            "id": f"price-anomaly:{normalize_ticker(ticker)}:{detected_at}:price_move",
            "ticker": normalize_ticker(ticker),
            "anomaly_type": "price_move",
            "observed_value": pct_change,
            "threshold_value": pct,
            "unit": "percent",
            "detected_at": detected_at,
            "explanation": reason,
        })
    return result


def _fixture_records(path: Path, tickers: set[str] | None = None) -> list[dict[str, Any]]:
    required = {"ticker", "trading_date", "close", "volume"}
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"Fixture CSV must contain columns: {', '.join(sorted(required))}")
        records: list[dict[str, Any]] = []
        for row in reader:
            ticker = normalize_ticker(row["ticker"])
            if tickers is not None and ticker not in tickers:
                continue
            trading_date = date.fromisoformat(row["trading_date"].strip()).isoformat()
            close = _number(row.get("close"))
            if close is None or close <= 0:
                raise ValueError(f"Invalid close for {ticker} on {trading_date}")
            records.append({
                "ticker": ticker,
                "trading_date": trading_date,
                "open": _number(row.get("open")),
                "high": _number(row.get("high")),
                "low": _number(row.get("low")),
                "close": close,
                "adjusted_close": _number(row.get("adjusted_close")),
                "volume": int(float(row["volume"])) if row.get("volume", "").strip() else None,
                "source": "fixture-csv",
            })
    return records


def _store_records(records: Iterable[Mapping[str, Any]], db_path: str | None = None) -> int:
    rows = list(records)
    if not rows:
        return 0
    with connect(db_path) as conn:
        for ticker in sorted({str(row["ticker"]) for row in rows}):
            conn.execute(
                "INSERT INTO companies(ticker, name) VALUES(?, ?) ON CONFLICT(ticker) DO NOTHING",
                (ticker, ticker),
            )
        for row in rows:
            existing = conn.execute(
                """SELECT id FROM prices WHERE ticker=? AND trading_date=?
                   ORDER BY CASE WHEN source=? THEN 0 ELSE 1 END,
                            CASE WHEN source='yfinance:NS' THEN 2
                                 WHEN source='yfinance:BO' THEN 1 ELSE 0 END DESC, id LIMIT 1""",
                (row["ticker"], row["trading_date"], row["source"]),
            ).fetchone()
            if existing:
                # Treat (ticker, date) as the logical key even though the legacy
                # table's unique key also includes source. Update the existing
                # row in place so fallback-source changes cannot add duplicates
                # or remove historical rows.
                conn.execute(
                    """UPDATE prices SET open=:open,high=:high,low=:low,close=:close,
                       adjusted_close=:adjusted_close,volume=:volume,source=:source,
                       fetched_at=CURRENT_TIMESTAMP WHERE id=:id""",
                    {**row, "id": existing["id"]},
                )
            else:
                conn.execute(
                    """INSERT INTO prices
                       (ticker,trading_date,open,high,low,close,adjusted_close,volume,source)
                       VALUES (:ticker,:trading_date,:open,:high,:low,:close,:adjusted_close,:volume,:source)
                       ON CONFLICT(ticker,trading_date,source) DO UPDATE SET
                         open=excluded.open,high=excluded.high,low=excluded.low,close=excluded.close,
                         adjusted_close=excluded.adjusted_close,volume=excluded.volume,
                         fetched_at=CURRENT_TIMESTAMP""",
                    row,
                )
    return len(rows)


def _fixture_refresh(
    tickers: Iterable[str] | None,
    fixture_path: str | Path,
    db_path: str | None,
) -> dict[str, Any]:
    requested = {normalize_ticker(ticker) for ticker in tickers} if tickers else None
    records = _fixture_records(Path(fixture_path), requested)
    _store_records(records, db_path)
    found = {row["ticker"] for row in records}
    requested = requested or found
    results = {
        ticker: {
            "status": "updated" if ticker in found else "missing",
            "source": "fixture-csv",
            "rows": sum(1 for row in records if row["ticker"] == ticker),
        }
        for ticker in sorted(requested)
    }
    return {"updated": len(records), "tickers": results}


def download_history(symbol: str) -> Any:
    """Download daily EOD history for a single Yahoo Finance symbol."""
    import yfinance as yf

    try:
        timeout = float(os.getenv("FINN_YFINANCE_TIMEOUT", "15"))
    except ValueError:
        timeout = 15.0
    if not math.isfinite(timeout) or timeout <= 0:
        timeout = 15.0

    ticker_client = yf.Ticker(symbol)
    # yfinance's chart request honors `timeout`, but its first cookie/crumb
    # handshake otherwise uses its own 30-second default. Prime it explicitly
    # when the installed yfinance version exposes that hook.
    data_client = getattr(ticker_client, "_data", None)
    cookie_handshake = getattr(data_client, "_get_cookie_and_crumb", None)
    if callable(cookie_handshake):
        cookie_handshake(timeout=timeout)

    return ticker_client.history(
        period="3mo", interval="1d", auto_adjust=False, actions=False,
        prepost=False, raise_errors=True, timeout=timeout,
    )


def _frame_records(frame: Any, ticker: str, source: str) -> list[dict[str, Any]]:
    if frame is None or getattr(frame, "empty", True):
        return []
    records = []
    for index, row in frame.iterrows():
        values = {str(key).casefold(): value for key, value in row.items()}
        close = _number(values.get("close"))
        if close is None or close <= 0:
            continue
        session_date = index.date() if hasattr(index, "date") else date.fromisoformat(str(index)[:10])
        records.append({
            "ticker": ticker,
            "trading_date": session_date.isoformat(),
            "open": _number(values.get("open")),
            "high": _number(values.get("high")),
            "low": _number(values.get("low")),
            "close": close,
            "adjusted_close": _number(values.get("adj close")),
            "volume": int(values["volume"]) if _number(values.get("volume")) is not None else None,
            "source": source,
        })

    india_now = datetime.now(ZoneInfo("Asia/Kolkata"))
    if india_now.time() < day_time(16, 0):
        records = [row for row in records if row["trading_date"] < india_now.date().isoformat()]
    return records


def _portfolio_tickers(db_path: str | None = None) -> list[str]:
    with connect(db_path) as conn:
        configured = [row[0] for row in conn.execute(
            "SELECT ticker FROM companies WHERE is_portfolio=1 ORDER BY ticker"
        ).fetchall()]
    return sorted(set(DEFAULT_PORTFOLIO_TICKERS).union(configured))


def refresh_prices(
    tickers: Iterable[str] | None = None,
    *,
    offline: bool = False,
    fixture_path: str | Path = DEFAULT_FIXTURE,
    db_path: str | None = None,
    retries: int = 3,
    request_interval: float = 1.0,
    sleep: Callable[[float], None] = time.sleep,
    history_loader: Callable[[str], Any] = download_history,
) -> dict[str, Any]:
    """Refresh about 60 sessions, preferring NSE and falling back to BSE."""
    if retries < 1:
        raise ValueError("retries must be at least 1")
    if not math.isfinite(request_interval) or request_interval < 0:
        raise ValueError("request_interval must be finite and non-negative")
    requested = [normalize_ticker(ticker) for ticker in tickers] if tickers else None
    if offline:
        return _fixture_refresh(requested, fixture_path, db_path)
    requested = requested or _portfolio_tickers(db_path)
    if not requested:
        raise ValueError("No tickers supplied and no companies are marked is_portfolio=1")

    reports: dict[str, dict[str, Any]] = {}
    total = 0
    last_request = 0.0
    for ticker in dict.fromkeys(requested):
        saved: list[dict[str, Any]] = []
        used_symbol: str | None = None
        errors: list[str] = []
        for suffix in ("NS", "BO"):
            symbol = f"{ticker}.{suffix}"
            for attempt in range(retries):
                delay = request_interval - (time.monotonic() - last_request)
                if last_request and delay > 0:
                    sleep(delay)
                try:
                    frame = history_loader(symbol)
                    last_request = time.monotonic()
                    saved = _frame_records(frame, ticker, f"yfinance:{suffix}")
                    if saved:
                        used_symbol = symbol
                        break
                    errors.append(f"{symbol}: no price history returned")
                    break
                except Exception as exc:  # provider errors vary between versions
                    last_request = time.monotonic()
                    errors.append(f"{symbol} attempt {attempt + 1}: {exc}")
                    if attempt + 1 < retries:
                        sleep(min(2 ** attempt, 30))
            if saved:
                break
        if saved:
            count = _store_records(saved, db_path)
            total += count
            reports[ticker] = {
                "status": "updated",
                "symbol": used_symbol,
                "rows": count,
                "rows_written": count,
                "error": None,
            }
        else:
            reports[ticker] = {
                "status": "missing",
                "symbol": None,
                "rows": 0,
                "rows_written": 0,
                "errors": errors,
                "error": "; ".join(errors) if errors else "No price history returned",
            }
    return {"updated": total, "tickers": reports}


def refresh_anomalies(
    vol_x: float = 2.0,
    pct: float = 3.0,
    *,
    db_path: str | None = None,
    ticker: str | None = None,
    exclude_fixtures: bool = False,
) -> tuple[list[dict[str, Any]], datetime, bool]:
    """Calculate and persist the latest price-derived anomalies per ticker."""
    if not math.isfinite(vol_x) or vol_x <= 0:
        raise ValueError("vol_x must be a finite number greater than zero")
    if not math.isfinite(pct) or pct <= 0:
        raise ValueError("pct must be a finite number greater than zero")
    with connect(db_path) as conn:
        stored_all = conn.execute(
            """SELECT ticker, trading_date, open, high, low, close, adjusted_close, volume, source
               FROM prices
               ORDER BY ticker, trading_date,
               CASE WHEN source='yfinance:NS' THEN 2
                    WHEN source='yfinance:BO' THEN 1 ELSE 0 END"""
        ).fetchall()
        if exclude_fixtures:
            stored_all = [row for row in stored_all if not str(row["source"]).startswith("fixture")]
        requested = normalize_ticker(ticker) if ticker else None
        stored = [row for row in stored_all if requested is None or row["ticker"] == requested]
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        # If a fixture and live response share a date, prefer the live row.
        for row in stored:
            item = dict(row)
            if grouped[item["ticker"]] and grouped[item["ticker"]][-1]["trading_date"] == item["trading_date"]:
                grouped[item["ticker"]][-1] = item
            else:
                grouped[item["ticker"]].append(item)

        anomalies: list[dict[str, Any]] = []
        for ticker, sessions in grouped.items():
            current = calculate_anomalies(ticker, sessions, vol_x=vol_x, pct=pct)
            anomalies.extend(current)
            conn.executemany(
                """INSERT INTO anomalies
                   (id,ticker,anomaly_type,observed_value,threshold_value,unit,detected_at,explanation,source_price_date)
                   VALUES (:id,:ticker,:anomaly_type,:observed_value,:threshold_value,:unit,:detected_at,:explanation,:detected_at)
                   ON CONFLICT(id) DO UPDATE SET observed_value=excluded.observed_value,
                     threshold_value=excluded.threshold_value,unit=excluded.unit,
                     detected_at=excluded.detected_at,explanation=excluded.explanation,
                     source_price_date=excluded.source_price_date""",
                current,
            )

        latest_session = max((row["trading_date"] for row in stored), default=None)
        # Conservatively label mixed fixture/live responses as demo so the API
        # never implies every returned record is live market data.
        is_demo = not stored or any(row["source"].startswith("fixture") for row in stored)
        if not stored and stored_all:
            # Empty ticker filters still describe the frozen database snapshot.
            latest_session = max(row["trading_date"] for row in stored_all)
        as_of = (
            datetime.combine(date.fromisoformat(latest_session), day_time.min, tzinfo=timezone.utc)
            if latest_session else datetime.now(timezone.utc)
        )
        return anomalies, as_of, is_demo


def price_data_source(
    *, ticker: str | None = None, db_path: str | None = None
) -> str:
    """Describe the stored price source without implying fixture data is live."""
    requested = normalize_ticker(ticker) if ticker else None
    with connect(db_path) as conn:
        if requested:
            rows = conn.execute(
                "SELECT DISTINCT source FROM prices WHERE ticker=?", (requested,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT DISTINCT source FROM prices").fetchall()
    sources = {str(row["source"]) for row in rows}
    if not sources:
        return "none"
    has_fixture = any(source.startswith("fixture") for source in sources)
    has_live = any(source.startswith("yfinance:") for source in sources)
    if has_fixture and has_live:
        return "mixed"
    if has_fixture:
        return "fixture-csv"
    if has_live:
        return "yfinance"
    return "mixed"
