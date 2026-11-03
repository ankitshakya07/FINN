from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal
from pydantic import BaseModel, Field

Window = Literal["24h", "3d", "7d", "custom"]


class Citation(BaseModel):
    document: str
    locator: str  # page number, quarter, or filing reference
    quote: str


class DigestItem(BaseModel):
    id: str
    ticker: str
    company_name: str
    kind: Literal["filing", "anomaly", "results"]
    category: str
    headline: str
    summary: str
    priority: Literal["high", "medium", "low"]
    occurred_at: datetime
    citations: list[Citation] = Field(default_factory=list)
    materiality_score: float | None = None
    source_reference: str | None = None
    attachment_url: str | None = None
    data_source: str = "unknown"
    source: str | None = None
    fetched_at: datetime | None = None
    demo_mode: bool = False
    rank_score: float = 0
    rank_reasons: list[str] = Field(default_factory=list)
    collapsed_count: int = 1
    supporting_details: dict[str, Any] = Field(default_factory=dict)


class DigestResponse(BaseModel):
    window: Window
    from_at: datetime
    to_at: datetime
    as_of: datetime
    demo_mode: bool
    status: Literal["ok", "no_data_in_window", "never_refreshed", "source_unavailable"] = "ok"
    last_refresh: datetime | None = None
    items: list[DigestItem]
    collapsed_count: int = 0
    total_count: int = 0
    limit: int = 50
    offset: int = 0
    sort: Literal["relevance", "recency"] = "relevance"


class Alert(BaseModel):
    id: str
    kind: Literal["price", "volume", "announcement"] = "announcement"
    alert_type: Literal["announcement", "price_move", "volume_spike"]
    ticker: str
    title: str
    reason: str = ""
    message: str = ""
    triggered_at: datetime
    source: str = "system"
    read: bool = False


class AlertsResponse(BaseModel):
    as_of: datetime
    demo_mode: bool
    alerts: list[Alert]


class PortfolioItem(BaseModel):
    ticker: str
    name: str
    sector: str | None = None
    latest_close: float | None = None
    prev_close: float | None = None
    change_pct: float | None = None
    latest_volume: int | None = None
    vol_ratio_20d: float | None = None
    as_of_date: str | None = None
    source: str | None = None
    fetched_at: str | None = None
    is_stale: bool = False
    status: Literal["ok", "no_data"] = "ok"


class PortfolioResponse(BaseModel):
    as_of: datetime
    demo_mode: bool
    data_source: str
    companies: list[PortfolioItem]


class AlertConfigInput(BaseModel):
    ticker: str | None = None  # null means portfolio-wide
    enabled: bool = True
    announcement_categories: list[str] = Field(default_factory=list)
    price_move_pct: float | None = Field(default=None, gt=0, le=100)
    volume_multiple: float | None = Field(default=None, gt=1, le=100)
    notify_on_high_priority: bool = True


class AlertConfigResponse(AlertConfigInput):
    id: int
    updated_at: datetime


class Anomaly(BaseModel):
    id: str
    ticker: str
    anomaly_type: Literal["price_move", "volume_spike"]
    observed_value: float
    threshold_value: float
    unit: str
    detected_at: datetime
    explanation: str


class AnomaliesResponse(BaseModel):
    as_of: datetime
    demo_mode: bool
    data_source: Literal["fixture-csv", "yfinance", "mixed", "none"] = "none"
    anomalies: list[Anomaly]


class FilingCardResponse(BaseModel):
    id: str
    ticker: str
    company_name: str
    filed_at: datetime
    category: str
    headline: str
    raw_url: str
    priority: Literal["high", "medium", "low"]
    summary: str
    key_points: list[str]
    citations: list[Citation]
    as_of: datetime
    demo_mode: bool


ResearchModule = Literal[
    "business_snapshot", "financial_snapshot", "trajectory", "balance_sheet",
    "cash_quality", "narrative_vs_numbers", "guidance", "bull_vs_bear"
]


class ResearchRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=24, pattern=r"^[A-Za-z0-9&._-]+$")
    module: ResearchModule



class ResearchResult(BaseModel):
    ticker: str
    module: str
    status: Literal["complete", "partial", "not_found"]
    answer: str
    findings: list[dict[str, Any]] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    as_of: datetime
    demo_mode: bool


class AskRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=24, pattern=r"^[A-Za-z0-9&._-]+$")
    question: str = Field(min_length=3, max_length=2000)
    conversation_id: str | None = None


class AskResponse(BaseModel):
    ticker: str
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    status: Literal["answered", "not_found"]
    as_of: datetime
    demo_mode: bool
    conversation_id: str | None = None
    suggested_followups: list[str] = Field(default_factory=list)



AnnouncementCategory = Literal[
    "results", "M&A", "fund_raise", "management_change", "litigation",
    "insider_trading", "earnings_call", "investor_meetings", "credit_rating",
    "dividend", "bonus_split", "capex", "press_release", "postal_ballot",
    "agm_egm", "pledging", "unclassified",
]


class AnnouncementRecord(BaseModel):
    id: str
    ticker: str
    company_name: str
    timestamp: datetime
    headline: str
    raw_category: str | None = None
    attachment_url: str | None = None
    source: Literal["bse", "nse", "fixture"]
    source_identifier: str | None = None
    raw_metadata: dict[str, Any] = Field(default_factory=dict)
    classification: AnnouncementCategory
    classification_method: Literal["rules", "model", "unclassified"]
    classification_confidence: float
    materiality_base_score: float
    materiality_score: float
    materiality_reason: str
    summary: str | None = None
    created_at: datetime


