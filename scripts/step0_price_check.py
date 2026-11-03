import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import yfinance as yf
from app.db import connect

print("=" * 80)
print("STEP 0.2: PRICE SANITY CHECK")
print("=" * 80)

# 1. Compare stored RELIANCE bars with fresh yfinance pull for 2026-10-30 and 2026-11-02
print("\n[A] Comparing Stored RELIANCE Bars vs Fresh yfinance Pull:")
with connect() as conn:
    stored_rows = conn.execute(
        "SELECT trading_date, close, volume, source, fetched_at FROM prices WHERE ticker='RELIANCE' ORDER BY trading_date DESC LIMIT 5"
    ).fetchall()

stored_by_date = {r["trading_date"]: r for r in stored_rows}

yf_ns = yf.Ticker("RELIANCE.NS").history(period="5d")
yf_bo = yf.Ticker("RELIANCE.BO").history(period="5d")

print(f"{'Date':<12} | {'Source':<15} | {'Stored Close':<14} | {'Stored Vol':<12} | {'Fresh Close':<14} | {'Fresh Vol':<12} | {'Match?'}")
print("-" * 95)

for dt_str in ["2026-10-30", "2026-11-02"]:
    stored = stored_by_date.get(dt_str)
    s_close = f"{stored['close']:.2f}" if stored else "N/A"
    s_vol = f"{stored['volume']:,}" if stored and stored["volume"] is not None else "N/A"
    
    # Check yf_ns
    fresh_close = "N/A"
    fresh_vol = "N/A"
    match_str = "NO DATA"
    
    for idx, row in yf_ns.iterrows():
        if idx.strftime("%Y-%m-%d") == dt_str:
            f_close_val = float(row["Close"])
            f_vol_val = int(row["Volume"])
            fresh_close = f"{f_close_val:.2f}"
            fresh_vol = f"{f_vol_val:,}"
            if stored:
                close_diff = abs(stored["close"] - f_close_val)
                match_str = "EXACT MATCH" if close_diff < 0.01 else f"CLOSE DIFF ({close_diff:.2f})"
            break
            
    print(f"{dt_str:<12} | {'RELIANCE.NS':<15} | {s_close:<14} | {s_vol:<12} | {fresh_close:<14} | {fresh_vol:<12} | {match_str}")

# Also show RELIANCE.BO for reference
for idx, row in yf_bo.iterrows():
    if idx.strftime("%Y-%m-%d") == "2026-11-02":
        print(f"{'2026-11-02':<12} | {'RELIANCE.BO':<15} | {'-':<14} | {'-':<12} | {float(row['Close']):<14.2f} | {int(row['Volume']):<12,} | BO Reference")

# 2. Print all 20 tickers: latest close, change %, volume ratio, date, flagging abs(change) > 8%
print("\n[B] Portfolio Overview (20 Tickers):")
print(f"{'Ticker':<12} | {'Date':<12} | {'Close':<10} | {'Prev Close':<10} | {'Change %':<10} | {'Vol Ratio':<10} | {'Flag (>8%)'}")
print("-" * 80)

with connect() as conn:
    comps = [r["ticker"] for r in conn.execute("SELECT ticker FROM companies WHERE is_portfolio=1 ORDER BY ticker").fetchall()]
    for ticker in comps:
        p_rows = conn.execute(
            "SELECT trading_date, close, volume FROM prices WHERE ticker=? ORDER BY trading_date ASC", (ticker,)
        ).fetchall()
        if not p_rows:
            print(f"{ticker:<12} | NO DATA")
            continue
            
        latest = p_rows[-1]
        prev = p_rows[-2] if len(p_rows) >= 2 else None
        
        latest_close = float(latest["close"])
        prev_close = float(prev["close"]) if prev else None
        change_pct = round(((latest_close - prev_close) / prev_close) * 100, 2) if prev_close else 0.0
        
        vol_ratio_str = "N/A"
        if len(p_rows) >= 22:
            prior_20 = [r["volume"] for r in p_rows[-21:-1]]
            if all(v is not None for v in prior_20) and latest["volume"] is not None:
                avg_vol = sum(prior_20) / 20.0
                if avg_vol > 0:
                    vol_ratio_str = f"{latest['volume'] / avg_vol:.2f}x"
                    
        flag = "FLAGGED (>8%)" if abs(change_pct) > 8.0 else ""
        print(f"{ticker:<12} | {latest['trading_date']:<12} | {latest_close:<10.2f} | {str(prev_close):<10} | {change_pct:<+10.2f} | {vol_ratio_str:<10} | {flag}")
