import sys
import json
import time
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import httpx
from app.announcements import _managed_client, _get_with_retries, _NSE_HEADERS, NSE_HOME_URL
from app.results_card import download_pdf

print("=" * 80)
print("STEP 0.5 (a): PDF DOWNLOAD PROBE (3 Real Results Filings)")
print("=" * 80)

filings = [
    ("RELIANCE", "https://nsearchives.nseindia.com/corporate/kavinavora_30102026193935_SE_30102026_Results.pdf"),
    ("BAJFINANCE", "https://nsearchives.nseindia.com/corporate/BAJFINANCE_19102026172017_BMOutcome_19102026.pdf"),
    ("DIXON", "https://nsearchives.nseindia.com/corporate/DIXON_30102026160547_Outcome30102026.pdf"),
]

for ticker, url in filings:
    print(f"\nProbing download for {ticker} ({url})...")
    # Test using results_card download_pdf
    try:
        start_t = time.time()
        # Direct request probe first for content-type and headers
        headers = {**_NSE_HEADERS, "Accept": "application/pdf,*/*"}
        with httpx.Client(timeout=30.0, follow_redirects=True, headers=headers) as client:
            resp = client.get(url)
            latency = time.time() - start_t
            status = resp.status_code
            c_type = resp.headers.get("content-type", "unknown")
            size = len(resp.content)
            is_pdf = resp.content.startswith(b"%PDF-")
            print(f"  HTTP Status: {status}")
            print(f"  Content-Type: {c_type}")
            print(f"  Size: {size:,} bytes")
            print(f"  Starts with %PDF-: {is_pdf}")
            print(f"  Latency: {latency:.2f}s")
            
        # Also test download_pdf function caching
        target_path, sha256_hash = download_pdf(url)
        print(f"  Cached to: {target_path.name} (SHA-256: {sha256_hash[:16]}...)")
    except Exception as exc:
        print(f"  Download FAILED: {exc}")

print("\n" + "=" * 80)
print("STEP 0.5 (b): NSE STRUCTURED RESULTS ENDPOINT PROBE (RELIANCE)")
print("=" * 80)

# Call NSE's corporates-financial-results endpoint using session handling
managed, owned = _managed_client(None, _NSE_HEADERS, 15.0)
try:
    print("Warming NSE session at home URL...")
    warm = _get_with_retries(managed, NSE_HOME_URL, headers=_NSE_HEADERS, retries=2)
    print(f"Session warm status: {warm.status_code}")
    
    # Endpoints used by NSE for corporate financial results
    # 1. /api/corporates-financial-results
    endpoints = [
        ("https://www.nseindia.com/api/corporates-financial-results", {"index": "equities", "symbol": "RELIANCE"}),
        ("https://www.nseindia.com/api/financial-results", {"index": "equities", "symbol": "RELIANCE"}),
    ]
    
    for url, params in endpoints:
        print(f"\nCalling {url} with params {params}...")
        try:
            resp = managed.get(url, params=params, headers=_NSE_HEADERS)
            print(f"Status: {resp.status_code}")
            print(f"Content-Type: {resp.headers.get('content-type')}")
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if isinstance(data, list) and data:
                        first_row = data[0]
                        print("Returned rows count:", len(data))
                        print("Sample field names:", list(first_row.keys()) if isinstance(first_row, dict) else type(first_row))
                        print("Sample row preview:", json.dumps(first_row, indent=2)[:500])
                    elif isinstance(data, dict):
                        print("Dict keys:", list(data.keys()))
                        print("Dict preview:", json.dumps(data, indent=2)[:500])
                    else:
                        print("Response data:", data)
                except Exception as e:
                    print("Could not parse JSON:", e, resp.text[:200])
            else:
                print("Response text preview:", resp.text[:200])
        except Exception as exc:
            print("Request failed:", exc)
finally:
    if owned:
        managed.close()

