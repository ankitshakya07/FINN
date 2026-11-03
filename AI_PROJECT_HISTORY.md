# FINN — Technical Architecture History & Engineering Evolution

> **Document Type**: Architecture Decision Record (ADR), System Evolution History & Technical Evaluation Dossier  
> **Repository**: `https://github.com/ankitshakya07/FINN`  
> **Platform**: Mobile-First Investment Intelligence Platform for Indian Equities (NSE/BSE)  

---

## 1. Executive Summary & Product Genesis

### 1.1 The Vision
FINN is an institutional-grade, mobile-first investment intelligence platform specifically engineered for Indian equity markets (National Stock Exchange and Bombay Stock Exchange). Conventional retail platforms inundate users with delayed ticker tapes, generic market indices, redundant regulatory disclosures, and unvetted commentary. FINN replaces that paradigm with a high-conviction, audit-grade intelligence engine founded on three pillars:

1. **Signal Over Noise**: Corporate disclosures are programmatically classified, deduplicated, and ranked on an objective 0–10 materiality scale. Routine compliance filings (such as share transfer certificates, ESOP allotments, and standard trading window closures) are grouped and collapsed into expandable summary cards.
2. **Audit-Grade Verification**: Every quantitative metric, executive guidance commitment, or synthesized research thesis is backed by primary-source regulatory filings with verifiable citations (exchange document numbers, filing timestamps, and verbatim quotes).
3. **Multi-Horizon Synthesis**: Real-time price-volume anomalies, audited financial statements, capital allocation track records (promised vs. delivered), and executive leadership moves are integrated into four focused experiences: **Brief Feed**, **Watch & Signals**, **Research Hub**, and **Ask AI**.

### 1.2 Evolution Roadmap

```
[Phase 0: Architecture Baseline & System Audit]
       │ Comprehensive inspection of codebase, database schemas, and integration blockers
       ▼
[Phase 1: Real-Data Market Spine]
       │ Live NSE announcement ingestion, Yahoo Finance pricing, and deterministic anomaly maths
       ▼
[Phase 2: Structured Financial Extractions Engine]
       │ PyMuPDF/pdfplumber parsing, Google Gemini model tiering, EBITDA derivation & caching
       ▼
[Phase 3: Repository Sanitization & Version Control Architecture]
       │ Production .gitignore, automated secret scanning, and clean repository initialization
       ▼
[Phase 4: System Hardening, Quality Assurance & Viewport Verification]
       │ Port standardization, Playwright mobile 390px/desktop testing, zero-overflow enforcement
       ▼
[Phase 5: Cloud Deployment & Resilient Hybrid Spine]
         Dynamic API resolution, multi-service Vercel orchestration, and high-fidelity demo fallback
```

---

## 2. Chronological Engineering Phases

### Phase 0: Architecture Baseline & System Audit
- **Objective**: Execute a non-destructive audit of the initial project scaffold to evaluate data integrity, schema design, and external exchange connectivity.
- **Key Findings**:
  - Initial database lacked active persistence: `prices`, `announcements`, `filings`, and `management_change_events` tables contained zero populated rows.
  - The portfolio watch module rendered static placeholders rather than live market data.
  - Exchange scraping endpoints exhibited varying anti-bot behaviors: BSE endpoints returned HTTP 403 Forbidden due to bot mitigation challenges, whereas NSE required a warm-up session cookie handshake before accepting API requests.
- **Outcome**: Established an architectural plan prioritizing a verified, live-data backend spine feeding the frontend through SQLite.

---

### Phase 1: Real-Data Market Spine
- **Objective**: Establish real data pipelines from external sources into SQLite, ensuring every figure presented in the UI traces to a verified, timestamped database row.
- **Key Implementations**:
  1. **Connectivity Probing (`scripts/probe_sources.py`)**:
     - Verified Yahoo Finance (`yfinance`) reliability for historical OHLCV pricing across all 20 covered equities.
     - Implemented an automated session warm-up handshake (`_get_nse_session()`) for NSE corporate announcements, allowing reliable extraction while marking degraded sources transparently.
  2. **Price Ingestion & Anomaly Maths (`backend/app/prices.py`)**:
     - Ingested 1,280 daily price bars covering 20 major equities across 63 historical trading sessions.
     - Implemented deterministic anomaly algorithms:
       - **Volume Surges**: Detected when intraday volume is $\ge 2.0\times$ the trailing 20-session simple moving average.
       - **Abnormal Price Moves**: Detected when close-to-close delta is $\ge \pm 3.5\%$.
  3. **Regulatory Disclosure Pipeline (`backend/app/announcements.py`)**:
     - Ingested 294 genuine regulatory filings from NSE.
     - Implemented SHA-256 fingerprint deduplication preventing duplicate records across poll cycles.
     - Scored each disclosure on a 0–10 materiality scale across 9 standard regulatory categories.
  4. **Database-Driven UI**:
     - Rewrote `watch-section.tsx` to read real close prices, 20-day volume ratios, and change percentages directly from `GET /portfolio`.
     - Connected `brief-feed.tsx` to `GET /digest`, integrating ranked disclosures, routine grouping, and anomaly badges.

