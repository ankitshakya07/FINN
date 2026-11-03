# FINN — Investment Intelligence Platform

A mobile-first investment intelligence application for Indian stock markets (NSE/BSE), combining corporate announcements, market anomalies, financial research, and AI-powered insights.

---

## 1. Overview

FINN is engineered to provide institutional-grade intelligence on Indian equities for retail and professional investors. Rather than serving generic stock market dashboards or delayed newsfeeds, FINN synthesizes exchange filings, abnormal price/volume movements, quarterly corporate results, and management shifts into four core mobile-first experiences:

1. **Brief Feed**: A prioritized, ranked investment intelligence feed grouping corporate disclosures, financial events, and price-volume anomalies.
2. **Watch & Signals**: Real-time portfolio monitoring showing live quotes, 20-day volume multiples, close-to-close change percentages, and threshold-sensitive signal alerts.
3. **Research Hub**: Deep fundamentals, capital commitments tracking (promised vs. delivered), and structured quarterly results.
4. **Ask AI**: An AI-powered research assistant providing grounded, citation-backed answers on covered equities.

FINN can run entirely offline with **synthetic demo fixtures** (`DEMO_MODE=true`) or connected to **genuine live market sources** (`DEMO_MODE=false`).

---

## 2. Main Application Features

- **Ranked Intelligence Digest (`/digest`)**: Ranks disclosures by materiality score (0–10), category impact, recency, and portfolio priority, collapsing routine compliances.
- **Anomaly Detection (`/anomalies`)**: Detects price moves beyond configurable percentage thresholds (`pct`) and volume spikes against trailing 20-session averages (`vol_x`).
- **Signal Alerts (`/alerts`)**: Evaluates real alerts from stored anomalies and exchange announcements against per-ticker user configurations in `alert_config`.
- **Live Portfolio Spine (`/portfolio`)**: Tracks 20 major NSE equities with automated stale detection (>4 calendar days tolerance for weekends and market holidays).
- **Exchange Announcement Ingestion**: Ingests disclosures from National Stock Exchange (NSE) feeds with automatic deduplication, fingerprinting, and taxonomy classification.
- **Leadership Tracking (`/management-changes`)**: Detects executive appointments, resignations, and retirements with designation extraction and materiality scoring.
- **Corporate Commitments (`/commitments`)**: Audits executive guidance and capital allocation promises against subsequent delivery assessments.
- **Responsive Mobile Navigation**: Touch-optimized interface designed for standard 390px mobile viewports (iPhone/Android) with zero horizontal overflow.

---

## 3. Technology Stack

- **Backend**:
  - Python 3.11+ / 3.12
  - FastAPI (ASGI REST framework)
  - SQLite 3 (with foreign key enforcement and additive schema migrations)
  - Pydantic v2 (Schema validation and serialization)
  - PyMuPDF (`fitz`) & `pdfplumber` (Document and table extraction)
  - `httpx` & `curl_cffi` (Exchange integration & resilient HTTP)
  - `yfinance` (NSE/BSE historical & daily bar retrieval)
- **Frontend**:
  - Next.js 15 (React 19, App Router)
  - TypeScript 5
  - Tailwind CSS 3
  - Framer Motion (Mobile transitions and gesture handling)
  - Progressive Web App (PWA) manifest
- **AI & Reasoning**:
  - OpenAI-compatible chat completion interface
  - Support for Google Gemini (Free tier) or OpenAI models
  - Content-addressed SHA-256 caching (`llm_cache` table)
  - Tiered model orchestration (`small` high-volume vs. `strong` reasoning)

---

## 4. Repository Structure

