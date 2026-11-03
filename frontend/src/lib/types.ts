export type WindowPreset = "24h" | "3d" | "7d" | "custom";
export type Priority = "high" | "medium" | "low";
export type Citation = { document: string; locator: string; quote: string };

export type DigestItem = {
  id: string;
  ticker: string;
  company_name: string;
  kind: "filing" | "anomaly" | "results";
  category: string;
  headline: string;
  summary: string;
  priority: Priority;
  occurred_at: string;
  citations: Citation[];
  materiality_score: number | null;
  source_reference: string | null;
  attachment_url: string | null;
  data_source: string;
  source?: string | null;
  fetched_at?: string | null;
  demo_mode: boolean;
  rank_score: number;
  rank_reasons: string[];
  collapsed_count: number;
  supporting_details: Record<string, unknown>;
};
export type DigestResponse = {
  window: WindowPreset;
  from_at: string;
  to_at: string;
  as_of: string;
  demo_mode: boolean;
  status?: "ok" | "no_data_in_window" | "never_refreshed" | "source_unavailable";
  last_refresh?: string | null;
  items: DigestItem[];
  collapsed_count: number;
  total_count: number;
  limit: number;
  offset: number;
  sort: "relevance" | "recency";
};

export type Alert = {
  id: string;
  ticker: string;
  kind?: "price" | "volume" | "announcement";
  alert_type: "announcement" | "price_move" | "volume_spike";
  title: string;
  reason?: string;
  message: string;
  triggered_at: string;
  source?: string;
  read: boolean;
};
export type AlertsResponse = { as_of: string; demo_mode: boolean; alerts: Alert[] };

export type PortfolioItem = {
  ticker: string;
  name: string;
  sector: string | null;
  latest_close: number | null;
  prev_close: number | null;
  change_pct: number | null;
  latest_volume: number | null;
  vol_ratio_20d: number | null;
  as_of_date: string | null;
  source: string | null;
  fetched_at: string | null;
  is_stale: boolean;
  status: "ok" | "no_data";
};

export type PortfolioResponse = {
  as_of: string;
  demo_mode: boolean;
  data_source: string;
  companies: PortfolioItem[];
};

export type AlertConfigInput = {
  ticker: string | null;
  enabled: boolean;
  announcement_categories: string[];
  price_move_pct: number | null;
  volume_multiple: number | null;
  notify_on_high_priority: boolean;
};
export type AlertConfigResponse = AlertConfigInput & { id: number; updated_at: string };

export type Anomaly = {
  id: string;
  ticker: string;
  anomaly_type: "price_move" | "volume_spike";
  observed_value: number;
  threshold_value: number;
  unit: string;
  detected_at: string;
  explanation: string;
};
export type AnomaliesResponse = { as_of: string; demo_mode: boolean; data_source?: "fixture-csv" | "yfinance" | "mixed" | "none"; anomalies: Anomaly[] };

export type FilingCardResponse = {
  id: string;
  ticker: string;
  company_name: string;
  filed_at: string;
  category: string;
  headline: string;
  raw_url: string;
  priority: Priority;
  summary: string;
  key_points: string[];
  citations: Citation[];
  as_of: string;
  demo_mode: boolean;
};

export type ResultsFiling = {
  filing_id: string;
  ticker: string;
  company_name: string;
  headline: string;
  filed_at: string;
  attachment_url: string;
  raw_url: string;
  source: string;
  card_available: boolean;
};
export type ResultsFilingsResponse = { count: number; demo_mode: boolean; filings: ResultsFiling[] };

