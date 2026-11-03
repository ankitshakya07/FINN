"use client";

import { useEffect, useMemo, useState } from "react";
import { getFundamentals, getFundamentalsHistory, getFundamentalsRatios } from "@/lib/api";
import type {
  FinancialPeriodRecord,
  FundamentalsHistoryResponse,
  FundamentalsOverview,
  FundamentalsRatiosResponse,
} from "@/lib/types";

const COMPANIES = [
  { ticker: "INFY", name: "Infosys Limited" },
  { ticker: "TCS", name: "Tata Consultancy Services Limited" },
  { ticker: "RELIANCE", name: "Reliance Industries Limited" },
  { ticker: "HDFCBANK", name: "HDFC Bank Limited" },
];

const formatCr = (val: number | null | undefined): string => {
  if (val == null) return "—";
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 1 }).format(val);
};

const formatPct = (val: number | null | undefined): string => {
  if (val == null) return "—";
  return `${val.toFixed(1)}%`;
};

const formatRatio = (val: number | null | undefined): string => {
  if (val == null) return "—";
  return `${val.toFixed(1)}x`;
};

type StatementTab = "kpis" | "income" | "balance" | "cashflow" | "ratios";

export default function FundamentalsSection() {
  const [selectedTicker, setSelectedTicker] = useState("INFY");
  const [basis, setBasis] = useState<"consolidated" | "standalone">("consolidated");
  const [periodType, setPeriodType] = useState<"annual" | "quarterly">("annual");
  const [activeTab, setActiveTab] = useState<StatementTab>("kpis");

  const [overview, setOverview] = useState<FundamentalsOverview | null>(null);
  const [history, setHistory] = useState<FundamentalsHistoryResponse | null>(null);
  const [ratios, setRatios] = useState<FundamentalsRatiosResponse | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    setError(null);

    Promise.all([
      getFundamentals(selectedTicker, basis),
      getFundamentalsHistory(selectedTicker, { period_type: periodType, basis, limit: 10 }),
      getFundamentalsRatios(selectedTicker, basis),
    ])
      .then(([ov, hist, rat]) => {
        if (!alive) return;
        setOverview(ov);
        setHistory(hist);
        setRatios(rat);
      })
      .catch(() => {
        if (!alive) return;
        setError("Could not retrieve company fundamentals. Verify API connection and try again.");
      })
      .finally(() => {
        if (alive) setLoading(false);
      });

    return () => {
      alive = false;
    };
  }, [selectedTicker, basis, periodType, retry]);

  const periods: FinancialPeriodRecord[] = useMemo(() => history?.periods ?? [], [history]);
  const latestAnnual = overview?.latest_annual;
  const latestQuarter = overview?.latest_quarter;

  // Chart data calculations
  const maxRevenue = useMemo(() => {
    if (!periods.length) return 1;
    return Math.max(...periods.map((p) => p.revenue ?? 0), 1);
  }, [periods]);

  return (
    <section className="fundamentals-section" id="fundamentals">
      <div className="section-heading compact">
        <div>
          <div className="section-kicker">COMPANY RESEARCH</div>
          <h2>Company fundamentals</h2>
          <p className="asof-line">
            Historical financial statements, profitability metrics, and return ratios in INR Crore
          </p>
        </div>
        <span className={`snapshot-badge ${overview && !overview.demo_mode ? "mode-live-badge" : ""}`}>
          {overview ? (overview.demo_mode ? "DEMO MODE" : "PRIMARY DATA") : "CHECKING DATA"}
        </span>
      </div>

      {/* Selectors and Control Bar */}
      <div className="fundamentals-controls">
        <div className="control-group">
          <label htmlFor="fund-ticker-select" className="control-label">
            Company
          </label>
          <select
            id="fund-ticker-select"
            value={selectedTicker}
            onChange={(e) => setSelectedTicker(e.target.value)}
            className="fund-select"
            disabled={loading}
          >
            {COMPANIES.map((c) => (
              <option key={c.ticker} value={c.ticker}>
                {c.ticker} · {c.name}
              </option>
            ))}
          </select>
        </div>

        <div className="toggle-group">
          <div className="pill-toggle" role="radiogroup" aria-label="Reporting basis">
            <button
              type="button"
              className={`pill-btn ${basis === "consolidated" ? "active" : ""}`}
              onClick={() => setBasis("consolidated")}
              aria-checked={basis === "consolidated"}
            >
              Consolidated
            </button>
            <button
              type="button"
              className={`pill-btn ${basis === "standalone" ? "active" : ""}`}
              onClick={() => setBasis("standalone")}
              aria-checked={basis === "standalone"}
            >
              Standalone
            </button>
          </div>

          <div className="pill-toggle" role="radiogroup" aria-label="Frequency">
            <button
              type="button"
              className={`pill-btn ${periodType === "annual" ? "active" : ""}`}
              onClick={() => setPeriodType("annual")}
              aria-checked={periodType === "annual"}
            >
              Annual
            </button>
            <button
              type="button"
              className={`pill-btn ${periodType === "quarterly" ? "active" : ""}`}
              onClick={() => setPeriodType("quarterly")}
              aria-checked={periodType === "quarterly"}
            >
              Quarterly
            </button>
          </div>
        </div>
      </div>

      {error ? (
        <div className="feed-state error-state">
          <span className="state-symbol">!</span>
          <b>Fundamentals unavailable</b>
          <p>{error}</p>
          <button type="button" onClick={() => setRetry((x) => x + 1)}>
            Try again <span>→</span>
          </button>
        </div>
      ) : loading && !overview ? (
        <div className="feed-state loading-state">
          <span className="loader-ring" />
          <b>Loading fundamentals</b>
          <p>Requesting {selectedTicker} financial statements and ratios…</p>
        </div>
      ) : (
        <div className="fundamentals-content">
          {/* Company Valuation & Profile Card */}
          {overview && (
            <div className="card fund-company-card">
              <div className="company-header-row">
                <div>
                  <span className="company-ticker-badge">{overview.ticker}</span>
                  <h3 className="company-title">{overview.company_name}</h3>
                  <div className="company-tags">
                    {overview.sector && <span className="meta-tag">{overview.sector}</span>}
                    {overview.industry && <span className="meta-tag">{overview.industry}</span>}
                    <span className="meta-tag basis-tag">{basis.toUpperCase()}</span>
                  </div>
                </div>
                <div className="company-price-box">
                  <span className="price-label">LAST PRICE</span>
                  <strong className="current-price">
                    {overview.current_price ? `₹${formatCr(overview.current_price)}` : "—"}
                  </strong>
                </div>
              </div>

              <div className="valuation-grid">
                <div className="val-stat">
                  <span>Market Cap</span>
                  <strong>{overview.market_cap_inr_cr ? `₹${formatCr(overview.market_cap_inr_cr)} Cr` : "—"}</strong>
                </div>
                <div className="val-stat">
                  <span>P/E Ratio</span>
                  <strong>{formatRatio(overview.pe_ratio)}</strong>
                </div>
                <div className="val-stat">
                  <span>P/B Ratio</span>
                  <strong>{formatRatio(overview.pb_ratio)}</strong>
                </div>
                <div className="val-stat">
                  <span>ROE</span>
                  <strong className="accent-text">{formatPct(overview.roe_pct)}</strong>
                </div>
                <div className="val-stat">
                  <span>ROCE</span>
                  <strong className="accent-text">{formatPct(overview.roce_pct)}</strong>
                </div>
                <div className="val-stat">
                  <span>Div. Yield</span>
                  <strong>{formatPct(overview.dividend_yield_pct)}</strong>
                </div>
              </div>
            </div>
          )}

          {/* Statement View Navigation Tabs */}
          <div className="statement-nav" role="tablist" aria-label="Statement selection">
            {(
              [
                ["kpis", "Overview & KPIs"],
                ["income", "Income Statement"],
                ["balance", "Balance Sheet"],
                ["cashflow", "Cash Flow"],
                ["ratios", "Ratios & Trends"],
              ] as const
            ).map(([tabKey, tabLabel]) => (
              <button
                key={tabKey}
                type="button"
                role="tab"
                aria-selected={activeTab === tabKey}
                className={`statement-tab-btn ${activeTab === tabKey ? "active" : ""}`}
                onClick={() => setActiveTab(tabKey)}
              >
                {tabLabel}
              </button>
            ))}
          </div>

          {/* TAB 1: OVERVIEW & KEY PERFORMANCE INDICATORS */}
          {activeTab === "kpis" && (
            <div className="kpis-container">
              {/* Latest Performance Summary Cards */}
              <div className="kpis-grid">
                <article className="results-kpi">
                  <span>REVENUE ({periodType === "annual" ? latestAnnual?.period_label ?? "FY26" : latestQuarter?.period_label ?? "Q2 FY27"})</span>
                  <strong>
                    ₹{formatCr(periodType === "annual" ? latestAnnual?.revenue : latestQuarter?.revenue)} Cr
                  </strong>
                  <div className="results-growth">
                    <small>
                      Operating Margin: <b>{formatPct(periodType === "annual" ? latestAnnual?.operating_margin_pct : latestQuarter?.operating_margin_pct)}</b>
                    </small>
                  </div>
                </article>

                <article className="results-kpi">
                  <span>EBITDA</span>
                  <strong>
                    ₹{formatCr(periodType === "annual" ? latestAnnual?.ebitda : latestQuarter?.ebitda)} Cr
                  </strong>
                  <div className="results-growth">
                    <small>
                      EBITDA Margin: <b>{formatPct(periodType === "annual" ? latestAnnual?.ebitda_margin_pct : latestQuarter?.ebitda_margin_pct)}</b>
                    </small>
                  </div>
                </article>

                <article className="results-kpi">
                  <span>NET PROFIT (PAT)</span>
                  <strong>
                    ₹{formatCr(periodType === "annual" ? latestAnnual?.pat : latestQuarter?.pat)} Cr
                  </strong>
                  <div className="results-growth">
                    <small>
                      PAT Margin: <b>{formatPct(periodType === "annual" ? latestAnnual?.net_profit_margin_pct : latestQuarter?.net_profit_margin_pct)}</b>
                    </small>
                  </div>
                </article>

                <article className="results-kpi">
                  <span>FREE CASH FLOW</span>
                  <strong>
                    ₹{formatCr(periodType === "annual" ? latestAnnual?.free_cash_flow : latestQuarter?.free_cash_flow)} Cr
                  </strong>
                  <div className="results-growth">
                    <small>
                      Net Debt: <b>₹{formatCr(periodType === "annual" ? latestAnnual?.net_debt : latestQuarter?.net_debt)} Cr</b>
                    </small>
                  </div>
                </article>
              </div>

              {/* Responsive SVG Historical Chart */}
              {periods.length > 0 && (
                <div className="card chart-card">
                  <div className="chart-header">
                    <div>
                      <span className="chart-title">Revenue & Net Profit Trend</span>
                      <small className="chart-sub">Reported progression across {periods.length} {periodType} periods</small>
                    </div>
                    <div className="chart-legend">
                      <span className="legend-item"><i className="legend-box rev-box" /> Revenue</span>
                      <span className="legend-item"><i className="legend-box pat-box" /> PAT</span>
                    </div>
                  </div>

                  <div className="chart-svg-wrap">
                    <svg
                      viewBox={`0 0 ${periods.length * 60 + 40} 140`}
                      className="fundamentals-chart-svg"
                      preserveAspectRatio="none"
                    >
                      {/* Grid lines */}
                      <line x1="20" y1="20" x2={periods.length * 60 + 20} y2="20" stroke="rgba(255,255,255,0.08)" strokeDasharray="2 2" />
                      <line x1="20" y1="65" x2={periods.length * 60 + 20} y2="65" stroke="rgba(255,255,255,0.08)" strokeDasharray="2 2" />
                      <line x1="20" y1="110" x2={periods.length * 60 + 20} y2="110" stroke="rgba(255,255,255,0.15)" />

                      {/* Bars */}
                      {periods.map((p, i) => {
                        const x = 30 + i * 60;
                        const revHeight = Math.max(4, ((p.revenue ?? 0) / maxRevenue) * 90);
                        const patHeight = Math.max(2, ((p.pat ?? 0) / maxRevenue) * 90);
                        const revY = 110 - revHeight;
                        const patY = 110 - patHeight;

                        return (
                          <g key={p.id}>
                            {/* Revenue Bar */}
                            <rect
                              x={x - 14}
                              y={revY}
                              width="12"
                              height={revHeight}
                              rx="2"
                              fill="#3b82f6"
                              opacity="0.85"
                            />
                            {/* PAT Bar */}
                            <rect
                              x={x}
                              y={patY}
                              width="12"
                              height={patHeight}
                              rx="2"
                              fill="#10b981"
                              opacity="0.9"
                            />
                            {/* Period label */}
                            <text
                              x={x}
                              y="126"
                              textAnchor="middle"
                              fontSize="9"
                              fill="#94a3b8"
                              fontFamily="inherit"
                            >
                              {p.period_label}
                            </text>
                          </g>
                        );
                      })}
                    </svg>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: INCOME STATEMENT */}
          {activeTab === "income" && (
            <div className="card statement-card">
              <div className="table-responsive">
                <table className="fund-table">
                  <thead>
                    <tr>
                      <th className="sticky-col">Line Item (₹ Cr)</th>
                      {periods.map((p) => (
                        <th key={p.id}>{p.period_label}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="sticky-col font-medium">Revenue from Operations</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell">{formatCr(p.revenue)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="sticky-col">Other Income</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell">{formatCr(p.other_income)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="sticky-col">Total Expenses</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell">{formatCr(p.total_expenses)}</td>
                      ))}
                    </tr>
                    <tr className="highlight-row">
                      <td className="sticky-col font-medium">Operating Profit</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell highlight-val">{formatCr(p.operating_profit)}</td>
                      ))}
                    </tr>
                    <tr className="highlight-row">
                      <td className="sticky-col font-medium">EBITDA</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell highlight-val">{formatCr(p.ebitda)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="sticky-col">Depreciation</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell">{formatCr(p.depreciation)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="sticky-col">Finance Costs</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell">{formatCr(p.finance_costs)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="sticky-col font-medium">Profit Before Tax (PBT)</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell">{formatCr(p.pbt)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="sticky-col">Tax Expense</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell">{formatCr(p.tax)}</td>
                      ))}
                    </tr>
                    <tr className="accent-row">
                      <td className="sticky-col font-bold">Net Profit (PAT)</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell font-bold accent-val">{formatCr(p.pat)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="sticky-col">EPS (₹)</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell">{p.eps != null ? `₹${p.eps.toFixed(1)}` : "—"}</td>
                      ))}
                    </tr>
                    <tr className="metric-row">
                      <td className="sticky-col">Operating Margin %</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell">{formatPct(p.operating_margin_pct)}</td>
                      ))}
                    </tr>
                    <tr className="metric-row">
                      <td className="sticky-col">EBITDA Margin %</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell">{formatPct(p.ebitda_margin_pct)}</td>
                      ))}
                    </tr>
                    <tr className="metric-row">
                      <td className="sticky-col">Net Profit Margin %</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell">{formatPct(p.net_profit_margin_pct)}</td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 3: BALANCE SHEET */}
          {activeTab === "balance" && (
            <div className="card statement-card">
              <div className="table-responsive">
                <table className="fund-table">
                  <thead>
                    <tr>
                      <th className="sticky-col">Balance Sheet (₹ Cr)</th>
                      {periods.map((p) => (
                        <th key={p.id}>{p.period_label}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="highlight-row">
                      <td className="sticky-col font-bold">Total Assets</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell font-bold highlight-val">{formatCr(p.total_assets)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="sticky-col font-medium">Total Equity (Net Worth)</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell">{formatCr(p.total_equity)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="sticky-col">Total Borrowings (Debt)</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell">{formatCr(p.total_borrowings)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="sticky-col">Cash and Equivalents</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell">{formatCr(p.cash_and_equivalents)}</td>
                      ))}
                    </tr>
                    <tr className="accent-row">
                      <td className="sticky-col font-bold">Net Debt</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell font-bold accent-val">{formatCr(p.net_debt)}</td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: CASH FLOW */}
          {activeTab === "cashflow" && (
            <div className="card statement-card">
              <div className="table-responsive">
                <table className="fund-table">
                  <thead>
                    <tr>
                      <th className="sticky-col">Cash Flow (₹ Cr)</th>
                      {periods.map((p) => (
                        <th key={p.id}>{p.period_label}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="highlight-row">
                      <td className="sticky-col font-medium">Cash Flow from Operations (CFO)</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell font-medium highlight-val">{formatCr(p.cash_from_operations)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="sticky-col">Capital Expenditure (Capex)</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell">{formatCr(p.capex)}</td>
                      ))}
                    </tr>
                    <tr className="accent-row">
                      <td className="sticky-col font-bold">Free Cash Flow (FCF)</td>
                      {periods.map((p) => (
                        <td key={p.id} className="num-cell font-bold accent-val">{formatCr(p.free_cash_flow)}</td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 5: RATIOS & TRENDS */}
          {activeTab === "ratios" && (
            <div className="ratios-container">
              <div className="ratios-summary-grid">
                <article className="results-kpi">
                  <span>OPERATING MARGIN</span>
                  <strong>{formatPct(ratios?.current_ratios.operating_margin_pct)}</strong>
                  <div className="results-growth"><small>Core profitability</small></div>
                </article>
                <article className="results-kpi">
                  <span>EBITDA MARGIN</span>
                  <strong>{formatPct(ratios?.current_ratios.ebitda_margin_pct)}</strong>
                  <div className="results-growth"><small>Operational cash margin</small></div>
                </article>
                <article className="results-kpi">
                  <span>NET PROFIT MARGIN</span>
                  <strong>{formatPct(ratios?.current_ratios.net_profit_margin_pct)}</strong>
                  <div className="results-growth"><small>Bottom-line conversion</small></div>
                </article>
                <article className="results-kpi">
                  <span>RETURN ON EQUITY (ROE)</span>
                  <strong className="accent-text">{formatPct(ratios?.current_ratios.roe_pct)}</strong>
                  <div className="results-growth"><small>Shareholder returns</small></div>
                </article>
                <article className="results-kpi">
                  <span>RETURN ON CAPITAL (ROCE)</span>
                  <strong className="accent-text">{formatPct(ratios?.current_ratios.roce_pct)}</strong>
                  <div className="results-growth"><small>Capital efficiency</small></div>
                </article>
                <article className="results-kpi">
                  <span>DEBT TO EQUITY</span>
                  <strong>{ratios?.current_ratios.debt_to_equity != null ? `${ratios.current_ratios.debt_to_equity.toFixed(2)}x` : "—"}</strong>
                  <div className="results-growth"><small>Balance sheet leverage</small></div>
                </article>
              </div>

              {/* Ratios Trend Table */}
              <div className="card statement-card">
                <div className="table-responsive">
                  <table className="fund-table">
                    <thead>
                      <tr>
                        <th className="sticky-col">Period</th>
                        <th>Op. Margin</th>
                        <th>EBITDA Margin</th>
                        <th>PAT Margin</th>
                        <th>ROE</th>
                        <th>ROCE</th>
                        <th>Debt / Equity</th>
                        <th>Int. Coverage</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ratios?.trends.map((t) => (
                        <tr key={t.period_end}>
                          <td className="sticky-col font-medium">{t.period_label}</td>
                          <td className="num-cell">{formatPct(t.operating_margin_pct)}</td>
                          <td className="num-cell">{formatPct(t.ebitda_margin_pct)}</td>
                          <td className="num-cell">{formatPct(t.net_profit_margin_pct)}</td>
                          <td className="num-cell accent-text">{formatPct(t.roe_pct)}</td>
                          <td className="num-cell accent-text">{formatPct(t.roce_pct)}</td>
                          <td className="num-cell">{t.debt_to_equity != null ? `${t.debt_to_equity.toFixed(2)}x` : "—"}</td>
                          <td className="num-cell">{t.interest_coverage != null ? `${t.interest_coverage.toFixed(1)}x` : "—"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Footnote and Metadata */}
          <footer className="fund-footnote">
            <div className="footnote-left">
              <span>Primary source: {overview?.source.toUpperCase()}</span>
              <span>· Unit: INR Crore</span>
              <span>· Reporting: {basis.toUpperCase()}</span>
            </div>
            {overview?.latest_annual?.source_url && (
              <a
                href={overview.latest_annual.source_url}
                target="_blank"
                rel="noreferrer"
                className="source-link"
              >
                View on Screener ↗
              </a>
            )}
          </footer>
        </div>
      )}
    </section>
  );
}
