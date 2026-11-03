"use client";

import React, { useEffect, useMemo, useState } from "react";
import { getCommitments } from "../src/lib/api";
import type {
  CommitmentCategory,
  CommitmentRecord,
  CommitmentStatus,
  CompanyCommitmentsResponse,
} from "../src/lib/types";

const COMPANIES = [
  { ticker: "INFY", name: "Infosys Ltd" },
  { ticker: "TCS", name: "Tata Consultancy Services" },
  { ticker: "RELIANCE", name: "Reliance Industries" },
  { ticker: "HDFCBANK", name: "HDFC Bank" },
];

const CATEGORY_LABELS: Record<string, string> = {
  all: "All Categories",
  revenue_growth: "Revenue Growth",
  margin: "Margins & Cost",
  capex_capacity: "Capex & Rollouts",
  debt_reduction: "Debt Reduction",
  capital_allocation: "Capital Return",
  operational: "Operational & Tech",
};

const STATUS_CONFIG: Record<
  CommitmentStatus,
  { label: string; bg: string; text: string; border: string; icon: string }
> = {
  beat: {
    label: "Beat Target",
    bg: "rgba(16, 185, 129, 0.15)",
    text: "#10b981",
    border: "rgba(16, 185, 129, 0.35)",
    icon: "✓+",
  },
  met: {
    label: "Target Met",
    bg: "rgba(59, 130, 246, 0.15)",
    text: "#60a5fa",
    border: "rgba(59, 130, 246, 0.35)",
    icon: "✓",
  },
  missed: {
    label: "Target Missed",
    bg: "rgba(239, 68, 68, 0.15)",
    text: "#f87171",
    border: "rgba(239, 68, 68, 0.35)",
    icon: "✗",
  },
  in_progress: {
    label: "In Progress",
    bg: "rgba(245, 158, 11, 0.15)",
    text: "#fbbf24",
    border: "rgba(245, 158, 11, 0.35)",
    icon: "⏳",
  },
  delayed: {
    label: "Delayed",
    bg: "rgba(249, 115, 22, 0.15)",
    text: "#fb923c",
    border: "rgba(249, 115, 22, 0.35)",
    icon: "⚠",
  },
};

