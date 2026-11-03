"use client";

import { useEffect, useMemo, useState } from "react";
import { getAnnouncements } from "@/lib/api";
import type { AnnouncementCategory, AnnouncementListResponse } from "@/lib/types";

const categories: AnnouncementCategory[] = ["results", "M&A", "fund_raise", "management_change", "litigation", "insider_trading", "earnings_call", "investor_meetings", "credit_rating", "dividend", "bonus_split", "capex", "press_release", "postal_ballot", "agm_egm", "pledging", "unclassified"];
const formatTime = (value: string) => new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short", timeZone: "Asia/Kolkata" }).format(new Date(value));

export default function AnnouncementsSection() {
  const [data, setData] = useState<AnnouncementListResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [ticker, setTicker] = useState("");
  const [category, setCategory] = useState<AnnouncementCategory | "">("");
  const [highOnly, setHighOnly] = useState(false);
  const [retry, setRetry] = useState(0);
  const tickers = useMemo(() => Array.from(new Set((data?.announcements ?? []).map(x => x.ticker))).sort(), [data]);

  useEffect(() => {
    const selectCompany = (event: Event) => {
      const ticker = (event as CustomEvent<string>).detail;
      if (ticker) setTicker(ticker.toUpperCase());
    };
    window.addEventListener("finn:company-research", selectCompany);
    return () => window.removeEventListener("finn:company-research", selectCompany);
  }, []);

  useEffect(() => {
    let alive = true;
    setError(null); setLoading(true);
    getAnnouncements({ ticker: ticker || undefined, category: category || undefined, minMateriality: highOnly ? 5 : undefined, highMateriality: highOnly, limit: 100 })
      .then(result => { if (alive) setData(result); })
      .catch(() => { if (alive) setError("Could not load corporate announcements. Check the API connection and retry."); })
      .finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, [ticker, category, highOnly, retry]);

  return <section className="announcements-section" id="announcements">
    <div className="section-heading compact"><div><div className="section-kicker">EXCHANGE FILINGS</div><h2>Corporate announcements</h2><p className="asof-line">{data ? `${data.demo_mode ? "Demo snapshot" : "API snapshot"} as of ${formatTime(data.as_of)} · ${data.count} records` : "Awaiting announcement snapshot"}</p></div><span className={`snapshot-badge ${data && !data.demo_mode ? "mode-live-badge" : ""}`}>{data ? data.demo_mode ? "DEMO DATA" : "LIVE SOURCES" : "CHECKING"}</span></div>
    <div className="announcement-filters">
      <label>Ticker<select value={ticker} onChange={event => setTicker(event.target.value)}><option value="">All tickers</option>{tickers.map(value => <option key={value} value={value}>{value}</option>)}</select></label>
      <label>Category<select value={category} onChange={event => setCategory(event.target.value as AnnouncementCategory | "")}><option value="">All categories</option>{categories.map(value => <option key={value} value={value}>{value.replaceAll("_", " ")}</option>)}</select></label>
      <label className="announcement-high-filter"><input type="checkbox" checked={highOnly} onChange={event => setHighOnly(event.target.checked)} /> High materiality <span>≥ 5</span></label>
    </div>
    <div className="announcement-list" aria-live="polite">
      {loading && !data ? <div className="feed-state"><span className="loader-ring"/><b>Loading announcements</b><p>Requesting the stored exchange snapshot…</p></div>
        : error && !data ? <div className="feed-state error-state"><span className="state-symbol">!</span><b>Announcements unavailable</b><p>{error}</p><button onClick={() => setRetry(value => value + 1)}>Retry</button></div>
          : !data?.announcements.length ? <div className="feed-state empty-state"><span className="calm-icon">✓</span><b>No announcements match these filters</b><p>{data?.demo_mode ? "The demo snapshot has no records for this selection." : "No stored announcements match this selection."}</p></div>
            : data.announcements.map(item => <article className="announcement-row" key={item.id}>
              <div className="announcement-topline"><div className="announcement-company"><b>{item.ticker}</b><span>{item.company_name}</span></div><div className="announcement-badges"><span className="announcement-category">{item.classification.replaceAll("_", " ")}</span><span className="materiality-score">{item.materiality_score.toFixed(0)}<small>/10</small></span></div></div>
              <h3>{item.headline}</h3>{item.summary && <p className="announcement-summary">{item.summary}</p>}
              <div className="announcement-meta"><span>{formatTime(item.timestamp)}</span><span className="source-tag">{item.source === "fixture" ? "DEMO FIXTURE" : item.source.toUpperCase()}</span><span>{item.classification_method === "model" ? "Model assisted" : "Rule classified"}</span>{item.attachment_url && <a href={item.attachment_url} target="_blank" rel="noreferrer">Open attachment ↗</a>}</div>
            </article>)}
      {loading && data && <div className="announcement-refreshing">Updating filtered results…</div>}
      {error && data && <div className="announcement-refreshing error-inline">Refresh failed; showing the last successful response. <button onClick={() => setRetry(value => value + 1)}>Retry</button></div>}
    </div>
  </section>;
}
