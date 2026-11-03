"""Refresh one ticker's announcements, or refresh the BSE security master."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.announcements import ingest_announcements, refresh_bse_mappings  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", help="NSE ticker to refresh")
    parser.add_argument("--from-date", type=date.fromisoformat)
    parser.add_argument("--to-date", type=date.fromisoformat)
    parser.add_argument("--offline", action="store_true", help="Use clearly marked fixture data only")
    parser.add_argument("--refresh-mappings", action="store_true", help="Refresh cached NSE-to-BSE mappings from BSE's security list")
    args = parser.parse_args()
    db_path = os.getenv("SQLITE_PATH", str(BACKEND / "finn.db"))

    if args.refresh_mappings:
        print(json.dumps(refresh_bse_mappings(db_path=db_path), ensure_ascii=False, indent=2))
    if args.ticker:
        end = args.to_date or date.today()
        start = args.from_date or end - timedelta(days=30)
        result = asyncio.run(ingest_announcements(
            args.ticker,
            from_date=start,
            to_date=end,
            db_path=db_path,
            demo_mode=args.offline,
        ))
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    elif not args.refresh_mappings:
        parser.error("provide --ticker, --refresh-mappings, or both")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
