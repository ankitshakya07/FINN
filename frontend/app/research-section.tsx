"use client";

import React, { useEffect, useState } from "react";
import { getResearchModules, runResearch, getResearchResult } from "../src/lib/api";
import type {
  Citation,
  ResearchModule,
  ResearchModuleInfo,
  ResearchProgress,
  ResearchResult,
} from "../src/lib/types";

const COMPANIES = [
  { ticker: "INFY", name: "Infosys Ltd" },
  { ticker: "TCS", name: "Tata Consultancy Services" },
  { ticker: "RELIANCE", name: "Reliance Industries" },
  { ticker: "HDFCBANK", name: "HDFC Bank" },
];

const FALLBACK_MODULES: ResearchModuleInfo[] = [
  {
    id: "bull_vs_bear",
    title: "Bull vs. Bear Thesis",
    description: "Balanced, citation-verified bull catalysts vs structural headwinds and operational risks.",
    icon: "🐂🐻",
    category: "Investment Thesis",
  },
  {
    id: "business_snapshot",
    title: "Business Snapshot",
    description: "Core operating segments, geographical exposure, competitive moats, and business model.",
    icon: "🏢",
    category: "Strategic",
  },
  {
    id: "financial_snapshot",
    title: "Financial Snapshot",
    description: "Reported scale, margin corridors, EBITDA generation, return ratios, and revenue composition.",
    icon: "📊",
    category: "Financial",
  },
  {
    id: "narrative_vs_numbers",
    title: "Narrative vs. Numbers",
    description: "Audited reconciliation comparing management concall statements against actual balance sheet results.",
    icon: "⚖",
    category: "Governance",
  },
  {
    id: "trajectory",
    title: "Growth Trajectory",
    description: "Multi-year CAGR, organic growth trends, operational momentum, and cyclical inflection points.",
    icon: "📈",
    category: "Strategic",
  },
  {
    id: "balance_sheet",
    title: "Balance Sheet & Solvency",
    description: "Capital structure, net debt position, working capital cycle, and asset health.",
    icon: "🏛",
    category: "Risk & Solvency",
  },
  {
    id: "cash_quality",
    title: "Cash Flow Quality",
    description: "Operating cash flow conversion ratio, free cash flow conversion, and capex discipline.",
    icon: "💧",
    category: "Financial",
  },
  {
    id: "guidance",
    title: "Guidance & Outlook",
    description: "Executive guidance bands, target visibility, demand commentary, and pipeline milestones.",
    icon: "🎯",
    category: "Forward-Looking",
  },
];

function renderBoldText(text: string): React.ReactNode {
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} className="md-strong">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
}

