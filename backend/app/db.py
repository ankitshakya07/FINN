from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv("SQLITE_PATH", "finn.db")

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS companies (
    ticker TEXT PRIMARY KEY,
    exchange TEXT NOT NULL DEFAULT 'NSE',
    name TEXT NOT NULL,
    sector TEXT,
    industry TEXT,
    isin TEXT,
    is_portfolio INTEGER NOT NULL DEFAULT 0,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    trading_date TEXT NOT NULL,
    open REAL, high REAL, low REAL, close REAL NOT NULL,
    adjusted_close REAL, volume INTEGER,
    source TEXT NOT NULL,
    fetched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, trading_date, source)
);
CREATE INDEX IF NOT EXISTS idx_prices_ticker_date ON prices(ticker, trading_date DESC);

CREATE TABLE IF NOT EXISTS anomalies (
    id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    anomaly_type TEXT NOT NULL CHECK(anomaly_type IN ('price_move','volume_spike')),
    observed_value REAL NOT NULL,
    threshold_value REAL NOT NULL,
    unit TEXT NOT NULL,
    detected_at TEXT NOT NULL,
    explanation TEXT NOT NULL DEFAULT '',
    source_price_date TEXT,
    acknowledged INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_anomalies_detected ON anomalies(detected_at DESC);

CREATE TABLE IF NOT EXISTS filings (
    id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    exchange TEXT NOT NULL,
    filed_at TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'unclassified',
    headline TEXT NOT NULL,
    raw_url TEXT NOT NULL,
    attachment_url TEXT,
    filing_ref TEXT,
    content_hash TEXT,
    raw_text_path TEXT,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_filings_ticker_date ON filings(ticker, filed_at DESC);

CREATE TABLE IF NOT EXISTS filing_enrichment (
    filing_id TEXT PRIMARY KEY REFERENCES filings(id) ON DELETE CASCADE,
    summary TEXT NOT NULL DEFAULT '',
    priority TEXT NOT NULL DEFAULT 'low' CHECK(priority IN ('high','medium','low')),
    key_points_json TEXT NOT NULL DEFAULT '[]',
    citations_json TEXT NOT NULL DEFAULT '[]',
    extracted_numbers_json TEXT NOT NULL DEFAULT '{}',
    model TEXT,
    enriched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    document_type TEXT NOT NULL CHECK(document_type IN ('annual_report','quarterly_results','concall_transcript','investor_presentation','screener_financials','other_primary')),
    title TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    fiscal_period TEXT,
    published_at TEXT,
    page_count INTEGER,
    content_hash TEXT NOT NULL,
    local_path TEXT,
    parse_status TEXT NOT NULL DEFAULT 'pending',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, content_hash)
);
CREATE INDEX IF NOT EXISTS idx_documents_ticker_type ON documents(ticker, document_type);

CREATE TABLE IF NOT EXISTS doc_chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    page_start INTEGER,
    page_end INTEGER,
    section_title TEXT,
    text TEXT NOT NULL,
    token_estimate INTEGER,
    content_hash TEXT NOT NULL,
    embedding_json TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    UNIQUE(document_id, chunk_index)
);
CREATE INDEX IF NOT EXISTS idx_chunks_document_page ON doc_chunks(document_id, page_start, page_end);

CREATE TABLE IF NOT EXISTS extractions (
    id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    document_id TEXT REFERENCES documents(id) ON DELETE SET NULL,
    module TEXT NOT NULL,
    extraction_key TEXT NOT NULL,
    value_json TEXT NOT NULL,
    citations_json TEXT NOT NULL DEFAULT '[]',
    model TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, module, extraction_key, content_hash)
);
CREATE INDEX IF NOT EXISTS idx_extractions_ticker_module ON extractions(ticker, module);