export type ManagementChange = {
  id: string; ticker: string; company_name: string; person_name: string | null;
  role_category: string; previous_designation: string | null; new_designation: string | null;
  change_type: "appointment" | "resignation" | "retirement" | "reappointment" | "cessation" | "role_change" | "unknown";
  effective_date: string | null; reason: string | null; announced_at: string;
  filing_reference: string | null; attachment_url: string | null; materiality_score: number;
  explanation: string; extraction_status: "complete" | "incomplete" | "ambiguous";
  source: string; headline: string;
};
export type ManagementChangesResponse = { count: number; demo_mode: boolean; events: ManagementChange[] };
export type ResultsMetric = {
  raw_value: string | number | null;
  unit_as_printed: string;
  value_inr_crore: number | null;
  derived: boolean;
  citation: { field: string; period_role: string; page: number; quote: string } | Array<{ field: string; period_role: string; page: number; quote: string }> | null;
};
export type ResultsPeriod = {
  period_label: string;
  unit_as_printed: string;
  revenue_from_operations: ResultsMetric;
  other_income: ResultsMetric;
  total_expenses: ResultsMetric;
  finance_costs: ResultsMetric;
  depreciation: ResultsMetric;
  profit_before_tax: ResultsMetric;
  tax_expense: ResultsMetric;
  profit_after_tax: ResultsMetric;
  ebitda: ResultsMetric;
  ebitda_margin_pct?: number | null;
  pat_margin_pct?: number | null;
};
export type ResultsCardResponse = {
  ticker: string;
  company_name: string;
  filing_id: string;
  source_url: string;
  reporting_basis: "consolidated" | "standalone" | null;
  periods: Partial<Record<"current" | "preceding_quarter" | "corresponding_previous_year", ResultsPeriod>>;
  changes: Partial<Record<string, { qoq_pct: number | null; yoy_pct: number | null }>>;
  extraction_confidence: number | null;
  source_citations: Array<{ field: string; period_role: string; page: number; quote: string }>;
  what_stands_out: string[] | null;
  parse_failed: boolean;
  validation_errors: string[];
  demo_mode: boolean;
  source_type: "live" | "fixture";
  as_of: string;
  content_hash?: string;
};

export type ResearchModule =
  | "business_snapshot"
  | "financial_snapshot"
  | "trajectory"
  | "balance_sheet"
  | "cash_quality"
  | "narrative_vs_numbers"
  | "guidance"
  | "bull_vs_bear";

export type ResearchModuleInfo = {
  id: ResearchModule;
  title: string;
  description: string;
  icon: string;
  category: string;
};

export type ResearchRequest = { ticker: string; module: ResearchModule };
export type ResearchResult = {
  ticker: string;
  module: ResearchModule;
  status: "complete" | "partial" | "not_found";
  answer: string;
  findings: Array<Record<string, unknown>>;
  citations: Citation[];
  as_of: string;
  demo_mode: boolean;
};
export type ResearchProgress = { stage: string; message: string };
export type ResearchStreamEvent =
  | { event: "progress"; data: ResearchProgress }
  | { event: "result"; data: ResearchResult }
  | { event: "error"; data: { message: string } };

export type AskRequest = { ticker: string; question: string; conversation_id?: string };
export type AskResponse = {
  ticker: string;
  answer: string;
  citations: Citation[];
  status: "answered" | "not_found";
  as_of: string;
  demo_mode: boolean;
  conversation_id?: string | null;
  suggested_followups?: string[];
};

export type AnnouncementCategory = "results" | "M&A" | "fund_raise" | "management_change" | "litigation" | "insider_trading" | "earnings_call" | "investor_meetings" | "credit_rating" | "dividend" | "bonus_split" | "capex" | "press_release" | "postal_ballot" | "agm_egm" | "pledging" | "unclassified";
export type Announcement = {
  id: string; ticker: string; company_name: string; timestamp: string; headline: string;
  raw_category: string | null; attachment_url: string | null; source: "bse" | "nse" | "fixture";
  source_identifier: string | null; raw_metadata: Record<string, unknown>;
  classification: AnnouncementCategory; classification_method: "rules" | "model" | "unclassified";
  classification_confidence: number; materiality_base_score: number; materiality_score: number;
  materiality_reason: string; summary: string | null; created_at: string;
};
export type AnnouncementListResponse = { as_of: string; demo_mode: boolean; count: number; announcements: Announcement[] };