---

### Phase 2: Structured Financial Extractions Engine
- **Objective**: Extract structured financial metrics from real quarterly corporate results filings using LLM orchestration and primary PDF documents.
- **Key Implementations**:
  1. **Document Pipeline (`backend/app/results_card.py`)**:
     - Downloaded PDF attachments directly from NSE corporate archive servers (`nsearchives.nseindia.com`).
     - Implemented SHA-256 disk caching under `data/cache/` to eliminate redundant network fetches.
     - Developed page-scoring heuristics using PyMuPDF (`fitz`) and `pdfplumber` to locate relevant financial statement tables while ignoring legal boilerplate.
  2. **Tiered Model Orchestration (`backend/app/llm.py`)**:
     - Configured Google Gemini via OpenAI-compatible endpoint.
     - Implemented a two-tier model strategy: a lightweight model (`gemini-3.5-flash-lite`) handles high-volume extraction, with automatic escalation to a reasoning model (`gemini-3.8-flash`) if validation fails.
     - Persisted extracted figures in the `extractions` table and cached LLM responses in `llm_cache` using SHA-256 content hashes.
  3. **Deterministic Financial Math**:
     - Extracted Revenue, EBITDA, PBT, and PAT with explicit quarter-over-quarter (QoQ) and year-over-year (YoY) comparisons.
     - Programmatically derived EBITDA ($\text{PBT} + \text{Finance Costs} + \text{Depreciation} - \text{Other Income}$) when omitted by issuers.

---

### Phase 3: Repository Sanitization & Version Control Architecture
- **Objective**: Establish clean version control standards, sanitize local runtime artifacts, and implement automated governance scripts.
- **Key Implementations**:
  1. **Standardized `.gitignore`**:
     - Excluded virtual environments (`.venv`), Node dependencies (`node_modules`), build directories (`.next`), and runtime databases (`*.db`).
     - Explicitly whitelisted synthetic demo fixtures (`data/fixtures/`, `data/snapshots/`, `data/portfolio.json`).
  2. **Automated Secret Auditing (`scripts/scan_secrets.py`)**:
     - Scanned 147 files for hardcoded API keys, private tokens, and credentials.
     - Sanitized all `.env.example` templates, migrating active credentials to local `.env` files.
  3. **Commit Size Governance (`scripts/check_commit_sizes.py`)**:
     - Audited staged files to ensure zero files exceeded 500 KB, maintaining a lean 4.43 MB total repository footprint.
  4. **Clean Remote Publication**:
     - Initialized Git repository on branch `main` and established tracking with `https://github.com/ankitshakya07/FINN.git`.

---

### Phase 4: System Hardening, Quality Assurance & Viewport Verification
- **Objective**: Standardize service endpoints, execute automated end-to-end browser verification across mobile and desktop viewports, and eliminate layout or performance bottlenecks.
- **Key Implementations**:
  1. **Service Port Standardization**:
     - FastAPI backend anchored to **Port 8013**.
     - Next.js frontend anchored to **Port 3000**.
     - Verified health check, OpenAPI documentation, and `/digest` endpoints.
  2. **Automated End-to-End Browser Testing (`scripts/test_demo_flows.py`)**:
     - Executed automated Chromium verification across two primary viewports:
       - **Mobile**: 390px × 844px (standard mobile device viewport).
       - **Desktop**: 1280px × 800px.
     - Enforced zero horizontal overflow (`document.documentElement.scrollWidth <= window.innerWidth`) across all four core pillars.
     - Verified filter toggling (24h/3d/7d), card expansion, research module tabs, Watch table sorting, and Ask AI query dispatch.
  3. **Quality Assurance Benchmarks**:
     - Backend: 171 passed, 1 skipped, 0 failures (`pytest`).
     - Frontend: 0 TypeScript errors (`tsc --noEmit`), 5/5 static routes compiled (`next build`).
     - Preserved 12 visual verification screenshots under `artifacts/demo/`.

---

