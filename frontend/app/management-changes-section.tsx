"use client";

import { useEffect, useState } from "react";
import { getManagementChanges } from "@/lib/api";
import type { ManagementChangesResponse } from "@/lib/types";

const displayDate = (value: string | null) => value ? new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeZone: "Asia/Kolkata" }).format(new Date(value)) : "Not disclosed";

export default function ManagementChangesSection() {
  const [data, setData] = useState<ManagementChangesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ticker, setTicker] = useState("");
  const [refresh, setRefresh] = useState(0);
  useEffect(() => {
    let active = true;
    setData(null); setError(null);
    getManagementChanges({ ticker: ticker.trim() || undefined }).then(value => { if (active) setData(value); })
      .catch(() => { if (active) setError("Management-change data is unavailable. Check the API connection and retry."); });
    return () => { active = false; };
  }, [ticker, refresh]);

  return <section className="management-section" id="management-changes">
    <div className="section-heading compact">
      <div><div className="section-kicker">LEADERSHIP &amp; BOARD</div><h2>Management changes</h2></div>
      <span className={`snapshot-badge ${data && !data.demo_mode ? "mode-live-badge" : ""}`}>{data ? data.demo_mode ? "DEMO DATA" : "LIVE DATA" : "CHECKING"}</span>
    </div>
    <div className="management-toolbar"><label htmlFor="management-ticker">Company ticker</label><input id="management-ticker" value={ticker} onChange={event => setTicker(event.target.value.toUpperCase())} placeholder="All companies" maxLength={24} /></div>
    {error ? <div className="card feed-state error-state"><b>Management changes unavailable</b><p>{error}</p><button onClick={() => setRefresh(value => value + 1)}>Try again</button></div>
      : !data ? <div className="card research-state"><span className="loader-ring"/> Loading management changes…</div>
      : data.events.length === 0 ? <div className="card feed-state empty-state"><span className="calm-icon">✓</span><b>No management changes found</b><p>{data.demo_mode ? "No matching announcement-derived events are available in this demo snapshot." : "No events match this ticker filter."}</p></div>
      : <div className="management-grid">{data.events.map(event => <article className="card management-card" key={event.id}>
        <div className="management-card-top"><span className="ticker-tag">{event.ticker}</span><span className="management-score">Materiality <b>{event.materiality_score.toFixed(1)}</b>/10</span></div>
        <h3>{event.person_name ?? "Name not identified in filing"}</h3>
        <div className="management-designation">{event.new_designation ?? event.role_category.replaceAll("_", " ")} · {event.company_name}</div>
        <div className="management-tags"><span>{event.change_type.replaceAll("_", " ")}</span><span>{event.extraction_status}</span></div>
        <p>{event.explanation}</p>
        <div className="management-dates"><span>Effective <b>{displayDate(event.effective_date)}</b></span><span>Announced <b>{displayDate(event.announced_at)}</b></span></div>
        {event.reason && <p className="management-reason">Disclosed reason: {event.reason}</p>}
        {event.attachment_url ? <a className="management-source" href={event.attachment_url} target="_blank" rel="noreferrer">Open original filing <span>↗</span></a> : <span className="management-source-unavailable">Original attachment link unavailable</span>}
      </article>)}</div>}
  </section>;
}
