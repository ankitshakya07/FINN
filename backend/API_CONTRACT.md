# FINN REST API contract (v0)

Base URL: `http://localhost:8000`. JSON timestamps are ISO-8601 UTC. All read responses include `as_of` and `demo_mode` where applicable. In demo mode, `as_of` is the fixture's frozen timestamp, not request time.

## `GET /digest?window=24h|3d|7d|custom`

Custom window additionally requires `from` and `to` ISO timestamps.

```json
{
  "window": "24h",
  "from_at": "2026-10-30T14:00:00Z",
  "to_at": "2026-10-31T14:00:00Z",
  "as_of": "2026-10-31T14:00:00Z",
  "demo_mode": true,
  "collapsed_count": 12,
  "items": [{
    "id": "filing-001",
    "ticker": "INFY",
    "company_name": "Example issuer",
    "kind": "filing",
    "category": "results",
    "headline": "Quarterly results approved",
    "summary": "Board approved quarterly results.",
    "priority": "high",
    "occurred_at": "2026-10-31T10:30:00Z",
    "citations": [{"document":"Q2 FY27 results filing","locator":"page 1","quote":"Revenue from operations ..."}]
  }]
}
```

## `GET /alerts`

```json
{
  "as_of": "2026-10-31T14:00:00Z",
  "demo_mode": true,
  "alerts": [{
    "id": "alert-001", "ticker": "INFY", "alert_type": "volume_spike",
    "title": "Unusual volume", "message": "Volume was 2.4× its 20-day average.",
    "triggered_at": "2026-10-31T10:00:00Z", "read": false
  }]
}
```

## `POST /alerts/config`

Request:

```json
{
  "ticker": "INFY",
  "enabled": true,
  "announcement_categories": ["results", "M&A", "management_change"],
  "price_move_pct": 3.0,
  "volume_multiple": 2.0,
  "notify_on_high_priority": true
}
```

Response:

```json
{
  "id": 1, "ticker": "INFY", "enabled": true,
  "announcement_categories": ["results", "M&A", "management_change"],
  "price_move_pct": 3.0, "volume_multiple": 2.0,
  "notify_on_high_priority": true, "updated_at": "2026-10-31T14:00:00Z"
}
```

## `GET /anomalies?vol_x=2.0&pct=3.0`

Both thresholds are positive request parameters. `vol_x` compares the latest
session's volume with the mean volume of the previous 20 sessions; `pct` is the
absolute close-to-previous-close percentage move. Either threshold can trigger
an anomaly. If both trigger, each returned record includes the combined
plain-English reason. The route evaluates stored `prices` rows and records the
latest generated anomalies in SQLite; it never contacts the quote provider.

```json
{
  "as_of": "2026-09-30T00:00:00Z",
  "demo_mode": true,
  "anomalies": [
    {
      "id": "price-anomaly:SAMPLE:2026-09-30:volume_spike", "ticker": "SAMPLE",
      "anomaly_type": "volume_spike", "observed_value": 3.4,
      "threshold_value": 2.0, "unit": "multiple",
      "detected_at": "2026-09-30T00:00:00Z",
      "explanation": "Volume 3.4x its 20-day average; price +5.2%"
    },
    {
      "id": "price-anomaly:SAMPLE:2026-09-30:price_move", "ticker": "SAMPLE",
      "anomaly_type": "price_move", "observed_value": 5.2,
      "threshold_value": 3.0, "unit": "percent",
      "detected_at": "2026-09-30T00:00:00Z",
      "explanation": "Volume 3.4x its 20-day average; price +5.2%"
    }
  ]
}
```

The `SAMPLE` values above come from the synthetic offline fixture, not a real issuer.

## `GET /announcements`