CREATE TABLE IF NOT EXISTS alert_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT REFERENCES companies(ticker) ON DELETE CASCADE,
    enabled INTEGER NOT NULL DEFAULT 1,
    announcement_categories_json TEXT NOT NULL DEFAULT '[]',
    price_move_pct REAL,
    volume_multiple REAL,
    notify_on_high_priority INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS llm_cache (
    key TEXT PRIMARY KEY,                 -- SHA-256 of canonical request content
    value TEXT NOT NULL,                  -- validated JSON response
    model TEXT NOT NULL,
    tokens INTEGER NOT NULL DEFAULT 0,    -- total tokens; input/output stored below too
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    cost REAL NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS announcements (
    id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    timestamp TEXT NOT NULL,
    headline TEXT NOT NULL,
    raw_category TEXT,
    attachment_url TEXT,
    source TEXT NOT NULL,
    source_identifier TEXT,
    source_identity TEXT UNIQUE,
    raw_metadata_json TEXT NOT NULL DEFAULT '{}',
    fingerprint TEXT NOT NULL UNIQUE,
    cross_source_fingerprint TEXT NOT NULL UNIQUE,
    classification TEXT NOT NULL DEFAULT 'unclassified'
        CHECK(classification IN ('results','M&A','fund_raise','management_change','litigation',
        'insider_trading','earnings_call','investor_meetings','credit_rating','dividend',
        'bonus_split','capex','press_release','postal_ballot','agm_egm','pledging','unclassified')),
    classification_method TEXT NOT NULL DEFAULT 'rules',
    classification_confidence REAL NOT NULL DEFAULT 0,
    materiality_base_score REAL NOT NULL DEFAULT 0,
    materiality_score REAL NOT NULL DEFAULT 0,
    materiality_reason TEXT NOT NULL DEFAULT '',
    summary TEXT,
    demo_data INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_announcements_ticker_time ON announcements(ticker, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_announcements_category_time ON announcements(classification, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_announcements_materiality ON announcements(materiality_score DESC, timestamp DESC);

CREATE TABLE IF NOT EXISTS management_change_events (
    id TEXT PRIMARY KEY,
    announcement_id TEXT NOT NULL UNIQUE REFERENCES announcements(id) ON DELETE CASCADE,
    ticker TEXT NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    company_name TEXT NOT NULL,
    person_name TEXT,
    role_category TEXT NOT NULL DEFAULT 'other',
    previous_designation TEXT,
    new_designation TEXT,
    change_type TEXT NOT NULL CHECK(change_type IN ('appointment','resignation','retirement','reappointment','cessation','role_change','unknown')),
    effective_date TEXT,
    reason TEXT,
    announced_at TEXT NOT NULL,
    filing_reference TEXT,
    attachment_url TEXT,
    materiality_score REAL NOT NULL DEFAULT 0 CHECK(materiality_score >= 0 AND materiality_score <= 10),
    explanation TEXT NOT NULL,
    extraction_status TEXT NOT NULL CHECK(extraction_status IN ('complete','incomplete','ambiguous')),
    source TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_management_change_ticker_date ON management_change_events(ticker, announced_at DESC);
CREATE INDEX IF NOT EXISTS idx_management_change_materiality ON management_change_events(materiality_score DESC, announced_at DESC);

CREATE TABLE IF NOT EXISTS announcement_mappings (
    ticker TEXT PRIMARY KEY,
    nse_symbol TEXT NOT NULL,
    company_name TEXT NOT NULL,
    bse_scrip_code TEXT NOT NULL,
    isin TEXT,
    mapping_source TEXT NOT NULL,
    mapping_confidence REAL NOT NULL,
    last_verified_at TEXT NOT NULL,
    source_metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS company_fundamentals (
    id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    basis TEXT NOT NULL CHECK(basis IN ('consolidated', 'standalone')),
    period_type TEXT NOT NULL CHECK(period_type IN ('quarterly', 'annual')),
    period_end TEXT NOT NULL,
    period_label TEXT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER,
    revenue REAL,
    other_income REAL,
    total_expenses REAL,
    operating_profit REAL,
    ebitda REAL,
    depreciation REAL,
    finance_costs REAL,
    pbt REAL,
    tax REAL,
    pat REAL,
    eps REAL,
    total_assets REAL,
    total_equity REAL,
    total_borrowings REAL,
    cash_and_equivalents REAL,
    net_debt REAL,
    cash_from_operations REAL,
    capex REAL,
    free_cash_flow REAL,
    operating_margin_pct REAL,
    ebitda_margin_pct REAL,
    net_profit_margin_pct REAL,
    roe_pct REAL,
    roce_pct REAL,
    currency TEXT NOT NULL DEFAULT 'INR',
    unit TEXT NOT NULL DEFAULT 'INR Crore',
    source TEXT NOT NULL DEFAULT 'screener',
    source_url TEXT,
    is_calculated_json TEXT NOT NULL DEFAULT '{}',
    raw_metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, basis, period_type, period_end)
);
CREATE INDEX IF NOT EXISTS idx_fundamentals_lookup ON company_fundamentals(ticker, period_type, basis, period_end DESC);

CREATE TABLE IF NOT EXISTS company_commitments (
    id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    category TEXT NOT NULL CHECK(category IN ('revenue_growth','margin','capex_capacity','debt_reduction','capital_allocation','operational')),
    promise_headline TEXT NOT NULL,
    promised_by TEXT,
    promised_at TEXT NOT NULL,
    promised_period TEXT NOT NULL,
    promised_document TEXT NOT NULL,
    promised_quote TEXT NOT NULL,
    promised_locator TEXT,
    target_metric TEXT,
    target_date TEXT,
    status TEXT NOT NULL CHECK(status IN ('met','beat','missed','in_progress','delayed')),
    delivered_at TEXT,
    delivered_document TEXT,
    delivered_quote TEXT,
    delivered_locator TEXT,
    delivered_metric TEXT,
    variance_pct REAL,
    delivery_assessment TEXT NOT NULL,
    management_explanation TEXT,
    source TEXT NOT NULL DEFAULT 'primary_filing',
    source_url TEXT,
    demo_mode INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, promise_headline, promised_at)
);
CREATE INDEX IF NOT EXISTS idx_commitments_ticker ON company_commitments(ticker, promised_at DESC);
CREATE INDEX IF NOT EXISTS idx_commitments_status ON company_commitments(status, ticker);

CREATE TABLE IF NOT EXISTS ask_messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    ticker TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    citations_json TEXT NOT NULL DEFAULT '[]',
    suggested_followups_json TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'complete',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ask_conversation ON ask_messages(conversation_id, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_ask_ticker ON ask_messages(ticker, created_at DESC);
"""

def connect(db_path: str | None = None) -> sqlite3.Connection:
    path = db_path or os.getenv("SQLITE_PATH", DB_PATH)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def load_portfolio_config(
    db_path: str | None = None,
    portfolio_path: str | Path | None = None,
) -> int:
    path = Path(portfolio_path) if portfolio_path else Path(__file__).resolve().parents[2] / "data" / "portfolio.json"
    if not path.is_file():
        return 0
    try:
        import json
        items = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return 0
    with connect(db_path) as conn:
        for item in items:
            ticker = str(item["ticker"]).strip().upper()
            name = str(item.get("name") or ticker).strip()
            sector = str(item.get("sector") or "").strip() or None
            conn.execute(
                """INSERT INTO companies(ticker, name, sector, is_portfolio)
                   VALUES(?, ?, ?, 1)
                   ON CONFLICT(ticker) DO UPDATE SET
                     name=CASE WHEN companies.name IS NOT NULL AND companies.name != companies.ticker THEN companies.name ELSE excluded.name END,
                     sector=COALESCE(excluded.sector, companies.sector),
                     is_portfolio=1""",
                (ticker, name, sector),
            )
        conn.commit()
    return len(items)

def init_db(db_path: str | None = None, load_portfolio: bool | None = None) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
        # Safe additive migrations
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(prices)")
        price_cols = {row["name"] for row in cur.fetchall()}
        if "fetched_at" not in price_cols:
            conn.execute("ALTER TABLE prices ADD COLUMN fetched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP")

        cur.execute("PRAGMA table_info(announcements)")
        ann_cols = {row["name"] for row in cur.fetchall()}
        if "demo_data" not in ann_cols:
            conn.execute("ALTER TABLE announcements ADD COLUMN demo_data INTEGER NOT NULL DEFAULT 0")
        conn.commit()

    should_load = load_portfolio if load_portfolio is not None else (db_path is None or db_path == DB_PATH)
    if should_load:
        load_portfolio_config(db_path)

if __name__ == "__main__":
    init_db()
    print(f"SQLite schema initialised: {Path(DB_PATH).resolve()}")