```text
finn/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── announcements.py       # NSE/BSE announcements fetch, classification, deduplication
│   │   ├── ask.py                 # Multi-turn conversational research assistant
│   │   ├── db.py                  # SQLite schema, connection pool, and additive migrations
│   │   ├── digest.py              # Intelligent ranking and event collapsing algorithm
│   │   ├── fundamentals.py        # Financial statements and quarterly balance sheet ingestion
│   │   ├── llm.py                 # LLM client with token tracking, caching, and rate limiting
│   │   ├── main.py                # FastAPI routes, lifecycle handlers, and error handlers
│   │   ├── management_changes.py  # Executive appointment/resignation extractor
│   │   ├── prices.py              # Yahoo Finance OHLCV ingest and anomaly maths
│   │   ├── promised_vs_delivered.py # Corporate commitments audit engine
│   │   ├── research.py            # Synthesis engine for financial research modules
│   │   ├── results_card.py        # PDF parser and quarterly results statement extractor
│   │   └── schemas.py             # Pydantic models and request/response validation
│   ├── tests/                     # 170+ unit and integration tests (pytest)
│   ├── .env.example               # Backend environment template
│   ├── API_CONTRACT.md            # Complete REST API specification
│   ├── DEPENDENCY_MANIFEST.md     # Dependency manifest and versions
│   ├── Dockerfile                 # Backend container definition
│   └── requirements.txt           # Python package requirements
├── frontend/
│   ├── app/                       # Next.js App Router pages and sections
│   │   ├── brief-feed.tsx         # Mobile brief intelligence feed
│   │   ├── watch-section.tsx      # Portfolio watch table with live quotes & alerts
│   │   ├── research-hub.tsx       # Research hub container
│   │   ├── ask-section.tsx        # Ask AI interactive interface
│   │   ├── mobile-bottom-nav.tsx  # Mobile bottom tab navigation
│   │   ├── globals.css            # Tailwind styles and theme tokens
│   │   └── layout.tsx             # Root layout and metadata
│   ├── src/lib/
│   │   ├── api.ts                 # Type-safe API client
│   │   └── types.ts               # TypeScript data interfaces
│   ├── .env.example               # Frontend environment template
│   ├── package.json               # Node.js dependencies and scripts
│   └── tsconfig.json              # TypeScript compiler configuration
├── data/
│   ├── fixtures/                  # Frozen synthetic demo datasets (commitments, announcements, fundamentals, prices)
│   ├── snapshots/                 # Precomputed company research snapshots
│   └── portfolio.json             # Active portfolio definition (20 NSE companies)
├── prompts/                       # LLM extraction and research synthesis prompts
├── scripts/                       # Maintenance, probe, and ingestion scripts
│   ├── probe_sources.py           # Connectivity probe for Yahoo Finance, BSE, and NSE
│   ├── refresh_all.py             # Full market data ingest pipeline
│   ├── refresh_prices.py          # Daily OHLCV price refresher
│   ├── capture_screenshots.py     # Mobile Playwright viewport verification
│   └── verify_anomalies.py        # Independent anomaly math verification
├── docker-compose.yml             # Local multi-container orchestration
├── .gitignore                     # Git ignore rules
├── .env.example                   # Root environment template
└── README.md                      # Project documentation
```

---

## 5. Prerequisites

- **Python**: 3.11 or 3.12
- **Node.js**: 18.18+ or 20+
- **npm**: 9+
- **Git**: 2.30+
- Modern Web Browser (Chrome, Edge, Safari, or Firefox)

---

## 6. Backend Setup Instructions

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # On macOS/Linux:
   python3 -m venv .venv
   source .venv/bin/activate

   # On Windows (PowerShell):
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create local environment configuration:
   ```bash
   cp .env.example .env
   ```

5. Initialize the SQLite database and seed initial portfolio definitions:
   ```bash
   python -m app.db
   ```

---

## 7. Frontend Setup Instructions

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Create local frontend environment configuration:
   ```bash
   cp .env.example .env.local
   ```

---

## 8. Environment Configuration

### Backend Configuration (`backend/.env` or root `.env`)

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `APP_ENV` | `development` | Runtime environment (`development`, `production`, `test`) |
| `DEMO_MODE` | `true` | When `true`, uses frozen offline fixtures; when `false`, serves live database data |
| `DATABASE_URL` | `sqlite:///./finn.db` | Path to SQLite database file |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed origins for cross-origin resource sharing |
| `ANNOUNCEMENT_LOOKBACK_DAYS` | `30` | Trailing window (in days) for exchange announcement ingestion |
| `REFRESH_STALE_HOURS` | `12` | Age threshold after which prices/announcements are auto-refreshed |
| `LLM_BASE_URL` | `https://api.openai.com/v1` | OpenAI-compatible chat completions endpoint URL |
| `LLM_API_KEY` | *(empty)* | API key for LLM provider (OpenAI or Google Gemini) |
| `LLM_SMALL_MODEL` | `gpt-4o-mini` | High-throughput model for extraction and classification |
| `LLM_STRONG_MODEL` | `gpt-4o` | Deep reasoning model for synthesis and complex extraction |

### Frontend Configuration (`frontend/.env.local`)

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Root URL of the FINN FastAPI backend server |

---

## 9. How to Start the Backend