export default function PromisedDeliveredSection() {
  const [ticker, setTicker] = useState<string>("INFY");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [data, setData] = useState<CompanyCommitmentsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    getCommitments(ticker, {
      category: categoryFilter !== "all" ? categoryFilter : undefined,
      status: statusFilter !== "all" ? statusFilter : undefined,
    })
      .then((res) => {
        if (!cancelled) {
          setData(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message || "Failed to load management track record");
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [ticker, categoryFilter, statusFilter]);

  const trackRecord = data?.track_record;

  const scoreColor = useMemo(() => {
    if (!trackRecord) return "#94a3b8";
    if (trackRecord.delivery_score_pct >= 80) return "#10b981";
    if (trackRecord.delivery_score_pct >= 60) return "#f59e0b";
    return "#ef4444";
  }, [trackRecord]);

  return (
    <section id="promised-delivered" className="section-container commitments-section">
      <div className="section-header-compact">
        <div className="header-meta">
          <span className="badge badge-accent">Corporate Accountability</span>
          <span className="timestamp">Audit-Grade Transcripts</span>
        </div>
        <h2 className="section-title">Promised vs. Delivered</h2>
        <p className="section-subtitle">
          Track executive commitments from earnings calls & annual filings against audited quarterly delivery and actual business outcomes.
        </p>
      </div>

      {/* Company Selector */}
      <div className="ticker-selector-scroll">
        {COMPANIES.map((c) => (
          <button
            key={c.ticker}
            type="button"
            className={`pill-btn ${ticker === c.ticker ? "active" : ""}`}
            onClick={() => setTicker(c.ticker)}
          >
            <span className="font-bold">{c.ticker}</span>
            <span className="ticker-subname">{c.name.split(" ")[0]}</span>
          </button>
        ))}
      </div>

      {/* Credibility Scorecard Banner */}
      {trackRecord && (
        <div className="credibility-scorecard">
          <div className="scorecard-top">
            <div className="scorecard-main">
              <div className="score-ring-wrap">
                <div
                  className="score-circle"
                  style={{
                    borderColor: scoreColor,
                    boxShadow: `0 0 16px ${scoreColor}33`,
                  }}
                >
                  <span className="score-number" style={{ color: scoreColor }}>
                    {trackRecord.delivery_score_pct}%
                  </span>
                  <span className="score-label">Delivery Score</span>
                </div>
              </div>
              <div className="scorecard-text">
                <div className="scorecard-title-row">
                  <span className="scorecard-badge">Executive Track Record</span>
                  <span className="scorecard-co">{data?.company_name}</span>
                </div>
                <div className="score-rating-desc">
                  {trackRecord.delivery_score_pct >= 80
                    ? "High Credibility — Management consistently achieves or surpasses public guidance targets."
                    : trackRecord.delivery_score_pct >= 60
                    ? "Moderate Credibility — Reasonable delivery with occasional macroeconomic or execution variances."
                    : "Low Credibility — Significant divergence observed between guided targets and delivered metrics."}
                </div>
              </div>
            </div>

            {/* Quick Count Stat Badges */}
            <div className="score-stats-grid">
              <div className="score-stat-card beat">
                <span className="stat-count">{trackRecord.beat_count}</span>
                <span className="stat-name">Beat</span>
              </div>
              <div className="score-stat-card met">
                <span className="stat-count">{trackRecord.met_count}</span>
                <span className="stat-name">Met</span>
              </div>
              <div className="score-stat-card missed">
                <span className="stat-count">{trackRecord.missed_count}</span>
                <span className="stat-name">Missed</span>
              </div>
              <div className="score-stat-card progress">
                <span className="stat-count">{trackRecord.in_progress_count}</span>
                <span className="stat-name">Active</span>
              </div>
            </div>
          </div>

          {/* Category Performance Breakdown Bar */}
          {trackRecord.category_breakdown &&
            Object.keys(trackRecord.category_breakdown).length > 0 && (
              <div className="category-track-row">
                <span className="cat-track-title">Delivery by Guidance Domain:</span>
                <div className="cat-track-badges">
                  {Object.entries(trackRecord.category_breakdown).map(([cat, stats]) => (
                    <div key={cat} className="cat-stat-chip">
                      <span className="cat-chip-name">
                        {CATEGORY_LABELS[cat] || cat}
                      </span>
                      <span
                        className="cat-chip-score"
                        style={{
                          color:
                            stats.delivery_score_pct >= 75
                              ? "#10b981"
                              : stats.delivery_score_pct >= 50
                              ? "#f59e0b"
                              : "#ef4444",
                        }}
                      >
                        {stats.delivery_score_pct}% ({stats.beat + stats.met}/{stats.total})
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
        </div>
      )}

      {/* Filter Controls */}
      <div className="commitments-filter-bar">
        <div className="filter-group">
          <label className="filter-label" htmlFor="commit-category-select">Domain:</label>
          <select
            id="commit-category-select"
            className="filter-select"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <option value="all">All Domains ({data?.count ?? 0})</option>
            <option value="revenue_growth">Revenue Growth</option>
            <option value="margin">Margin Guidance</option>
            <option value="capex_capacity">Capex & Capacity</option>
            <option value="debt_reduction">Debt Reduction</option>
            <option value="capital_allocation">Capital Allocation</option>
            <option value="operational">Operational & Tech</option>
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label" htmlFor="commit-status-select">Outcome:</label>
          <select
            id="commit-status-select"
            className="filter-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All Outcomes</option>
            <option value="beat">Beat Guidance</option>
            <option value="met">Target Met</option>
            <option value="missed">Missed Guidance</option>
            <option value="in_progress">In Progress</option>
          </select>
        </div>
      </div>

      {/* Loading & Error States */}
      {loading && (
        <div className="card loading-card">
          <div className="spinner" />
          <p>Auditing management statements & delivery filings...</p>
        </div>
      )}

      {error && !loading && (
        <div className="card error-card">
          <p className="text-red font-semibold">{error}</p>
          <button
            type="button"
            className="pill-btn mt-2"
            onClick={() => setTicker(ticker)}
          >
            Retry Verification
          </button>
        </div>
      )}

      {/* Commitments Comparative Cards List */}
      {!loading && !error && data?.commitments && (
        <div className="commitments-list">
          {data.commitments.length === 0 ? (
            <div className="card empty-card">
              <p>No commitments found matching the selected filter criteria.</p>
            </div>
          ) : (
            data.commitments.map((c) => {
              const statusCfg = STATUS_CONFIG[c.status] || STATUS_CONFIG.in_progress;
              const isExpanded = expandedId === c.id;

              return (
                <article
                  key={c.id}
                  className={`commitment-card status-${c.status}`}
                  onClick={() => setExpandedId(isExpanded ? null : c.id)}
                >
                  {/* Card Header */}
                  <div className="commit-header">
                    <div className="commit-meta-top">
                      <span className="category-pill">
                        {CATEGORY_LABELS[c.category] || c.category}
                      </span>
                      <span className="period-pill">{c.promised_period}</span>
                      <span
                        className="status-pill"
                        style={{
                          backgroundColor: statusCfg.bg,
                          color: statusCfg.text,
                          borderColor: statusCfg.border,
                        }}
                      >
                        <span className="status-icon">{statusCfg.icon}</span>
                        {statusCfg.label}
                      </span>
                    </div>
                    <h3 className="commit-headline">{c.promise_headline}</h3>
                  </div>

                  {/* Comparative Side-by-Side Grid */}
                  <div className="comparison-grid">
                    {/* The Promise */}
                    <div className="comparison-pane promise-pane">
                      <div className="pane-header">
                        <span className="pane-tag promise-tag">Promised</span>
                        {c.target_metric && (
                          <span className="metric-badge promise-metric">
                            Target: {c.target_metric}
                          </span>
                        )}
                      </div>
                      <blockquote className="verbatim-quote">
                        &ldquo;{c.promised_quote}&rdquo;
                      </blockquote>
                      <div className="speaker-citation">
                        <div className="speaker-name">
                          {c.promised_by || "Executive Management"}
                        </div>
                        <div className="doc-citation">
                          {c.promised_document}
                          {c.promised_locator && ` • ${c.promised_locator}`}
                        </div>
                        <div className="target-date">
                          Target Date: {c.target_date || c.promised_period}
                        </div>
                      </div>
                    </div>

                    {/* The Delivery */}
                    <div className="comparison-pane delivery-pane">
                      <div className="pane-header">
                        <span className="pane-tag delivery-tag">Delivered</span>
                        {c.delivered_metric ? (
                          <span className="metric-badge delivered-metric">
                            Actual: {c.delivered_metric}
                          </span>
                        ) : (
                          <span className="metric-badge in-progress-metric">
                            Monitoring in Progress
                          </span>
                        )}
                      </div>
                      {c.delivered_quote ? (
                        <blockquote className="verbatim-quote delivered-quote">
                          &ldquo;{c.delivered_quote}&rdquo;
                        </blockquote>
                      ) : (
                        <p className="awaiting-quote">
                          Awaiting formal delivery filing audit for target date {c.target_date}.
                        </p>
                      )}
                      <div className="speaker-citation">
                        {c.delivered_document && (
                          <div className="doc-citation delivered-doc">
                            {c.delivered_document}
                            {c.delivered_locator && ` • ${c.delivered_locator}`}
                          </div>
                        )}
                        {c.delivered_at && (
                          <div className="delivery-date">
                            Reported: {c.delivered_at.slice(0, 10)}
                          </div>
                        )}
                        {c.variance_pct !== null && (
                          <div
                            className={`variance-pill ${
                              c.variance_pct >= 0 ? "positive" : "negative"
                            }`}
                          >
                            Variance: {c.variance_pct > 0 ? `+${c.variance_pct}%` : `${c.variance_pct}%`}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Assessment & Management Explanation */}
                  <div className="commitment-footer">
                    <div className="assessment-row">
                      <span className="assessment-tag">Assessment:</span>
                      <span className="assessment-text">{c.delivery_assessment}</span>
                    </div>

                    {c.management_explanation && (
                      <div className="explanation-row">
                        <span className="explanation-tag">Management Context:</span>
                        <span className="explanation-text">
                          {c.management_explanation}
                        </span>
                      </div>
                    )}

                    {/* Source filing link */}
                    {c.source_url && (
                      <div className="source-link-row">
                        <a
                          href={c.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="filing-link"
                          onClick={(e) => e.stopPropagation()}
                        >
                          Official Filing / Transcript Source →
                        </a>
                      </div>
                    )}
                  </div>
                </article>
              );
            })
          )}
        </div>
      )}
    </section>
  );
}
