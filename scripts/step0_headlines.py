import sys, json
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))
from app.db import connect

with connect() as conn:
    rows = conn.execute("SELECT ticker, headline, raw_metadata_json, attachment_url FROM announcements WHERE COALESCE(demo_data,0)=0").fetchall()

print(f"Total live announcements: {len(rows)}")

items = []
for r in rows:
    meta = json.loads(r["raw_metadata_json"])
    att_text = meta.get("attchmntText") or meta.get("desc") or ""
    att_file = r["attachment_url"] or meta.get("attchmntFile") or ""
    ext = Path(att_file.split("?")[0]).suffix.lower() if att_file else "none"
    items.append({
        "ticker": r["ticker"],
        "headline": r["headline"],
        "desc_preview": att_text[:90].replace("\n", " "),
        "ext": ext,
        "url": att_file
    })

# Print 40 sample diverse headlines
print("\n=== SAMPLE 40 HEADLINES (Ticker | Headline | Extension | Detail Preview) ===")
for i, item in enumerate(items[:40], 1):
    print(f"{i:02d}. {item['ticker']:<10} | {item['headline'][:35]:<35} | {item['ext']:<5} | {item['desc_preview']}")

# Search specifically for RELIANCE results
print("\n=== RELIANCE RESULTS SEARCH ===")
reliance_results = [
    it for it in items if it["ticker"] == "RELIANCE" and any(k in (it["headline"] + " " + it["desc_preview"]).lower() for k in ["result", "financial", "outcome", "board meeting"])
]
for rr in reliance_results:
    print("RELIANCE candidate:", rr["headline"], "| URL:", rr["url"])
    print("  Detail:", rr["desc_preview"])

