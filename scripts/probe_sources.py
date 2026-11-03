"""Probe external data sources for FINN (read-only, no DB writes).

Tests:
  (a) yfinance history for RELIANCE.NS, period 5d
  (b) BSE announcements call as in announcements.py for RELIANCE (scrip 500325)
  (c) NSE session warm + announcements call as in announcements.py for RELIANCE
  (d) BSE security master URL
"""

import sys
import time
from datetime import date, timedelta
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import httpx
import yfinance as yf
from app import announcements as ann

def probe_yfinance():
    print("--- [A] Probing yfinance (RELIANCE.NS, 5d) ---")
    start = time.perf_counter()
    status = "N/A"
    rows = 0
    error = None
    try:
        ticker = yf.Ticker("RELIANCE.NS")
        hist = ticker.history(period="5d", timeout=15)
        latency = time.perf_counter() - start
        rows = len(hist)
        status = 200 if rows > 0 else "EMPTY"
        print(f"Status: {status} | Rows: {rows} | Latency: {latency:.2f}s | Error: None")
        if rows > 0:
            print(f"Sample close: {hist['Close'].iloc[-1]:.2f} on {hist.index[-1].strftime('%Y-%m-%d')}")
        return {"source": "yfinance", "ok": rows > 0, "status": status, "rows": rows, "latency": latency, "error": None}
    except Exception as exc:
        latency = time.perf_counter() - start
        error = f"{type(exc).__name__}: {exc}"
        print(f"Status: ERROR | Rows: 0 | Latency: {latency:.2f}s | Error: {error}")
        return {"source": "yfinance", "ok": False, "status": "ERROR", "rows": 0, "latency": latency, "error": error}

def probe_bse():
    print("\n--- [B] Probing BSE Announcements (scrip 500325 - RELIANCE) ---")
    start = time.perf_counter()
    status = "N/A"
    rows = 0
    error = None
    to_date = date.today()
    from_date = to_date - timedelta(days=30)
    try:
        # Use fetch_bse_announcements directly
        found = ann.fetch_bse_announcements("500325", from_date, to_date, retries=1)
        latency = time.perf_counter() - start
        rows = len(found)
        status = 200
        print(f"Status: {status} | Rows: {rows} | Latency: {latency:.2f}s | Error: None")
        if rows > 0:
            sample_sub = ann._pick(found[0], "NEWSSUB", "NEWS_SUB", "HEADLINE")
            print(f"Sample headline: {str(sample_sub)[:80]}")
        return {"source": "BSE", "ok": True, "status": status, "rows": rows, "latency": latency, "error": None}
    except Exception as exc:
        latency = time.perf_counter() - start
        error = f"{type(exc).__name__}: {exc}"
        print(f"Status: ERROR | Rows: 0 | Latency: {latency:.2f}s | Error: {error}")
        return {"source": "BSE", "ok": False, "status": "ERROR", "rows": 0, "latency": latency, "error": error}

def probe_nse():
    print("\n--- [C] Probing NSE Announcements (RELIANCE) ---")
    start = time.perf_counter()
    status = "N/A"
    rows = 0
    error = None
    to_date = date.today()
    from_date = to_date - timedelta(days=30)
    try:
        found = ann.fetch_nse_announcements("RELIANCE", from_date, to_date, retries=1)
        latency = time.perf_counter() - start
        rows = len(found)
        status = 200
        print(f"Status: {status} | Rows: {rows} | Latency: {latency:.2f}s | Error: None")
        if rows > 0:
            sample_desc = ann._pick(found[0], "desc", "subject", "headline")
            print(f"Sample headline: {str(sample_desc)[:80]}")
        return {"source": "NSE", "ok": True, "status": status, "rows": rows, "latency": latency, "error": None}
    except Exception as exc:
        latency = time.perf_counter() - start
        error = f"{type(exc).__name__}: {exc}"
        print(f"Status: ERROR | Rows: 0 | Latency: {latency:.2f}s | Error: {error}")
        return {"source": "NSE", "ok": False, "status": "ERROR", "rows": 0, "latency": latency, "error": error}

def probe_bse_master():
    print("\n--- [D] Probing BSE Security Master URL ---")
    start = time.perf_counter()
    status = "N/A"
    rows = 0
    error = None
    try:
        url = ann.BSE_SECURITY_MASTER_URL
        headers = ann._BSE_HEADERS
        with httpx.Client(headers=headers, timeout=15) as client:
            resp = client.get(url)
            latency = time.perf_counter() - start
            status = resp.status_code
            if resp.status_code == 200:
                parsed = ann.parse_security_master(resp.content)
                rows = len(parsed)
                print(f"Status: {status} | Rows: {rows} | Latency: {latency:.2f}s | Error: None")
                return {"source": "BSE_MASTER", "ok": rows > 0, "status": status, "rows": rows, "latency": latency, "error": None}
            else:
                error = f"HTTP {resp.status_code}"
                print(f"Status: {status} | Rows: 0 | Latency: {latency:.2f}s | Error: {error}")
                return {"source": "BSE_MASTER", "ok": False, "status": status, "rows": 0, "latency": latency, "error": error}
    except Exception as exc:
        latency = time.perf_counter() - start
        error = f"{type(exc).__name__}: {exc}"
        print(f"Status: ERROR | Rows: 0 | Latency: {latency:.2f}s | Error: {error}")
        return {"source": "BSE_MASTER", "ok": False, "status": "ERROR", "rows": 0, "latency": latency, "error": error}

def main():
    print("FINN External Sources Probe")
    print("=" * 40)
    res_yf = probe_yfinance()
    res_bse = probe_bse()
    res_nse = probe_nse()
    res_master = probe_bse_master()
    
    print("\n" + "=" * 40)
    print("SUMMARY")
    print(f"yfinance:      {'OK' if res_yf['ok'] else 'FAILED'}")
    print(f"BSE Ann:       {'OK' if res_bse['ok'] else 'FAILED'}")
    print(f"NSE Ann:       {'OK' if res_nse['ok'] else 'FAILED'}")
    print(f"BSE Master:    {'OK' if res_master['ok'] else 'FAILED'}")
    print("=" * 40)
    
    if res_yf["ok"] and (res_bse["ok"] or res_nse["ok"]):
        print("DECISION: PROCEED (yfinance works and at least one announcement source works).")
    else:
        print("DECISION: STOP (required sources failed).")

if __name__ == "__main__":
    main()

