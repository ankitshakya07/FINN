from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
os.environ.setdefault("SQLITE_PATH", str(ROOT_DIR / "backend" / "finn.db"))
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.db import init_db  # noqa: E402
from app.prices import DEFAULT_FIXTURE, DEFAULT_PORTFOLIO_TICKERS, refresh_prices  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refresh about 60 daily NSE price sessions (BSE fallback) or import offline fixture data."
    )
    parser.add_argument("--tickers", nargs="+", help="NSE tickers (without .NS); defaults to the 20 FINN portfolio companies")
    parser.add_argument("--offline", action="store_true", help="Read the local fixture CSV instead of contacting Yahoo Finance")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE, help="Offline price fixture CSV")
    parser.add_argument("--retries", type=int, default=3, help="Attempts per Yahoo symbol before trying the BSE fallback")
    parser.add_argument("--request-interval", type=float, default=1.0, help="Minimum seconds between Yahoo requests")
    args = parser.parse_args()

    try:
        init_db()
        result = refresh_prices(
            args.tickers or DEFAULT_PORTFOLIO_TICKERS,
            offline=args.offline,
            fixture_path=args.fixture,
            retries=args.retries,
            request_interval=args.request_interval,
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if any(item["status"] == "missing" for item in result["tickers"].values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