export default function ResearchSection() {
  const [ticker, setTicker] = useState<string>("INFY");
  const [selectedModule, setSelectedModule] = useState<ResearchModule>("bull_vs_bear");
  const [modules, setModules] = useState<ResearchModuleInfo[]>(FALLBACK_MODULES);
  const [result, setResult] = useState<ResearchResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [progress, setProgress] = useState<ResearchProgress | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  // Fetch modules list on mount
  useEffect(() => {
    getResearchModules()
      .then((res) => {
        if (res.modules && res.modules.length > 0) {
          setModules(res.modules);
        }
      })
      .catch(() => {
        // Fallback modules used
      });
  }, []);

  // Run research when ticker or selected module changes
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setProgress({ stage: "source_discovery", message: `Discovering primary filings for ${ticker}...` });
    setActiveCitation(null);

    runResearch(
      { ticker, module: selectedModule },
      (p: ResearchProgress) => {
        if (!cancelled) setProgress(p);
      }
    )
      .then((res: ResearchResult) => {
        if (!cancelled) {
          setResult(res);
          setLoading(false);
          setProgress(null);
        }
      })
      .catch((err: any) => {
        // If SSE failed, attempt REST fallback
        if (!cancelled) {
          getResearchResult(ticker, selectedModule)
            .then((fallbackRes: ResearchResult) => {
              if (!cancelled) {
                setResult(fallbackRes);
                setLoading(false);
                setProgress(null);
              }
            })
            .catch((fErr: any) => {
              if (!cancelled) {
                setError(fErr?.message || err?.message || "Failed to synthesize research");
                setLoading(false);
                setProgress(null);
              }
            });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [ticker, selectedModule]);

  const activeModuleMeta = modules.find((m) => m.id === selectedModule) || FALLBACK_MODULES[0];

  const handleCopy = () => {
    if (!result) return;
    const text = `${result.answer}\n\nCitations:\n` +
      result.citations.map((c) => `- ${c.document} (${c.locator}): "${c.quote}"`).join("\n");
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section id="research" className="section-container research-section">
      <div className="section-header-compact">
        <div className="header-meta">
          <span className="badge badge-accent">Evidence Synthesis</span>
          <span className="timestamp">Primary Source Grounded</span>
        </div>
        <h2 className="section-title">Research Intelligence Modules</h2>
        <p className="section-subtitle">
          Evidence-grounded, multi-angle investment intelligence synthesized strictly from audited primary statements, concalls, and exchange filings.
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

      {/* 8-Module Tabs Navigation */}
      <div className="research-modules-nav">
        {modules.map((m) => {
          const isSelected = selectedModule === m.id;
          return (
            <button
              key={m.id}
              type="button"
              className={`research-module-btn ${isSelected ? "selected" : ""}`}
              onClick={() => setSelectedModule(m.id)}
            >
              <span className="module-icon">{m.icon}</span>
              <div className="module-label-wrap">
                <span className="module-title">{m.title}</span>
                <span className="module-cat">{m.category}</span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Active Module Banner */}
      <div className="active-module-header">
        <div className="module-info-left">
          <span className="module-banner-icon">{activeModuleMeta.icon}</span>
          <div>
            <div className="module-banner-badge">{activeModuleMeta.category} Module</div>
            <h3 className="module-banner-title">{activeModuleMeta.title}</h3>
            <p className="module-banner-desc">{activeModuleMeta.description}</p>
          </div>
        </div>
        <div className="module-info-right">
          <button
            type="button"
            className="action-btn copy-btn"
            onClick={handleCopy}
            disabled={!result || loading}
          >
            {copied ? "✓ Copied" : "📋 Copy Analysis"}
          </button>
        </div>
      </div>

      {/* Streaming Progress Indicator */}
      {loading && progress && (
        <div className="research-progress-card">
          <div className="progress-spinner" />
          <div className="progress-details">
            <span className="progress-stage">
              {progress.stage === "source_discovery"
                ? "1. Discovery"
                : progress.stage === "data_retrieval"
                ? "2. Data Retrieval"
                : "3. Synthesis"}
            </span>
            <span className="progress-msg">{progress.message}</span>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="card error-card">
          <p className="text-red font-semibold">{error}</p>
          <button
            type="button"
            className="pill-btn mt-2"
            onClick={() => setTicker(ticker)}
          >
            Retry Research Synthesis
          </button>
        </div>
      )}

      {/* Research Result Content */}
      {!loading && result && (
        <div className="research-content-wrap">
          {/* Executive Answer Card */}
          <article className="research-answer-card">
            <div className="answer-header">
              <span className="answer-tag">Synthesized Intelligence</span>
              <span className="answer-asof">
                As of {result.as_of ? new Date(result.as_of).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" }) : "Today"}
              </span>
            </div>
            <div className="answer-markdown">
              {result.answer.split("\n").map((line, idx) => {
                const trimmed = line.trim();
                if (!trimmed) return <div key={idx} className="md-spacer" />;
                if (trimmed.startsWith("### ")) {
                  return <h3 key={idx} className="md-h3">{trimmed.replace("### ", "")}</h3>;
                }
                if (trimmed.startsWith("#### ")) {
                  return <h4 key={idx} className="md-h4">{trimmed.replace("#### ", "")}</h4>;
                }
                if (trimmed.startsWith("- ")) {
                  const content = trimmed.replace(/^- /, "");
                  return (
                    <div key={idx} className="md-bullet-item">
                      <span className="bullet-dot">•</span>
                      <span>{renderBoldText(content)}</span>
                    </div>
                  );
                }
                const numMatch = trimmed.match(/^(\d+)\.\s+(.+)$/);
                if (numMatch) {
                  return (
                    <div key={idx} className="md-numbered-item">
                      <span className="num-pill">{numMatch[1]}.</span>
                      <span>{renderBoldText(numMatch[2])}</span>
                    </div>
                  );
                }
                return <p key={idx} className="md-p">{renderBoldText(trimmed)}</p>;
              })}
            </div>
          </article>

          {/* Structured Findings Grid */}
          {result.findings && result.findings.length > 0 && (
            <div className="findings-section">
              <h4 className="findings-section-title">Key Evidence Findings</h4>
              <div className="findings-grid">
                {result.findings.map((f, fIdx) => {
                  const sentiment = (f.sentiment as string) || "neutral";
                  return (
                    <div key={fIdx} className={`finding-card sentiment-${sentiment}`}>
                      <div className="finding-header">
                        <span className="finding-cat">{(f.category as string) || "Finding"}</span>
                        {f.metric ? <span className="finding-metric">{String(f.metric)}</span> : null}
                      </div>
                      <h5 className="finding-title">{String(f.title)}</h5>
                      <p className="finding-desc">{String(f.description)}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Citations & Evidence Section */}
          {result.citations && result.citations.length > 0 && (
            <div className="citations-section">
              <h4 className="citations-title">
                Audited Document Citations ({result.citations.length})
              </h4>
              <div className="citations-list">
                {result.citations.map((c, cIdx) => (
                  <div
                    key={cIdx}
                    className={`citation-card ${activeCitation === c ? "active" : ""}`}
                    onClick={() => setActiveCitation(activeCitation === c ? null : c)}
                  >
                    <div className="citation-header">
                      <span className="citation-doc">{c.document}</span>
                      <span className="citation-locator">{c.locator}</span>
                    </div>
                    <blockquote className="citation-quote">
                      &ldquo;{c.quote}&rdquo;
                    </blockquote>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