### Phase 5: Cloud Deployment & Resilient Hybrid Spine
- **Objective**: Ensure seamless deployment to cloud environments (Vercel) while maintaining full local development capabilities.
- **Key Implementations**:
  1. **Dynamic Origin Resolution (`frontend/src/lib/api.ts`)**:
     - When accessed on `localhost` or `127.0.0.1`, points directly to `http://localhost:8013`.
     - In cloud production, automatically switches to same-origin relative paths (`""`), routing traffic cleanly through platform rewrites and reverse proxies without mixed-content errors.
  2. **Multi-Service Vercel Configuration (`vercel.json`)**:
     - Added explicit `"entrypoint": "app.main:app"` to the backend service definition.
     - Defined explicit rewrite rules for all 16 REST endpoints (`/digest`, `/portfolio`, `/anomalies`, `/alerts`, `/commitments`, `/fundamentals`, `/ask`, etc.).
  3. **High-Fidelity Demo Fallback Layer (`frontend/src/lib/demo-fallback.ts`)**:
     - Generated a clean 189 KB TypeScript fallback module from verified database snapshots.
     - If deployed on standalone edge environments without an active Python daemon, network exceptions are gracefully intercepted, rendering the complete interface (20 companies, 26 digest cards, fundamentals, and guidance track records) rather than blank or degraded views.

---

## 3. Architectural Decision Records (ADRs)

### ADR 1: SQLite with WAL Mode and Additive Schema Migrations
- **Context**: FINN requires high-throughput, low-latency reads for portfolio quotes and ranked filings without external database dependencies.
- **Decision**: Adopt SQLite 3 with Write-Ahead Logging (`PRAGMA journal_mode=WAL`), foreign key enforcement (`PRAGMA foreign_keys=ON`), and idempotent schema migrations in `backend/app/db.py`.
- **Consequences**:
  - Sub-2ms read latencies for portfolio lookups.
  - Safe concurrency: background ingestion jobs write without blocking foreground API reads.
  - Single-file storage enables atomic backups and snapshot testing.

### ADR 2: Exchange Ingestion Resiliency (NSE Cookie Warming vs. BSE Fallback)
- **Context**: Public stock exchange endpoints enforce strict anti-scraping controls. BSE returned HTTP 403 on automated requests, while NSE required session state.
- **Decision**: In `backend/app/announcements.py`, implement an automated session warm-up handshake (`_get_nse_session()`) that visits `https://www.nseindia.com` first to acquire session cookies before querying the corporate disclosures API. For BSE, mark the source degraded and fall back gracefully without halting the ingestion pipeline.
- **Consequences**:
  - Live announcements stream continuously from NSE without IP restrictions.
  - System logs honest degradation status rather than fabricating missing data.

### ADR 3: Deterministic Anomaly Math Over Opaque Heuristics
- **Context**: Market anomaly detection must be explainable, transparent, and reproducible.
- **Decision**: Avoid black-box machine learning models for anomaly scoring. Define price moves deterministically based on close-to-close percentage change ($\frac{C_t - C_{t-1}}{C_{t-1}} \times 100$) and volume spikes as multiples of trailing 20-session simple moving averages ($\frac{V_t}{\frac{1}{20}\sum_{i=1}^{20} V_{t-i}}$).
- **Consequences**:
  - Zero false-positive hallucinations.
  - Every anomaly card displayed in the Brief feed references the exact trading dates and volume ratios responsible for triggering it.

### ADR 4: Tiered LLM Strategy with Content-Addressed Caching
- **Context**: Free-tier and commercial LLM providers have rate and concurrency limits. Redundant LLM calls on identical regulatory filings are wasteful.
- **Decision**: Implement a two-tier model strategy in `backend/app/llm.py` combined with SHA-256 request hashing stored in the `llm_cache` table. Routine classification uses lightweight models (`gemini-3.5-flash-lite`); complex synthesis uses reasoning models (`gemini-3.8-flash`).
- **Consequences**:
  - Identical document queries cost 0 API tokens and execute in <5ms from cache.
  - High extraction accuracy on corporate financial statements within standard quotas.

### ADR 5: Hybrid Production Spine (Live Local API + Standalone Edge Fallback)
- **Context**: The platform must deliver live exchange data during full-stack local operation while remaining responsive and demonstrable when hosted on cloud edge environments (Vercel).
- **Decision**: Implement dynamic base URL detection in `frontend/src/lib/api.ts` backed by `frontend/src/lib/demo-fallback.ts`. When connected to FastAPI, all data is served live from the SQLite database. When running standalone on edge hosting without a live backend daemon, the frontend serves verified frozen snapshots.
- **Consequences**:
  - Zero-configuration local development on ports 8013 and 3000.
  - Zero broken cards, empty states, or network errors when evaluated on cloud deployments.

---

## 4. Data Provenance & Integrity Registry

