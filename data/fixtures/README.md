# Frozen demo fixtures

Place deterministic JSON fixtures here. Each fixture should carry an explicit `as_of` timestamp.

Expected initial files:
- `digest.json` — `{ "as_of": "...", "items": [], "collapsed_count": 0 }`
- `alerts.json` — `{ "as_of": "...", "alerts": [] }`
- `anomalies.json` — `{ "as_of": "...", "anomalies": [] }`
- `filings.json` — `{ "items": [] }`
- `research_<TICKER>_<MODULE>.json` — `ResearchResult` response.

Use synthetic/sample data only when clearly labelled. Do not fabricate company facts or citations.

`prices.csv` contains deterministic, explicitly synthetic OHLCV rows for each of
the 20 FINN portfolio tickers (60 weekday sessions through 2026-10-30), plus the
`SAMPLE` series used by tests. The latest RELIANCE and TCS sessions intentionally
demonstrate a volume spike and a price move. Import with
`python scripts/refresh_prices.py --offline`; rows are tagged `fixture-csv` in
SQLite and must not be presented as live market data. The fixture snapshot is
frozen at 2026-10-30.

`announcements.json` contains 34 synthetic examples covering the announcement
taxonomy. Its root `demo_data` flag and every row's `demo_data` metadata flag are
true; the names and notices are not claims about real issuers or filings.
