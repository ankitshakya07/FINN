import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from collections import Counter
from app.db import connect

print("=" * 80)
print("STEP 0.3: ANNOUNCEMENT COVERAGE CHECK")
print("=" * 80)

with connect() as conn:
    rows = conn.execute(
        """SELECT a.ticker, a.timestamp, a.headline, a.classification, a.attachment_url, a.source, a.demo_data
           FROM announcements a
           WHERE COALESCE(a.demo_data, 0)=0 AND a.source != 'fixture'
           ORDER BY a.ticker, a.timestamp DESC"""
    ).fetchall()

by_ticker: dict[str, list] = {}
for r in rows:
    by_ticker.setdefault(r["ticker"], []).append(r)

print(f"{'Ticker':<12} | {'Count':<6} | {'Min Timestamp':<20} | {'Max Timestamp':<20} | {'With PDF':<8} | {'Results':<8} | {'Categories'}")
print("-" * 115)

for ticker in sorted(by_ticker.keys()):
    t_rows = by_ticker[ticker]
    count = len(t_rows)
    timestamps = [r["timestamp"] for r in t_rows if r["timestamp"]]
    min_ts = min(timestamps)[:19] if timestamps else "N/A"
    max_ts = max(timestamps)[:19] if timestamps else "N/A"
    with_att = sum(1 for r in t_rows if r["attachment_url"])
    results_cnt = sum(1 for r in t_rows if r["classification"] == "results")
    cats = Counter(r["classification"] for r in t_rows)
    cat_summary = ", ".join(f"{k}:{v}" for k, v in cats.most_common(3))
    
    print(f"{ticker:<12} | {count:<6} | {min_ts:<20} | {max_ts:<20} | {with_att:<8} | {results_cnt:<8} | {cat_summary}")

print(f"\nTotal Live Announcements: {len(rows)}")
print(f"Total with Attachments: {sum(1 for r in rows if r['attachment_url'])}")
print(f"Total in 'results' Category: {sum(1 for r in rows if r['classification'] == 'results')}")