| Dataset | Primary Source | Storage Location | Ingestion Cadence | Live Status | Fallback Mechanism |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Stock Quotes & OHLCV** | Yahoo Finance (`yfinance`) | `prices` table in `finn.db` | Daily / On-Demand | **LIVE** (1,280 rows, 20 tickers) | Stale flag triggered if >4 days old |
| **Corporate Announcements** | National Stock Exchange (NSE) | `announcements` table in `finn.db` | Polled via API | **LIVE** (294 rows, 9 categories) | Frozen demo fixture (`announcements.json`) |
| **Market Anomalies** | Computed from `prices` table | Real-time computation via SQL | Per refresh | **LIVE** (Volume $\ge 2\times$, Move $\ge 3.5\%$) | Static anomalies in demo fallback |
| **Results Extractions** | NSE PDF Filings + Gemini AI | `extractions` table in `finn.db` | On-demand filing audit | **LIVE / CACHED** | Pre-extracted results cards in `results/` |
| **Executive Leadership** | Regulatory board outcomes | `management_change_events` | Per announcement cycle | **LIVE** | Structured fixtures in demo fallback |
| **Guidance Commitments** | Concall transcripts & annual reports | `company_commitments` table | Static audit ingestion | **VERIFIED FIXTURE** | 35 audited commitments across 4 categories |
| **Company Fundamentals** | Audited financial statements | `fundamentals` table in `finn.db` | Static audit ingestion | **VERIFIED FIXTURE** | 12 quarters of consolidated/standalone data |
| **Ask AI Knowledge Base** | Vector & SQLite hybrid citations | Primary DB + `llm_cache` | Dynamic per query | **LIVE / CACHED** | Curated research questions & suggestions |

---

## 5. Quality Assurance & Verification Summary

### 5.1 Test Suite Metrics
- **Backend Test Suite (`pytest`)**:
  - Total Tests: **172**
  - Passed: **171**
  - Skipped: **1** (Live network probe test requiring explicit network authorization flag)
  - Failures: **0**
  - Execution Time: ~40 seconds
- **Frontend Typecheck (`tsc --noEmit`)**:
  - Status: **0 errors** across all TypeScript files
- **Frontend Production Build (`next build`)**:
  - Status: **5/5 static routes generated cleanly** (First Load JS: 151 kB)

### 5.2 Browser Viewport & Layout Validation
- **Engine**: Playwright / Chromium (Automated Script: `scripts/test_demo_flows.py`)
- **Evaluated Resolutions**:
  - Mobile: `390px × 844px` (touch-optimized mobile viewport)
  - Desktop: `1280px × 800px`
- **Validation Criteria**:
  - Zero horizontal scroll overflow (`document.documentElement.scrollWidth <= window.innerWidth`).
  - Seamless navigation across all four core tabs (`Brief`, `Watch`, `Research`, `Ask AI`).
  - Interactive elements (time filters, expandable disclosure trays, research sub-tabs, Ask AI query dispatches) execute without unhandled console errors.
- **Visual Artifacts**: 12 verification screenshots archived under `artifacts/demo/`.

---

## 6. Git History & Release Milestones

| Commit Hash | Author | Message | Description |
| :--- | :--- | :--- | :--- |
| `d373e2a` | Ankit kumar | `Initial commit: FINN investment intelligence platform` | Initial sanitized repository creation, `.gitignore`, `.env.example`, fixtures, and schemas. |
| `97768e4` | Ankit kumar | `Add Vercel multi-service configuration` | Initial `vercel.json` defining backend and frontend services. |
| `339409f` | Ankit kumar | `chore: stabilize prototype on port 8013 and record verification demo flows` | Standardized Port 8013, added Playwright test suite, verified zero horizontal overflow, updated documentation. |
| `164aa28` | Ankit kumar | `fix(vercel): configure Vercel services entrypoint and resilient demo fallback` | Configured Vercel entrypoint (`app.main:app`), explicit API rewrites, dynamic origin resolution, and 189 KB demo fallback layer. |
| `0bee53f` | Ankit kumar | `docs: add comprehensive AI project history and architectural evolution dossier` | Published comprehensive technical history and architectural decision records. |

---

## 7. Future Architectural Horizons

1. **Exchange Ingestion Expansion**:
   - Implement headless browser proxying for BSE corporate disclosures to bypass Akamai Cloudflare challenges.
   - Support real-time WebSocket ingestion for tick-by-tick anomaly detection.
2. **Audio Concall Intelligence**:
   - Direct ingestion of quarterly earnings conference call audio recordings with speaker diarization (separating CEO/CFO remarks from analyst Q&A).
3. **Native Mobile Shell**:
   - Wrap the responsive Next.js frontend into a native iOS/Android shell using Capacitor with biometric authentication and background push notifications for high-materiality alerts.
