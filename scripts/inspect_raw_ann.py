import sys, json
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))
from app.db import connect

with connect() as conn:
    rows = conn.execute("SELECT ticker, headline, raw_metadata_json FROM announcements WHERE headline LIKE '%Outcome%' LIMIT 3").fetchall()
    for r in rows:
        meta = json.loads(r["raw_metadata_json"])
        print(f"=== {r['ticker']}: {r['headline']} ===")
        print(json.dumps(meta, indent=2))

