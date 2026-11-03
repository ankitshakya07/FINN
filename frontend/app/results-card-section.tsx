"use client";

import { useEffect, useMemo, useState } from "react";
import { getResultsCard, getResultsFilings } from "@/lib/api";
import type { ResultsCardResponse, ResultsFiling, ResultsFilingsResponse, ResultsMetric } from "@/lib/types";

const amount = (value: number | null | undefined) => value == null
  ? "—"
  : new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(value);
const change = (value: number | null | undefined) => value == null
  ? "—"
  : `${value > 0 ? "+" : ""}${value.toFixed(1)}%`;
const when = (value: string) => new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short", timeZone: "Asia/Kolkata" }).format(new Date(value));
const pagesFor = (metric: ResultsMetric) => metric.citation == null ? [] : Array.isArray(metric.citation) ? metric.citation : [metric.citation];

export default function ResultsCardSection() {
  const [index, setIndex] = useState<ResultsFilingsResponse | null>(null);
  const [filing, setFiling] = useState("");
  const [card, setCard] = useState<ResultsCardResponse | null>(null);
  const [ticker, setTicker] = useState("");
  const [listLoading, setListLoading] = useState(true);
  const [cardLoading, setCardLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [listError, setListError] = useState<string | null>(null);
  const [retry, setRetry] = useState(0);
  const tickers = useMemo(() => Array.from(new Set((index?.filings ?? []).map(item => item.ticker))).sort(), [index]);
  const filings: ResultsFiling[] = index?.filings ?? [];

  useEffect(() => {
    let active = true;
    setListLoading(true); setListError(null); setIndex(null); setFiling(""); setCard(null);
    getResultsFilings(ticker || undefined)
      .then(value => { if (active) { setIndex(value); setFiling(value.filings[0]?.filing_id ?? ""); } })
      .catch(() => { if (active) setListError("Results filings could not be loaded. Check the FINN API connection and retry."); })
      .finally(() => { if (active) setListLoading(false); });
    return () => { active = false; };
  }, [ticker, retry]);

  async function loadCard() {
    if (!filing) return;
    setCardLoading(true); setError(null); setCard(null);
    try { setCard(await getResultsCard(filing)); }
    catch { setError("FINN could not generate this results card. The filing may be unavailable or the extraction service may need configuration."); }
    finally { setCardLoading(false); }
  }

  const current = card?.periods?.current;
  const displayMetric = (label: string, key: "revenue_from_operations" | "ebitda" | "profit_after_tax") => {
    const metric = current?.[key];
    const comparisonKey = key === "revenue_from_operations" ? "revenue_from_operations" : key === "ebitda" ? "ebitda" : "profit_after_tax";
    const comparison = card?.changes?.[comparisonKey];
    return <article className="results-kpi" key={key}>
      <span>{label}</span><strong>{metric?.value_inr_crore == null ? "Unavailable" : `₹${amount(metric.value_inr_crore)} Cr`}</strong>
      <div className="results-growth"><small>QoQ <b>{change(comparison?.qoq_pct)}</b></small><small>YoY <b>{change(comparison?.yoy_pct)}</b></small></div>
      {metric?.derived && <em>Derived</em>}
      {metric && pagesFor(metric).map((citation, index) => <a className="results-citation" key={`${citation.page}-${index}`} href={`${card?.source_url}#page=${citation.page}`} target="_blank" rel="noreferrer">Source p. {citation.page}</a>)}
    </article>;
  };

  return <section className="results-card-section" id="results-card">
    <div className="section-heading compact">
      <div><div className="section-kicker">COMPANY RESEARCH</div><h2>Quarterly results card</h2>
        <p className="asof-line">{card ? `Extracted ${when(card.as_of)} · ${card.reporting_basis ?? "basis unavailable"}` : "Source-cited financial results from stored filings"}</p>
      </div>
      <span className={`snapshot-badge ${card && !card.demo_mode ? "mode-live-badge" : ""}`}>{card ? card.demo_mode ? "DEMO FIXTURE" : "SOURCE FILING" : index ? index.filings.length ? index.demo_mode ? "DEMO FIXTURE" : "SOURCE FILINGS" : index.demo_mode ? "DEMO MODE" : "NO DATA" : "CHECKING"}</span>
    </div>

    <div className="results-picker">
      <label>Company<select value={ticker} onChange={event => setTicker(event.target.value)} disabled={listLoading}>
        <option value="">All companies</option>{tickers.map(value => <option key={value} value={value}>{value}</option>)}
      </select></label>
      <label>Results filing<select value={filing} onChange={event => { setFiling(event.target.value); setCard(null); }} disabled={listLoading || filings.length === 0}>
        {filings.length === 0 && <option value="">No filings available</option>}
        {filings.map(item => <option key={item.filing_id} value={item.filing_id}>{item.ticker} · {item.headline}</option>)}
      </select></label>
      <button className="results-load-button" onClick={loadCard} disabled={!filing || listLoading || cardLoading}>{cardLoading ? "Preparing…" : "Open results card"}</button>
    </div>

    <div className="results-card-body" aria-live="polite">
      {listLoading ? <div className="results-state"><span className="loader-ring"/><b>Loading company filings</b><small>Checking stored quarterly results.</small></div>
        : listError ? <div className="results-state results-error"><b>Results unavailable</b><small>{listError}</small><button onClick={() => setRetry(value => value + 1)}>Retry</button></div>
          : !filings.length ? <div className="results-state"><b>No results filings available</b><small>Store a verified company results filing to generate a cited card. FINN will not display sample financial values as company results.</small></div>
            : cardLoading ? <div className="results-state"><span className="loader-ring"/><b>Reading the filing</b><small>Extracting reported figures and validating source page citations.</small></div>
              : error ? <div className="results-state results-error"><b>Could not prepare this card</b><small>{error}</small><button onClick={loadCard}>Retry</button></div>
                : card?.parse_failed ? <div className="results-state results-error"><b>Filing could not be validated</b><small>Review the source filing before relying on extracted figures.</small><a href={card.source_url} target="_blank" rel="noreferrer">Open original filing</a></div>
                  : card ? <>
                    <div className="results-card-title"><div><span className="results-ticker">{card.ticker}</span><h3>{card.company_name}</h3><p>{current?.period_label ?? "Current quarter unavailable"} · {card.source_type === "fixture" ? "DEMO FIXTURE" : "Official filing"}</p></div><a href={card.source_url} target="_blank" rel="noreferrer">Open source filing ↗</a></div>
                    <div className="results-kpis">{displayMetric("Revenue", "revenue_from_operations")}{displayMetric("EBITDA", "ebitda")}{displayMetric("PAT", "profit_after_tax")}</div>
                    {card.what_stands_out?.length ? <div className="results-observation"><span>WHAT STANDS OUT</span>{card.what_stands_out.map((line, index) => <p key={index}>{line}</p>)}</div> : <div className="results-observation results-observation-empty"><span>WHAT STANDS OUT</span><p>Observation unavailable for this filing.</p></div>}
                    <details className="results-details"><summary>Financial details and source citations</summary>
                      <p>Preceding quarter: {card.periods?.preceding_quarter?.period_label ?? "Unavailable"} · Year ago: {card.periods?.corresponding_previous_year?.period_label ?? "Unavailable"}</p>
                      <div>{card.source_citations.map((citation, index) => <a key={`${citation.period_role}-${citation.field}-${index}`} href={`${card.source_url}#page=${citation.page}`} target="_blank" rel="noreferrer">{citation.field.replaceAll("_", " ")} · {citation.period_role.replaceAll("_", " ")} · p. {citation.page}</a>)}</div>
                    </details>
                    <small className="results-footnote">All amounts normalized to INR crore. EBITDA is marked derived when not explicitly reported. Snapshot as of {when(card.as_of)}.</small>
                  </> : <div className="results-state"><b>Select a results filing</b><small>Open a stored filing to extract and validate its financial results.</small></div>}
    </div>
  </section>;
}