Returns stored announcements. Optional filters are `ticker`, `category` (one of
the taxonomy values), `min_materiality` (0–10), `limit` (1–500), and `offset`.
`GET /announcements/high-materiality` uses a default `min_materiality=5`.
Responses include `as_of`, `demo_mode`, `count`, and normalized announcement
records with the source identifier and raw source payload retained under
`raw_metadata`.

## `POST /announcements/refresh`

Request:

```json
{"ticker":"INFY","from_date":"2026-10-01","to_date":"2026-10-31"}
```

Date fields are optional; the default window is the preceding 30 calendar days.
The collector tries BSE using a cached verified BSE scrip mapping, falls back to
NSE, then to `data/fixtures/announcements.json`. Access denial (401/403) is
treated as a source failure and is not bypassed. Fixture responses have
`source="fixture"` and `demo_mode=true`. When application `DEMO_MODE=true`, this
route uses fixture data only and makes no exchange or model requests.
The response includes `as_of`; for fixture-only responses this is the fixture's
frozen timestamp.

Normalized records include `id`, `ticker`, UTC `timestamp`, `headline`,
`raw_category`, `attachment_url`, `source`, `source_identifier`, classification
and method/confidence, base/final materiality and reason, summary, and creation
time. Summaries are null below materiality 5.

The mapping refresh function is also available through
`python scripts/refresh_announcements.py --refresh-mappings`. It stores only
unambiguous mappings based on ISIN, explicit NSE symbol, or checked company-name
matching; an ambiguous name is reported and left unmapped.

## `GET /filing/{id}/card`

```json
{
  "id": "filing-001", "ticker": "INFY", "company_name": "Example issuer",
  "filed_at": "2026-10-31T10:30:00Z", "category": "results",
  "headline": "Quarterly results approved",
  "raw_url": "https://example.invalid/filing.pdf", "priority": "high",
  "summary": "The board approved quarterly results.",
  "key_points": ["Revenue and PAT disclosed."],
  "citations": [{"document":"Q2 FY27 results filing","locator":"page 1","quote":"..."}],
  "as_of": "2026-10-31T14:00:00Z", "demo_mode": true
}
```

## `POST /research` — Server-Sent Events

Request:

```json
{"ticker":"INFY","module":"financial_snapshot"}
```

Supported modules: `business_snapshot`, `financial_snapshot`, `trajectory`, `balance_sheet`, `cash_quality`, `narrative_vs_numbers`, `guidance`, `bull_vs_bear`.

Response content type: `text/event-stream`. Each event is `event: <name>` followed by a JSON `data:` line.

```text
event: progress
data: {"stage":"source_discovery","message":"Finding primary sources for INFY"}

event: progress
data: {"stage":"synthesis","message":"Preparing cited findings"}

event: result
data: {"ticker":"INFY","module":"financial_snapshot","status":"not_found","answer":"not found in sources","findings":[],"citations":[],"as_of":"2026-10-31T14:00:00Z","demo_mode":true}
```

The live implementation must discover only primary sources (annual reports, quarterly results, concall transcripts, investor presentations and screener.in financials). Every factual finding must include document + page/quarter + short quote. Unsupported fields must explicitly say `not found in sources`. Financial calculations are performed in code.

## `POST /ask`

Request:

```json
{"ticker":"INFY","question":"What did management guide for revenue growth?","conversation_id":"optional-thread-id"}
```

Response:

```json
{
  "ticker":"INFY", "answer":"not found in sources", "citations":[],
  "status":"not_found", "as_of":"2026-10-31T14:00:00Z", "demo_mode":true
}
```

Ask is ticker-scoped and evidence-grounded. No source means no answer beyond `not found in sources`.

## Error semantics

- `422`: invalid request/window.
- `404`: filing card unavailable; preserve/show raw filing URL when known.
- `5xx`: unexpected server fault; frontend should retain the last snapshot and show a retry affordance.
- Upstream scrape/parse failures: never fail the digest/research view; use cached snapshot/fixture, otherwise return an explicit empty/not-found state and raw source link when available.
