"use client";

import { useEffect, useState, type MouseEvent } from "react";
import { getDigest } from "@/lib/api";
import type { DigestItem, DigestResponse } from "@/lib/types";

const categories = ["results", "M&A", "fund_raise", "management_change", "litigation", "insider_trading", "earnings_call", "investor_meetings", "credit_rating", "dividend", "bonus_split", "capex", "press_release", "postal_ballot", "agm_egm", "pledging", "unclassified", "price_volume_anomaly", "price_anomaly", "volume_anomaly", "results_card"];
const formatTime = (value: string) => new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short", timeZone: "Asia/Kolkata" }).format(new Date(value));
const label = (value: string) => value.replaceAll("_", " ");

function BriefCard({ item }: { item: DigestItem }) {
  const companyResearch = (_event: MouseEvent<HTMLAnchorElement>) => {
    window.dispatchEvent(new CustomEvent("finn:company-research", { detail: item.ticker }));
  };
  const detailEntries = Object.entries(item.supporting_details ?? {}).filter(([, value]) => value !== null && value !== undefined && value !== "");
  return <article className={`card brief-card ${item.priority === "high" ? "brief-card-high" : ""}`}>
    <div className="brief-card-top">
      <a className="brief-company" href="#announcements" onClick={companyResearch} title="Open company research">
        <span className="ticker-tag">{item.ticker}</span><span>{item.company_name}</span>
      </a>
      <div className="brief-score">{item.materiality_score === null ? <span>Materiality unavailable</span> : <>Materiality <b>{item.materiality_score.toFixed(1)}</b>/10</>}</div>
    </div>
    <div className="brief-meta"><span className="brief-category">{label(item.category)}</span><span className={`priority-tag priority-${item.priority}`}>{item.priority} priority</span><span className={`brief-origin ${item.demo_mode ? "brief-origin-demo" : "brief-origin-live"}`}>{item.demo_mode ? "DEMO" : "LIVE"} · {item.data_source}</span><time dateTime={item.occurred_at}>{formatTime(item.occurred_at)}</time></div>
    <h3>{item.headline}</h3>
    <p className="brief-observation">{item.summary}</p>
    {item.collapsed_count > 1 && <span className="brief-group-count">{item.collapsed_count} related disclosures grouped</span>}
    <div className="brief-card-actions">
      {item.attachment_url && /^https?:\/\//i.test(item.attachment_url)
        ? <a className="brief-source-link" href={item.attachment_url} target="_blank" rel="noreferrer">Open source filing <span>↗</span></a>
        : <span className="brief-source-missing">{item.source_reference ? `Source reference: ${item.source_reference}` : "Source link unavailable"}</span>}
      <details className="brief-details"><summary>Supporting details</summary>
        <div className="brief-detail-content"><p>Source: {item.data_source}{item.demo_mode ? " · DEMO fixture" : " · LIVE source"}</p>
          <p>Rank factors: {item.rank_reasons.length ? item.rank_reasons.join(" · ") : "Not available"}</p>
          {item.citations.length > 0 && <ul>{item.citations.map((citation, index) => <li key={`${citation.document}-${index}`}>{citation.document} · {citation.locator}{citation.quote ? ` — ${citation.quote}` : ""}</li>)}</ul>}
          {detailEntries.map(([key, value]) => <p key={key}><b>{label(key)}:</b> {typeof value === "string" ? value : JSON.stringify(value)}</p>)}
        </div>
      </details>
      <a className="brief-research-link" href="#announcements" onClick={companyResearch}>Company research →</a>
    </div>
  </article>;
}