class AnnouncementListResponse(BaseModel):
    as_of: datetime
    demo_mode: bool
    count: int
    announcements: list[AnnouncementRecord]


class AnnouncementRefreshRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=24, pattern=r"^[A-Za-z0-9&._-]+$")
    from_date: date | None = None
    to_date: date | None = None


class AnnouncementRefreshResponse(BaseModel):
    ticker: str
    source: Literal["bse", "nse", "fixture"]
    demo_mode: bool
    as_of: datetime
    received: int
    inserted: int
    failures: list[str] = Field(default_factory=list)
    announcements: list[AnnouncementRecord]


class AnnouncementMappingRefreshResponse(BaseModel):
    updated: int
    ambiguous: dict[str, list[dict[str, Any]]]
    missing: list[str]


class FinancialPeriodRecord(BaseModel):
    id: str
    ticker: str
    basis: Literal["consolidated", "standalone"]
    period_type: Literal["quarterly", "annual"]
    period_end: str
    period_label: str
    fiscal_year: int
    fiscal_quarter: int | None = None
    # Income statement
    revenue: float | None = None
    other_income: float | None = None
    total_expenses: float | None = None
    operating_profit: float | None = None
    ebitda: float | None = None
    depreciation: float | None = None
    finance_costs: float | None = None
    pbt: float | None = None
    tax: float | None = None
    pat: float | None = None
    eps: float | None = None
    # Balance sheet
    total_assets: float | None = None
    total_equity: float | None = None
    total_borrowings: float | None = None
    cash_and_equivalents: float | None = None
    net_debt: float | None = None
    # Cash flow
    cash_from_operations: float | None = None
    capex: float | None = None
    free_cash_flow: float | None = None
    # Profitability & Returns
    operating_margin_pct: float | None = None
    ebitda_margin_pct: float | None = None
    net_profit_margin_pct: float | None = None
    roe_pct: float | None = None
    roce_pct: float | None = None
    # Metadata
    currency: str = "INR"
    unit: str = "INR Crore"
    source: str = "screener"
    source_url: str | None = None
    is_calculated: dict[str, bool] = Field(default_factory=dict)


class FundamentalsOverview(BaseModel):
    ticker: str
    company_name: str
    sector: str | None = None
    industry: str | None = None
    basis: Literal["consolidated", "standalone"] = "consolidated"
    market_cap_inr_cr: float | None = None
    current_price: float | None = None
    pe_ratio: float | None = None
    pb_ratio: float | None = None
    roe_pct: float | None = None
    roce_pct: float | None = None
    dividend_yield_pct: float | None = None
    latest_quarter: FinancialPeriodRecord | None = None
    latest_annual: FinancialPeriodRecord | None = None
    as_of: datetime
    demo_mode: bool
    source: str = "screener"


class FundamentalsHistoryResponse(BaseModel):
    ticker: str
    company_name: str
    basis: Literal["consolidated", "standalone"]
    period_type: Literal["quarterly", "annual"]
    count: int
    as_of: datetime
    demo_mode: bool
    periods: list[FinancialPeriodRecord]


class RatioTrendPoint(BaseModel):
    period_label: str
    period_end: str
    operating_margin_pct: float | None = None
    ebitda_margin_pct: float | None = None
    net_profit_margin_pct: float | None = None
    roe_pct: float | None = None
    roce_pct: float | None = None
    debt_to_equity: float | None = None
    interest_coverage: float | None = None


class FundamentalsRatiosResponse(BaseModel):
    ticker: str
    company_name: str
    basis: Literal["consolidated", "standalone"]
    as_of: datetime
    demo_mode: bool
    current_ratios: dict[str, float | None]
    trends: list[RatioTrendPoint]


CommitmentCategory = Literal[
    "revenue_growth", "margin", "capex_capacity", "debt_reduction", "capital_allocation", "operational"
]
CommitmentStatus = Literal["met", "beat", "missed", "in_progress", "delayed"]


class CommitmentRecord(BaseModel):
    id: str
    ticker: str
    category: CommitmentCategory
    promise_headline: str
    promised_by: str | None = None
    promised_at: str
    promised_period: str
    promised_document: str
    promised_quote: str
    promised_locator: str | None = None
    target_metric: str | None = None
    target_date: str | None = None
    status: CommitmentStatus
    delivered_at: str | None = None
    delivered_document: str | None = None
    delivered_quote: str | None = None
    delivered_locator: str | None = None
    delivered_metric: str | None = None
    variance_pct: float | None = None
    delivery_assessment: str
    management_explanation: str | None = None
    source: str = "primary_filing"
    source_url: str | None = None
    demo_mode: bool = True


class CategoryTrackRecord(BaseModel):
    total: int
    beat: int
    met: int
    missed: int
    in_progress: int
    delivery_score_pct: float


class TrackRecordSummary(BaseModel):
    total_commitments: int
    delivered_count: int
    beat_count: int
    met_count: int
    missed_count: int
    in_progress_count: int
    delivery_score_pct: float
    category_breakdown: dict[str, CategoryTrackRecord] = Field(default_factory=dict)


class CompanyCommitmentsResponse(BaseModel):
    ticker: str
    company_name: str
    track_record: TrackRecordSummary
    count: int
    commitments: list[CommitmentRecord]
    as_of: datetime
    demo_mode: bool


class CommitmentSummaryResponse(BaseModel):
    ticker: str
    company_name: str
    delivery_score_pct: float
    total_commitments: int
    beat_count: int
    met_count: int
    missed_count: int
    in_progress_count: int
    as_of: datetime
    demo_mode: bool
