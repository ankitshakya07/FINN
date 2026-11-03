"use client";

import { useEffect, useState } from "react";
import { getAlerts, getDigest } from "@/lib/api";
import type { AlertsResponse, DigestResponse } from "@/lib/types";
import BriefFeed from "./brief-feed";
import AskSection from "./ask-section";
import WatchSection from "./watch-section";
import ResearchHub from "./research-hub";
import MobileBottomNav, { type MainTab } from "./mobile-bottom-nav";

type Range = "24h" | "3d" | "7d";
const nav = [
  ["Overview", "overview", "◫"],
  ["Brief Feed", "brief", "📰"],
  ["Ask AI", "ask", "💬"],
  ["Watch & Signals", "watch", "👁️"],
  ["Research Hub", "research-hub", "🔬"],
  ["Fundamentals", "fundamentals", "📈"],
  ["Promises", "promised-delivered", "⚖"],
  ["Results Cards", "results-card", "⌕"],
  ["Leadership", "management-changes", "↗"],
  ["Filings", "announcements", "A"],
  ["Alerts", "alerts", "◉"],
];
const time = (v: string) =>
  new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Asia/Kolkata",
  }).format(new Date(v));

export default function Home() {
  const [digest, setDigest] = useState<DigestResponse | null>(null);
  const [alerts, setAlerts] = useState<AlertsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [alertsError, setAlertsError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [range, setRange] = useState<Range>("24h");
  const [active, setActive] = useState("Overview");
  const [mobileTab, setMobileTab] = useState<MainTab>("brief");
  const [menuOpen, setMenuOpen] = useState(false);
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    let alive = true;
    setError(null);
    setLoading(true);
    getDigest({ window: range })
      .then((data) => {
        if (alive) setDigest(data);
      })
      .catch(() => {
        if (alive) setError("Could not reach the intelligence feed. Check the API connection and retry.");
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, [range, retry]);

  useEffect(() => {
    let alive = true;
    getAlerts()
      .then((data) => {
        if (alive) setAlerts(data);
      })
      .catch(() => {
        if (alive) setAlertsError("Could not reach the alerts service. Try again when the API is available.");
      });
    return () => {
      alive = false;
    };
  }, [retry]);

  const anomalies = digest?.items.filter((x) => x.kind === "anomaly") ?? [];
  const asOf = digest?.as_of ? time(digest.as_of) : null;

  const jump = (label: string, targetId?: string) => {
    setActive(label);
    setMenuOpen(false);

    // Sync mobile tab
    if (label.includes("Brief") || label === "Overview" || label === "Portfolio") {
      setMobileTab("brief");
    } else if (label.includes("Ask")) {
      setMobileTab("ask");
    } else if (label.includes("Watch")) {
      setMobileTab("watch");
    } else {
      setMobileTab("research");
    }

    if (targetId) {
      document.getElementById(targetId)?.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleMobileTabSelect = (tab: MainTab) => {
    setMobileTab(tab);
    const targetMap: Record<MainTab, string> = {
      brief: "brief",
      ask: "ask",
      watch: "watch",
      research: "research-hub",
    };
    const targetId = targetMap[tab];
    setActive(tab.toUpperCase());
    document.getElementById(targetId)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <main className="app-shell has-mobile-bottom-nav">
      <aside className={`sidebar ${menuOpen ? "sidebar-open" : ""}`}>
        <a className="brand" href="#overview" onClick={() => jump("Overview", "overview")}>
          <span className="brand-mark">f</span>
          <span>
            FINN<span className="brand-dot">.</span>
          </span>
        </a>
        <div className="workspace-label">WORKSPACE</div>
        <div className="workspace">
          <span className="workspace-avatar">E</span>
          <span>
            <b>Enam Holdings</b>
            <small>Institutional · India</small>
          </span>
          <span className="chevron">⌄</span>
        </div>
        <div className="nav-label">MAIN MENU</div>
        <nav className="main-nav" aria-label="Main navigation">
          {nav.map(([label, target, icon]) => (
            <a
              key={label}
              href={`#${target}`}
              className={`nav-item ${active === label ? "selected" : ""}`}
              aria-current={active === label ? "page" : undefined}
              onClick={() => jump(label, target)}
            >
              <span className="nav-icon">{icon}</span>
              {label}
              {label === "Alerts" && alerts?.alerts.length ? (
                <span className="nav-count">{alerts.alerts.length}</span>
              ) : null}
            </a>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="plan-card">
            <span className="plan-icon">✳</span>
            <b>Intelligence, in focus.</b>
            <p>Explore cited filings and company research.</p>
            <a href="#research-hub" onClick={() => jump("Research Hub", "research-hub")}>
              Explore research <span>→</span>
            </a>
          </div>
          <div className="profile">
            <span className="profile-avatar">AS</span>
            <span>
              <b>Arjun Shah</b>
              <small>Portfolio manager</small>
            </span>
          </div>
        </div>
      </aside>

      <section className="main-area" id="overview">
        <header className="topbar">
          <button
            className="mobile-menu"
            aria-label="Toggle navigation"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? "×" : "☰"}
          </button>
          <div className="breadcrumb">
            Workspace <span>/</span> <b>{active}</b>
          </div>
          <div className="topbar-actions">
            <span className={`mode-pill ${digest ? (!digest.demo_mode && (digest.total_count > 0 || (alerts && !alerts.demo_mode)) ? "live" : "demo") : "pending"}`}>
              {digest ? (!digest.demo_mode && (digest.total_count > 0 || (alerts && !alerts.demo_mode)) ? "LIVE MODE" : "DEMO MODE") : "CHECKING DATA"}
            </span>
            <a className="icon-button notification" href="#alerts" aria-label="Go to alerts">
              ♧{alerts?.alerts.length ? <span style={{ marginLeft: "4px", fontSize: "0.75rem", background: "#ef4444", color: "#fff", padding: "1px 6px", borderRadius: "10px" }}>{alerts.alerts.length}</span> : null}
            </a>
            <span className="top-avatar">AS</span>
          </div>
        </header>

        <div className="dashboard">
          {/* Welcome Strip */}
          <div className="welcome-row">
            <div>
              <div className="eyebrow">
                PORTFOLIO BRIEF <span className="eyebrow-line" />
              </div>
              <h1>
                Good morning, Arjun<span className="title-period">.</span>
              </h1>
              <p className="welcome-sub">A clear, evidence-backed view of your portfolio intelligence.</p>
            </div>
            <span className="date-button">
              ◷ <span>{range} window</span>
            </span>
          </div>

          <section className="market-strip" id="markets">
            <div className="market-heading">
              <span className="live-dot" /> MARKET DATA <span className="market-separator">·</span>
              <span>{digest ? (digest.demo_mode ? "DEMO" : "LIVE") : "PENDING"}</span>
            </div>
            <div className="market-unavailable">
              <b>Market quotes status</b>
              <span>Real-time NSE/BSE quotes with offline fallback and anomaly scanner enabled.</span>
            </div>
            <div className="market-asof">
              {asOf ? <>Digest response as of <b>{asOf}</b></> : "Waiting for API response"}
            </div>
          </section>

          {/* 1. Brief Pillar */}
          <div id="brief" className="pillar-anchor">
            <BriefFeed />
          </div>

          {error && digest ? (
            <div className="refresh-banner" role="status">
              <span>
                Showing the last successful {digest.window} response ({asOf}); the {range} refresh failed.
              </span>
              <button onClick={() => setRetry((x) => x + 1)}>Retry</button>
            </div>
          ) : loading && digest ? (
            <div className="refresh-banner" role="status">
              Updating the digest for {range}…
            </div>
          ) : null}

          {/* Portfolio & Signals Overview */}
          <div className="section-heading" id="portfolio">
            <div>
              <div className="section-kicker">YOUR PORTFOLIO</div>
              <h2>Portfolio intelligence</h2>
            </div>
            <a className="text-link" href="#portfolio" onClick={() => jump("Portfolio", "portfolio")}>
              View portfolio <span>→</span>
            </a>
          </div>

          <section className="overview-grid">
            <article className="card portfolio-card">
              <div className="card-top">
                <div>
                  <span className="label">PORTFOLIO VALUE</span>
                  <div className="portfolio-value portfolio-missing">Unavailable</div>
                  <div className="value-change">
                    <span>Position quantities are not configured in the current schema.</span>
                  </div>
                </div>
                <span className="snapshot-badge">
                  {digest?.demo_mode ? "DEMO RESPONSE" : digest ? "LIVE API" : "LOADING"}
                </span>
              </div>
              <div className="history-empty">
                <span className="history-icon">⌁</span>
                <b>Portfolio history is not available</b>
                <span>The database has no position quantities to calculate a portfolio value series.</span>
                <small>{asOf ? `Digest response as of ${asOf}` : "Waiting for the digest response"}</small>
              </div>
              <div className="chart-footer">
                <span>Historical values require configured holdings and price history.</span>
              </div>
            </article>

            <article className="card allocation-card">
              <div className="card-heading">
                <div>
                  <span className="label">ALLOCATION</span>
                  <h3>Holdings mix</h3>
                </div>
                <span className="snapshot-badge">UNAVAILABLE</span>
              </div>
              <div className="allocation-empty">
                <span className="calm-icon">▤</span>
                <b>Holdings data unavailable</b>
                <p>No portfolio positions are configured. Holdings and allocation are intentionally left blank.</p>
              </div>
              <div className="allocation-foot">
                <span>Portfolio positions</span>
                <b>Not configured</b>
              </div>
            </article>
          </section>

          <section className="lower-grid">
            <div className="holdings-panel" id="positions">
              <div className="section-heading compact">
                <div>
                  <div className="section-kicker">EXPOSURE</div>
                  <h2>Largest positions</h2>
                </div>
                <a className="text-link" href="#positions" onClick={() => jump("Portfolio", "positions")}>
                  All holdings <span>→</span>
                </a>
              </div>
              <div className="card holdings-card">
                <div className="holdings-empty">
                  <span className="calm-icon">▤</span>
                  <b>No holdings to display</b>
                  <p>Holdings require portfolio positions with quantities. This workspace has none configured.</p>
                </div>
              </div>
            </div>

            <div className="intel-column">
              <div className="section-heading compact">
                <div>
                  <div className="section-kicker">SIGNALS</div>
                  <h2>Worth your attention</h2>
                </div>
                <div className="signals-controls">
                  <div className="range-control" aria-label="Digest time window">
                    {(["24h", "3d", "7d"] as const).map((x) => (
                      <button
                        aria-pressed={range === x}
                        className={range === x ? "range-active" : ""}
                        key={x}
                        onClick={() => setRange(x)}
                      >
                        {x}
                      </button>
                    ))}
                  </div>
                  <span className="signal-count">{digest ? anomalies.length : "—"}</span>
                </div>
              </div>
              <div className="card signals-card">
                {error && !digest ? (
                  <div className="feed-state error-state">
                    <span className="state-symbol">!</span>
                    <b>Intelligence feed unavailable</b>
                    <p>{error}</p>
                    <button onClick={() => setRetry((x) => x + 1)}>
                      Try again <span>→</span>
                    </button>
                  </div>
                ) : !digest ? (
                  <div className="feed-state loading-state">
                    <span className="loader-ring" />
                    <b>Loading portfolio signals</b>
                    <p>Requesting the {range} digest window…</p>
                  </div>
                ) : anomalies.length ? (
                  <article className="signal-item">
                    <span className="signal-icon">?</span>
                    <div>
                      <div className="signal-meta">
                        <b>{anomalies.length} anomaly records</b>
                        <span>ranked in the Brief</span>
                      </div>
                      <h3>Price and volume signals</h3>
                      <p>Open Watch & Signals to monitor price outliers and adjust statistical thresholds.</p>
                      <a href="#watch" onClick={() => jump("Watch & Signals", "watch")}>
                        Open Watch signals →
                      </a>
                    </div>
                  </article>
                ) : (
                  <div className="feed-state empty-state">
                    <span className="calm-icon">✓</span>
                    <b>No anomalies in this response</b>
                    <p>
                      {digest.demo_mode
                        ? "The demo response contains no anomaly records."
                        : "No anomaly records were returned for this window."}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* 2. Ask AI Pillar */}
          <AskSection />

          {/* 3. Watch Pillar */}
          <WatchSection
            onAskTicker={(ticker, question) => {
              jump("Ask AI", "ask");
            }}
            onExploreResearch={(ticker) => {
              jump("Research Hub", "research-hub");
            }}
          />

          {/* 4. Research Hub Pillar (Hosts all 6 research modules with tab switching) */}
          <ResearchHub />

          {/* Alerts Section */}
          <section className="alerts-section" id="alerts">
            <div className="section-heading compact">
              <div>
                <div className="section-kicker">ALERTS</div>
                <h2>Portfolio notifications</h2>
                {alerts?.as_of && (
                  <p className="asof-line">
                    {alerts.demo_mode ? "Demo API response" : "API response"} as of {time(alerts.as_of)}
                  </p>
                )}
              </div>
              <span className={`snapshot-badge ${alerts && !alerts.demo_mode ? "mode-live-badge" : ""}`}>
                {alerts ? (alerts.demo_mode ? "DEMO MODE" : "LIVE MODE") : "LOADING"}
              </span>
            </div>
            <div className="card alerts-card">
              {alertsError ? (
                <div className="feed-state error-state">
                  <b>Alerts unavailable</b>
                  <p>{alertsError}</p>
                  <button
                    onClick={() => {
                      setAlertsError(null);
                      setRetry((x) => x + 1);
                    }}
                  >
                    Try again
                  </button>
                </div>
              ) : !alerts ? (
                <div className="research-state">
                  <span className="loader-ring" /> Loading alerts…
                </div>
              ) : alerts.alerts.length ? (
                alerts.alerts.map((alert) => (
                  <article className="alert-row" key={alert.id}>
                    <span className="signal-icon">◉</span>
                    <div>
                      <div className="signal-meta">
                        <b>{alert.ticker}</b>
                        <span>{alert.alert_type.replace("_", " ")}</span>
                      </div>
                      <h3>{alert.title}</h3>
                      <p>{alert.message}</p>
                      <small>{time(alert.triggered_at)}</small>
                    </div>
                  </article>
                ))
              ) : (
                <div className="feed-state empty-state">
                  <span className="calm-icon">✓</span>
                  <b>No alerts in this response</b>
                  <p>{alerts.demo_mode ? "No demo alert fixture is installed." : "The API returned no alerts."}</p>
                </div>
              )}
            </div>
          </section>

          <footer className="dashboard-footer">
            <span>
              FINN <b>·</b> Evidence first. Always.
            </span>
            <span>
              {asOf ? `${digest?.demo_mode ? "Demo API response" : "API response"} as of ${asOf}` : "Response timestamp unavailable"}
              <span className="footer-divider"> · </span>Market surveillance active
            </span>
          </footer>
        </div>
      </section>

      {/* Unified Mobile Bottom Navigation */}
      <MobileBottomNav
        activeTab={mobileTab}
        onSelectTab={handleMobileTabSelect}
        anomaliesCount={anomalies.length}
      />
    </main>
  );
}