export default function BriefFeed() {
  const [data, setData] = useState<DigestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ticker, setTicker] = useState("");
  const [tickerQuery, setTickerQuery] = useState("");
  const [category, setCategory] = useState("");
  const [minMateriality, setMinMateriality] = useState("");
  const [timeWindow, setTimeWindow] = useState<"24h" | "3d" | "7d">("24h");
  const [sort, setSort] = useState<"relevance" | "recency">("relevance");
  const [offset, setOffset] = useState(0);
  const [retry, setRetry] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = window.setTimeout(() => { setTicker(tickerQuery.trim().toUpperCase()); setOffset(0); }, 250);
    return () => window.clearTimeout(timer);
  }, [tickerQuery]);

  useEffect(() => {
    let alive = true;
    setLoading(true); setError(null);
    getDigest({ window: timeWindow, ticker: ticker || undefined, category: category || undefined,
      minMateriality: minMateriality === "" ? undefined : Number(minMateriality), limit: 20, offset, sort })
      .then((response) => {
        if (!alive) return;
        setData((previous) => offset === 0 || !previous ? response : {
          ...response, items: [...previous.items, ...response.items.filter((item) => !previous.items.some((old) => old.id === item.id))]
        });
      })
      .catch((cause: unknown) => {
        if (alive) setError(cause instanceof TypeError ? "FINN could not reach the API. Check your connection and retry." : "The Brief service returned an error. Your last successful items remain available.");
      })
      .finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, [timeWindow, ticker, category, minMateriality, sort, offset, retry]);

  const filterChanged = (callback: () => void) => { callback(); setOffset(0); };
  const hasFilters = Boolean(ticker || category || minMateriality);
  const remaining = data ? Math.max(0, data.total_count - data.items.length) : 0;

  return <section className="brief-section" id="brief" aria-labelledby="brief-heading">
    <div className="section-heading brief-heading">
      <div><div className="section-kicker">FINN INTELLIGENCE</div><h2 id="brief-heading">Your Brief</h2><p className="brief-asof">{data ? `${data.demo_mode ? "Demo snapshot" : "Live sources"} · As of ${formatTime(data.as_of)}${data.last_refresh ? ` · Refreshed ${formatTime(data.last_refresh)}` : ""}` : "Checking source freshness…"}</p></div>
      <div className="brief-heading-actions"><span className={`snapshot-badge ${data && !data.demo_mode ? "mode-live-badge" : ""}`}>{data ? data.demo_mode ? "DEMO DATA" : "LIVE DATA" : "CHECKING"}</span><button className="brief-refresh" type="button" onClick={() => setRetry((value) => value + 1)} disabled={loading} aria-label="Refresh brief">↻ Refresh</button></div>
    </div>
    <div className="brief-filters" aria-label="Brief filters">
      <label>Ticker<input value={tickerQuery} onChange={(event) => setTickerQuery(event.target.value)} placeholder="All companies" maxLength={24}/></label>
      <label>Category<select value={category} onChange={(event) => filterChanged(() => setCategory(event.target.value))}><option value="">All categories</option>{categories.map((value) => <option key={value} value={value}>{label(value)}</option>)}</select></label>
      <label>Minimum materiality<select value={minMateriality} onChange={(event) => filterChanged(() => setMinMateriality(event.target.value))}><option value="">Any / unavailable</option><option value="3">3+</option><option value="5">5+</option><option value="7">7+</option></select></label>
      <label>Time window<select value={timeWindow} onChange={(event) => filterChanged(() => setTimeWindow(event.target.value as "24h" | "3d" | "7d"))}><option value="24h">24 hours</option><option value="3d">3 days</option><option value="7d">7 days</option></select></label>
      <label>Sort<select value={sort} onChange={(event) => filterChanged(() => setSort(event.target.value as "relevance" | "recency"))}><option value="relevance">Relevance</option><option value="recency">Most recent</option></select></label>
    </div>
    {error && <div className="brief-error" role="status"><span>{error}</span><button type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></div>}
    {loading && !data ? <div className="brief-skeletons" aria-label="Loading brief"><div/><div/><div/></div>
      : !data ? <div className="card feed-state empty-state"><span className="state-symbol">!</span><b>Brief unavailable</b><p>{error ?? "No response from the intelligence service."}</p><button type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></div>
      : data.items.length === 0 ? <div className="card feed-state empty-state"><span className="calm-icon">⌕</span><b>{hasFilters ? "No events match these filters" : data.status === "never_refreshed" ? "No intelligence yet" : data.status === "source_unavailable" ? "Source unavailable" : "No intelligence in this window"}</b><p>{hasFilters ? "Try broadening your category or materiality filters." : data.status === "never_refreshed" ? "Last refresh: never. Live market announcements have not been ingested yet." : data.status === "source_unavailable" ? `External sources unavailable. Last refresh: ${data.last_refresh ? formatTime(data.last_refresh) : "never"}.` : `No source-backed events were returned for this time window. Last refresh: ${data.last_refresh ? formatTime(data.last_refresh) : "never"}.`}</p></div>
      : <div className="brief-feed" aria-live="polite">{data.items.map((item) => <BriefCard key={item.id} item={item}/>)}</div>}
    {loading && data && <div className="brief-refreshing" role="status">Updating your Brief…</div>}
    {data && remaining > 0 && <button type="button" className="brief-load-more" disabled={loading} onClick={() => setOffset(data.offset + data.limit)}>Load more · {remaining} remaining</button>}
    {data && data.collapsed_count > 0 && <p className="brief-collapsed-note">{data.collapsed_count} routine or duplicate events were collapsed.</p>}
  </section>;
}
