"use client";

import React, { useState } from "react";
import ResearchSection from "./research-section";
import FundamentalsSection from "./fundamentals-section";
import PromisedDeliveredSection from "./promised-delivered-section";
import ResultsCardSection from "./results-card-section";
import ManagementChangesSection from "./management-changes-section";
import AnnouncementsSection from "./announcements-section";

type ResearchSubTab = "intelligence" | "fundamentals" | "promises" | "results" | "management" | "announcements" | "all";

const SUB_TABS = [
  { id: "intelligence" as ResearchSubTab, label: "Intelligence", icon: "🧠", desc: "Synthesis & Thesis" },
  { id: "fundamentals" as ResearchSubTab, label: "Fundamentals", icon: "📈", desc: "Financials & Ratios" },
  { id: "promises" as ResearchSubTab, label: "Promises", icon: "⚖", desc: "Guidance Track Record" },
  { id: "results" as ResearchSubTab, label: "Results Cards", icon: "⌕", desc: "Quarterly Audits" },
  { id: "management" as ResearchSubTab, label: "Leadership", icon: "↗", desc: "Executive Moves" },
  { id: "announcements" as ResearchSubTab, label: "Filings", icon: "📰", desc: "Exchange Disclosures" },
  { id: "all" as ResearchSubTab, label: "View All", icon: "▦", desc: "Full Dossier" },
];

export default function ResearchHub() {
  const [activeSubTab, setActiveSubTab] = useState<ResearchSubTab>("intelligence");

  return (
    <div className="research-hub-container" id="research-hub">
      {/* Sub-navigation bar */}
      <div className="research-subnav-bar">
        <div className="subnav-label-wrap">
          <span className="subnav-title">Company Research Hub</span>
          <span className="subnav-meta">Audit-Grade Intelligence Suite</span>
        </div>
        <div className="research-subtabs-scroll">
          {SUB_TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={`research-subtab-btn ${activeSubTab === tab.id ? "active" : ""}`}
              onClick={() => setActiveSubTab(tab.id)}
            >
              <span className="subtab-icon">{tab.icon}</span>
              <span className="subtab-label">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Render selected module(s) */}
      <div className="research-tab-content">
        {(activeSubTab === "intelligence" || activeSubTab === "all") && (
          <div className="subtab-panel" id="research">
            <ResearchSection />
          </div>
        )}

        {(activeSubTab === "fundamentals" || activeSubTab === "all") && (
          <div className="subtab-panel" id="fundamentals">
            <FundamentalsSection />
          </div>
        )}

        {(activeSubTab === "promises" || activeSubTab === "all") && (
          <div className="subtab-panel" id="promised-delivered">
            <PromisedDeliveredSection />
          </div>
        )}

        {(activeSubTab === "results" || activeSubTab === "all") && (
          <div className="subtab-panel" id="results-card">
            <ResultsCardSection />
          </div>
        )}

        {(activeSubTab === "management" || activeSubTab === "all") && (
          <div className="subtab-panel" id="management-changes">
            <ManagementChangesSection />
          </div>
        )}

        {(activeSubTab === "announcements" || activeSubTab === "all") && (
          <div className="subtab-panel" id="announcements">
            <AnnouncementsSection />
          </div>
        )}
      </div>
    </div>
  );
}
