"use client";

import React, { useEffect, useState } from "react";
import { getAlerts, getAnomalies, getPortfolio, saveAlertConfig } from "../src/lib/api";
import type { Alert, AlertsResponse, AnomaliesResponse, Anomaly, PortfolioItem, PortfolioResponse } from "../src/lib/types";

interface WatchSectionProps {
  onAskTicker?: (ticker: string, question?: string) => void;
  onExploreResearch?: (ticker: string) => void;
}

export default function WatchSection({ onAskTicker, onExploreResearch }: WatchSectionProps) {
  const [selectedTicker, setSelectedTicker] = useState<string>("ALL");
  const [volX, setVolX] = useState<number>(2.0);
  const [pct, setPct] = useState<number>(3.0);
  const [portfolioData, setPortfolioData] = useState<PortfolioResponse | null>(null);
  const [anomaliesData, setAnomaliesData] = useState<AnomaliesResponse | null>(null);
  const [alertsData, setAlertsData] = useState<AlertsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [scanning, setScanning] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [retry, setRetry] = useState<number>(0);

  // Load portfolio, anomalies and alerts
  const loadData = async (tickerFilter?: string, currentVolX = volX, currentPct = pct) => {
    setScanning(true);
    setError(null);
    try {
      const tickerParam = !tickerFilter || tickerFilter === "ALL" ? undefined : tickerFilter;
      const [anomRes, alertRes, portRes] = await Promise.all([
        getAnomalies({ ticker: tickerParam, vol_x: currentVolX, pct: currentPct }),
        getAlerts(),
        getPortfolio(),
      ]);
      setAnomaliesData(anomRes);
      setAlertsData(alertRes);
      setPortfolioData(portRes);
    } catch (err: unknown) {
      console.error("Failed to load watch intelligence", err);
      setError("Unable to connect to market quote service. Check your connection and retry.");
    } finally {
      setScanning(false);
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(selectedTicker, volX, pct);
  }, [selectedTicker, retry]);

  const handleApplyThresholds = () => {
    loadData(selectedTicker, volX, pct);
  };

  const handleSaveAlertRule = async (ticker: string) => {
    try {
      await saveAlertConfig({
        ticker,
        enabled: true,
        announcement_categories: ["management_change", "results", "M&A", "dividend"],
        price_move_pct: pct,
        volume_multiple: volX,
        notify_on_high_priority: true,
      });
      setSaveSuccess(`Alert trigger configured for ${ticker} (>${pct}% move, >${volX}x volume)`);
      setTimeout(() => setSaveSuccess(null), 4000);
      loadData(selectedTicker, volX, pct);
    } catch (err) {
      console.error("Failed to save alert rule", err);
    }
  };

  const anomaliesList: Anomaly[] = anomaliesData?.anomalies || [];
  const alertsList: Alert[] = alertsData?.alerts || [];
  const companiesList: PortfolioItem[] = portfolioData?.companies || [];

  return (
    <section id="watch" className="section-container watch-section">
      <div className="section-header-compact">
        <div className="header-meta">
          <span className="badge badge-accent">Monitoring & Signals</span>
          <span className="timestamp">Active Surveillance</span>
        </div>
        <h2 className="section-title">Watchlist & Market Anomalies</h2>
        <p className="section-subtitle">
          Real-time price breakouts, volume surges, and corporate signals against 20-day statistical baselines.
        </p>
      </div>

      {saveSuccess && (
        <div className="watch-toast-success" role="status">
          <span className="toast-icon">✓</span>
          <span>{saveSuccess}</span>
        </div>
      )}

      {error ? (
        <div className="card feed-state error-state" style={{ margin: "16px 0", padding: "20px" }}>
          <b>Market Data Unavailable</b>
          <p>{error}</p>
          <button type="button" className="scan-btn" onClick={() => setRetry((x) => x + 1)} style={{ marginTop: "12px", width: "auto" }}>
            ↻ Retry Connection
          </button>
        </div>
      ) : loading && !portfolioData ? (
        <div className="watchlist-cards-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="watchlist-item-card" style={{ opacity: 0.6 }}>
              <div className="progress-spinner" style={{ margin: "20px auto" }} />
            </div>
          ))}
        </div>
      ) : companiesList.length === 0 ? (
        <div className="card feed-state empty-state" style={{ margin: "16px 0", padding: "24px", textAlign: "center" }}>
          <span className="calm-icon">⌕</span>
          <b>No price data yet</b>
          <p>Last refresh: never. Run data ingestion to populate watchlist quotes.</p>
        </div>
      ) : (
        /* Watchlist Quick-Grid from real API */
        <div className="watchlist-cards-grid">
          {companiesList.map((company) => {
            const isPositive = (company.change_pct ?? 0) >= 0;
            const isSelected = selectedTicker === company.ticker;
            const hasAnomaly = anomaliesList.some((a) => a.ticker === company.ticker);

            return (
              <div
                key={company.ticker}
                className={`watchlist-item-card ${isSelected ? "selected" : ""} ${hasAnomaly ? "anomaly-flagged" : ""}`}
                onClick={() => setSelectedTicker(selectedTicker === company.ticker ? "ALL" : company.ticker)}
              >
                <div className="watchlist-card-top">
                  <div className="watchlist-ticker-group">
                    <span className="watchlist-ticker">{company.ticker}</span>
                    <span className="watchlist-sector">{company.sector || "Equities"}</span>
                  </div>
                  <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                    {company.is_stale && (
                      <span className="anomaly-pill" style={{ background: "#713f12", color: "#fef08a" }} title="Quote is older than 4 calendar days">
                        Stale
                      </span>
                    )}
                    {hasAnomaly ? (
                      <span className="anomaly-pill">⚠ Signal</span>
                    ) : (
                      <span className="normal-pill">Normal</span>
                    )}
                  </div>
                </div>

                <div className="watchlist-card-mid">
                  <span className="watchlist-price">
                    {company.latest_close !== null
                      ? `₹${company.latest_close.toLocaleString("en-IN", { minimumFractionDigits: 1, maximumFractionDigits: 2 })}`
                      : "—"}
                  </span>
                  <span className={`watchlist-change ${company.change_pct === null ? "" : isPositive ? "up" : "down"}`}>
                    {company.change_pct !== null
                      ? `${isPositive ? "+" : ""}${company.change_pct.toFixed(2)}%`
                      : "—"}
                  </span>
                </div>

                <div className="watchlist-card-bot">
                  <span className="vol-stat">
                    Vol Multiple: <b>{company.vol_ratio_20d !== null ? `${company.vol_ratio_20d.toFixed(2)}x` : "—"}</b>
                    {company.source && (
                      <small style={{ display: "block", color: "#9ca3af", fontSize: "0.75rem", marginTop: "2px" }}>
                        {company.source} · {company.as_of_date || "—"}
                      </small>
                    )}
                  </span>
                  <button
                    type="button"
                    className="quick-rule-btn"
                    title="Configure alert triggers"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSaveAlertRule(company.ticker);
                    }}
                  >
                    + Alert Rule
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Threshold Controller Panel */}
      <div className="watch-controls-panel">
        <div className="controls-header">
          <span className="controls-title">Anomaly Scanner Configuration</span>
          <span className="controls-hint">Adjust triggers to filter market noise</span>
        </div>

        <div className="controls-row">
          {/* Volume Threshold */}
          <div className="control-group">
            <label className="control-label">
              Volume Multiplier: <b className="val-display">{volX.toFixed(1)}x</b>
            </label>
            <div className="preset-chips">
              {[1.5, 2.0, 2.5, 3.0].map((v) => (
                <button
                  key={v}
                  type="button"
                  className={`preset-chip ${volX === v ? "active" : ""}`}
                  onClick={() => setVolX(v)}
                >
                  {v.toFixed(1)}x
                </button>
              ))}
            </div>
          </div>

          {/* Price Move Threshold */}
          <div className="control-group">
            <label className="control-label">
              Price Move: <b className="val-display">{pct.toFixed(1)}%</b>
            </label>
            <div className="preset-chips">
              {[2.0, 3.0, 5.0, 8.0].map((p) => (
                <button
                  key={p}
                  type="button"
                  className={`preset-chip ${pct === p ? "active" : ""}`}
                  onClick={() => setPct(p)}
                >
                  ±{p.toFixed(0)}%
                </button>
              ))}
            </div>
          </div>

          {/* Action button */}
          <div className="control-action">
            <button
              type="button"
              className="scan-btn"
              onClick={handleApplyThresholds}
              disabled={scanning}
            >
              {scanning ? "Scanning Baselines..." : "Apply Thresholds ↻"}
            </button>
          </div>
        </div>
      </div>

      {/* Anomalies Results List */}
      <div className="anomalies-feed-section">
        <div className="sub-header">
          <h3 className="sub-title">
            Detected Anomalies ({anomaliesList.length})
            {selectedTicker !== "ALL" && <span className="filter-tag"> · {selectedTicker}</span>}
          </h3>
          <span className="sub-provenance">
            Baseline: 20-Session Moving Average · {anomaliesData?.demo_mode ? "Demo Provenance" : "Live Market"}
          </span>
        </div>

        {loading ? (
          <div className="watch-loading-card">
            <div className="progress-spinner" />
            <span>Scanning session history for unusual market activity...</span>
          </div>
        ) : anomaliesList.length === 0 ? (
          <div className="watch-empty-card">
            <span className="calm-icon">✓</span>
            <div className="empty-title">No Statistical Anomalies at Current Thresholds</div>
            <p className="empty-desc">
              All monitored sessions for {selectedTicker === "ALL" ? "the portfolio" : selectedTicker} traded within {volX}x volume and ±{pct}% price range. Lower thresholds above to increase sensitivity.
            </p>
          </div>
        ) : (
          <div className="anomalies-grid">
            {anomaliesList.map((anom, idx) => {
              const isVolume = anom.anomaly_type === "volume_spike";
              const isPrice = anom.anomaly_type === "price_move";
              const isPositive = anom.observed_value >= 0;

              return (
                <article key={idx} className="anomaly-card">
                  <div className="anomaly-card-top">
                    <div className="anom-ticker-date">
                      <span className="anom-ticker">{anom.ticker}</span>
                      <span className="anom-date">
                        {new Date(anom.detected_at).toLocaleDateString("en-IN", { month: "short", day: "numeric" })}
                      </span>
                    </div>
                    <div className="anom-tags">
                      {isVolume && (
                        <span className="anom-tag tag-volume">
                          Vol Surge {anom.observed_value.toFixed(2)}x
                        </span>
                      )}
                      {isPrice && (
                        <span className={`anom-tag ${isPositive ? "tag-bull" : "tag-bear"}`}>
                          {isPositive ? "▲" : "▼"} Move {anom.observed_value.toFixed(2)}%
                        </span>
                      )}
                    </div>
                  </div>

                  <p className="anomaly-reason">
                    {anom.explanation}
                  </p>

                  <div className="anomaly-metrics-strip">
                    <div className="metric-box">
                      <span className="m-label">Observed</span>
                      <span className="m-val">{anom.observed_value.toFixed(2)}{anom.unit}</span>
                    </div>
                    <div className="metric-box">
                      <span className="m-label">Threshold</span>
                      <span className="m-val">{anom.threshold_value.toFixed(2)}{anom.unit}</span>
                    </div>
                    <div className="metric-box">
                      <span className="m-label">Type</span>
                      <span className="m-val">{anom.anomaly_type.replace(/_/g, " ")}</span>
                    </div>
                  </div>

                  <div className="anomaly-actions">
                    <a
                      href="#ask"
                      className="anom-action-btn"
                      onClick={() => onAskTicker?.(anom.ticker, `Explain the recent volume surge and price move for ${anom.ticker}`)}
                    >
                      💬 Ask AI About Move
                    </a>
                    <a
                      href="#research"
                      className="anom-action-btn-secondary"
                      onClick={() => onExploreResearch?.(anom.ticker)}
                    >
                      🔬 Explore Research
                    </a>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </div>

      {/* Triggered Alerts & Rule History */}
      {alertsList.length > 0 && (
        <div className="watch-alerts-history">
          <div className="sub-header">
            <h3 className="sub-title">Active Alert Triggers ({alertsList.length})</h3>
            <span className="sub-provenance">Push Notifications & Notification Center</span>
          </div>
          <div className="alerts-history-list">
            {alertsList.map((alt) => (
              <div key={alt.id} className="alert-history-item">
                <span className="alert-icon">◉</span>
                <div className="alert-content">
                  <div className="alert-top">
                    <span className="alert-ticker">{alt.ticker}</span>
                    <span className="alert-type">{alt.alert_type.replace(/_/g, " ")}</span>
                    <span className="alert-time">
                      {new Date(alt.triggered_at).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                  <div className="alert-title">{alt.title}</div>
                  <p className="alert-desc">{alt.message || alt.reason}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
