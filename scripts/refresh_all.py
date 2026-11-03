"""Refresh all market data for FINN portfolio: prices, announcements, and management changes.

Idempotent, prints a per-ticker summary table, and exits non-zero only if every source failed.
"""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import date, timedelta
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.db import connect, init_db, load_portfolio_config
from app.prices import refresh_prices
from app.announcements import ingest_announcements
from app.management_changes import process_management_changes

async def main_async() -> int:
    print("=" * 80)
    print("FINN REFRESH ALL DATA PIPELINE")
    print("=" * 80)
    
    # Ensure DB initialized & portfolio loaded
    init_db()
    load_portfolio_config()
    
    with connect() as conn:
        rows = conn.execute("SELECT ticker, name, sector FROM companies WHERE is_portfolio=1 ORDER BY ticker").fetchall()
        tickers = [r["ticker"] for r in rows]
        
    print(f"Loaded {len(tickers)} portfolio companies to refresh.")
    print("-" * 80)
    
    # 1. Refresh prices
    print("\n[1/3] Refreshing price history from Yahoo Finance (.NS / .BO)...")
    price_res = refresh_prices(tickers, retries=2, request_interval=0.5)
    price_reports = price_res.get("tickers", {})
    total_price_rows = price_res.get("updated", 0)
    print(f"Prices refreshed: {total_price_rows} rows stored across {len(price_reports)} tickers.")
    
    # 2. Refresh announcements
    lookback = int(os.getenv("ANNOUNCEMENT_LOOKBACK_DAYS", "30"))
    to_date = date.today()
    from_date = to_date - timedelta(days=lookback)
    print(f"\n[2/3] Ingesting exchange announcements (Lookback: {lookback} days: {from_date} to {to_date})...")
    
    ann_reports: dict[str, dict] = {}
    total_ann_rows = 0
    demo_mode = os.getenv("DEMO_MODE", "false").lower() in ("true", "1")
    
    for idx, ticker in enumerate(tickers, start=1):
        print(f"  [{idx:02d}/{len(tickers):02d}] Fetching announcements for {ticker}...", end=" ", flush=True)
        try:
            res = await ingest_announcements(
                ticker,
                from_date=from_date,
                to_date=to_date,
                demo_mode=demo_mode,
                fallback_to_fixture=demo_mode,
            )
            inserted = res.get("inserted", 0)
            received = res.get("received", 0)
            source = res.get("source", "none")
            ann_reports[ticker] = {
                "status": "ok" if received > 0 else "no_data",
                "source": source,
                "received": received,
                "inserted": inserted,
                "error": None,
            }
            total_ann_rows += received
            print(f"OK ({source}: {received} rec, {inserted} ins)")
        except Exception as exc:
            err_msg = str(exc)
            status = "no_mapping" if "mapping" in err_msg.casefold() else "failed"
            ann_reports[ticker] = {
                "status": status,
                "source": "none",
                "received": 0,
                "inserted": 0,
                "error": err_msg,
            }
            print(f"{status.upper()} ({err_msg})")
            
    # 3. Process management changes
    print("\n[3/3] Processing management changes from ingested announcements...")
    mgmt_res = process_management_changes()
    print(f"Management changes processed: {mgmt_res.get('scanned', 0)} scanned, {mgmt_res.get('inserted', 0)} new events inserted.")
    
    # Summary Table
    print("\n" + "=" * 90)
    print(f"{'TICKER':<12} | {'PRICE STATUS':<12} | {'PRICE ROWS':<10} | {'ANN STATUS':<12} | {'ANN ROWS':<10} | {'ANN SOURCE'}")
    print("-" * 90)
    
    with connect() as conn:
        for ticker in tickers:
            p_rep = price_reports.get(ticker, {})
            p_rows_in_db = conn.execute("SELECT COUNT(*) FROM prices WHERE ticker=? AND source NOT LIKE 'fixture%'", (ticker,)).fetchone()[0]
            p_status = p_rep.get("status", "ok" if p_rows_in_db > 0 else "missing")
            
            a_rep = ann_reports.get(ticker, {})
            a_rows_in_db = conn.execute("SELECT COUNT(*) FROM announcements WHERE ticker=? AND COALESCE(demo_data,0)=0 AND source != 'fixture'", (ticker,)).fetchone()[0]
            a_status = a_rep.get("status", "ok" if a_rows_in_db > 0 else "missing")
            a_source = a_rep.get("source", "none")
            
            print(f"{ticker:<12} | {p_status:<12} | {p_rows_in_db:<10} | {a_status:<12} | {a_rows_in_db:<10} | {a_source}")
            
    print("=" * 90)
    
    # Exit condition: exit non-zero only if every source failed across all tickers
    with connect() as conn:
        total_live_p = conn.execute("SELECT COUNT(*) FROM prices WHERE source NOT LIKE 'fixture%'").fetchone()[0]
        total_live_a = conn.execute("SELECT COUNT(*) FROM announcements WHERE COALESCE(demo_data,0)=0 AND source != 'fixture'").fetchone()[0]
        
    print(f"Total live prices stored: {total_live_p}")
    print(f"Total live announcements stored: {total_live_a}")
    
    if total_live_p == 0 and total_live_a == 0:
        print("\nERROR: All external data sources failed. Exiting with code 1.")
        return 1
        
    print("\nSUCCESS: Refresh complete with live market data stored.")
    return 0

def main():
    code = asyncio.run(main_async())
    sys.exit(code)

if __name__ == "__main__":
    main()