From the `backend/` directory (with `.venv` activated):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify backend health:
```bash
curl http://localhost:8000/health
```

---

## 10. How to Start the Frontend

From the `frontend/` directory:

```bash
# Start Next.js development server
npm run dev

# Or run optimized production build
npm run build
npm start
```

Access the application in your browser at: **`http://localhost:3000`**

---

## 11. API Documentation URL

Interactive OpenAPI / Swagger documentation is automatically generated by FastAPI:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI Schema**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## 12. Demo Mode Instructions

To run FINN entirely offline without external API access or exchange scraping:

1. In your `.env`, set:
   ```env
   DEMO_MODE=true
   ```

2. Initialize the database:
   ```bash
   python -m app.db
   ```

3. Start backend (`uvicorn app.main:app --port 8000`) and frontend (`npm run dev`).
   - The UI will display a **DEMO** mode badge.
   - All tabs read from deterministic synthetic fixtures in `data/fixtures/` (`announcements.json`, `fundamentals.json`, `commitments.json`, `prices.csv`).
   - Zero outbound requests to NSE, BSE, or Yahoo Finance will be made.

---

## 13. Live Data & Upstream Limitations

To run FINN with genuine market data:

1. In your `.env`, set:
   ```env
   DEMO_MODE=false
   ```

2. Run the probe to verify connectivity:
   ```bash
   python scripts/probe_sources.py
   ```

3. Ingest live market data:
   ```bash
   python scripts/refresh_all.py
   ```

### Upstream Behavior & Fallbacks

- **Yahoo Finance**: Daily OHLCV bars are retrieved for plain symbols via `.NS` (National Stock Exchange) with automated fallback to `.BO` (Bombay Stock Exchange).
- **NSE Announcements**: Live corporate disclosures are fetched using warm-session cookie handshakes.
- **BSE Announcements**: BSE endpoints enforce strict anti-bot controls and currently reject automated headless requests with HTTP 403 Forbidden. The pipeline gracefully falls back to NSE for announcement coverage without guessing scrip codes or fabricating synthetic data.
- **Data Cleanliness**: When `DEMO_MODE=false`, all fixture rows (`source='fixture'` or `demo_data=1`) are strictly filtered out from read paths (`GET /digest`, `GET /portfolio`, `GET /alerts`, `GET /announcements`).

---

## 14. Testing Instructions

### Backend Automated Test Suite

From the `backend/` directory:

```bash
# Run full pytest suite (170+ tests)
pytest -v

# Run Task 1 real-data spine tests specifically
pytest tests/test_task1_real_data_spine.py -v

# Run opt-in live network tests (requires internet connection)
FINN_LIVE_TESTS=1 pytest -k test_live_network_sources -v
```

### Frontend Typecheck & Build

From the `frontend/` directory:

```bash
# Run TypeScript compilation check
npm run typecheck

# Run Next.js production build
npm run build
```

---

## 15. Current Implementation Status

- [x] **Portfolio Config**: 20 NSE symbols seeded in `data/portfolio.json` and upserted idempotently.
- [x] **Live Prices**: 60+ sessions stored per portfolio ticker in SQLite with per-ticker failure isolation.
- [x] **Digest Honesty**: `/digest` returns honest statuses (`ok`, `never_refreshed`, `no_data_in_window`, `source_unavailable`).
- [x] **Real Alerts**: `/alerts` computes live alerts from SQLite anomalies and announcements matching `alert_config`.
- [x] **Watch UI**: Watch table renders live SQLite quotes and trailing 20-day volume multiples with zero placeholder numbers.
- [x] **Mobile Responsiveness**: 390px viewport certified with zero horizontal scroll overflow.
- [x] **Additive Schema Migrations**: Safe SQLite migrations (`fetched_at` on prices, `demo_data` on announcements).

---

## 16. Known Limitations

1. **BSE Scraping Restriction**: BSE corporate filings API denies headless HTTP access with HTTP 403; live announcements currently rely on the primary NSE feed.
2. **LLM Tier Quotas**: Free-tier Gemini endpoints impose strict requests-per-minute (RPM) and daily quotas; large PDF results extraction requires rate-limiting.
3. **Price Bar Frequency**: Daily OHLCV bars reflect end-of-day market closes rather than sub-second tick-level streaming.
4. **Service Worker Offline Cache**: PWA manifest is configured; background service-worker caching for full offline PWA execution is scheduled for future stages.

---

## License

Private repository. All rights reserved.