export type FinancialPeriodRecord = {
  id: string;
  ticker: string;
  basis: "consolidated" | "standalone";
  period_type: "quarterly" | "annual";
  period_end: string;
  period_label: string;
  fiscal_year: number;
  fiscal_quarter: number | null;
  revenue: number | null;
  other_income: number | null;
  total_expenses: number | null;
  operating_profit: number | null;
  ebitda: number | null;
  depreciation: number | null;
  finance_costs: number | null;
  pbt: number | null;
  tax: number | null;
  pat: number | null;
  eps: number | null;
  total_assets: number | null;
  total_equity: number | null;
  total_borrowings: number | null;
  cash_and_equivalents: number | null;
  net_debt: number | null;
  cash_from_operations: number | null;
  capex: number | null;
  free_cash_flow: number | null;
  operating_margin_pct: number | null;
  ebitda_margin_pct: number | null;
  net_profit_margin_pct: number | null;
  roe_pct: number | null;
  roce_pct: number | null;
  currency: string;
  unit: string;
  source: string;
  source_url: string | null;
  is_calculated: Record<string, boolean>;
};

export type FundamentalsOverview = {
  ticker: string;
  company_name: string;
  sector: string | null;
  industry: string | null;
  basis: "consolidated" | "standalone";
  market_cap_inr_cr: number | null;
  current_price: number | null;
  pe_ratio: number | null;
  pb_ratio: number | null;
  roe_pct: number | null;
  roce_pct: number | null;
  dividend_yield_pct: number | null;
  latest_quarter: FinancialPeriodRecord | null;
  latest_annual: FinancialPeriodRecord | null;
  as_of: string;
  demo_mode: boolean;
  source: string;
};

export type FundamentalsHistoryResponse = {
  ticker: string;
  company_name: string;
  basis: "consolidated" | "standalone";
  period_type: "quarterly" | "annual";
  count: number;
  as_of: string;
  demo_mode: boolean;
  periods: FinancialPeriodRecord[];
};

export type RatioTrendPoint = {
  period_label: string;
  period_end: string;
  operating_margin_pct: number | null;
  ebitda_margin_pct: number | null;
  net_profit_margin_pct: number | null;
  roe_pct: number | null;
  roce_pct: number | null;
  debt_to_equity: number | null;
  interest_coverage: number | null;
};

export type FundamentalsRatiosResponse = {
  ticker: string;
  company_name: string;
  basis: "consolidated" | "standalone";
  as_of: string;
  demo_mode: boolean;
  current_ratios: Record<string, number | null>;
  trends: RatioTrendPoint[];
};

export type CommitmentCategory =
  | "revenue_growth"
  | "margin"
  | "capex_capacity"
  | "debt_reduction"
  | "capital_allocation"
  | "operational";

export type CommitmentStatus = "met" | "beat" | "missed" | "in_progress" | "delayed";

export type CommitmentRecord = {
  id: string;
  ticker: string;
  category: CommitmentCategory;
  promise_headline: string;
  promised_by: string | null;
  promised_at: string;
  promised_period: string;
  promised_document: string;
  promised_quote: string;
  promised_locator: string | null;
  target_metric: string | null;
  target_date: string | null;
  status: CommitmentStatus;
  delivered_at: string | null;
  delivered_document: string | null;
  delivered_quote: string | null;
  delivered_locator: string | null;
  delivered_metric: string | null;
  variance_pct: number | null;
  delivery_assessment: string;
  management_explanation: string | null;
  source: string;
  source_url: string | null;
  demo_mode: boolean;
};

export type CategoryTrackRecord = {
  total: number;
  beat: number;
  met: number;
  missed: number;
  in_progress: number;
  delivery_score_pct: number;
};

export type TrackRecordSummary = {
  total_commitments: number;
  delivered_count: number;
  beat_count: number;
  met_count: number;
  missed_count: number;
  in_progress_count: number;
  delivery_score_pct: number;
  category_breakdown: Record<string, CategoryTrackRecord>;
};

export type CompanyCommitmentsResponse = {
  ticker: string;
  company_name: string;
  track_record: TrackRecordSummary;
  count: number;
  commitments: CommitmentRecord[];
  as_of: string;
  demo_mode: boolean;
};

export type CommitmentSummaryResponse = {
  ticker: string;
  company_name: string;
  delivery_score_pct: number;
  total_commitments: number;
  beat_count: number;
  met_count: number;
  missed_count: number;
  in_progress_count: number;
  as_of: string;
  demo_mode: boolean;
};

