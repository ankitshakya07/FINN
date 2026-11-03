"use client";

import React from "react";

export type MainTab = "brief" | "ask" | "watch" | "research";

interface MobileBottomNavProps {
  activeTab: MainTab;
  onSelectTab: (tab: MainTab) => void;
  anomaliesCount?: number;
}

export default function MobileBottomNav({
  activeTab,
  onSelectTab,
  anomaliesCount = 0,
}: MobileBottomNavProps) {
  const tabs = [
    { id: "brief" as MainTab, label: "Brief", icon: "📰", badge: null },
    { id: "ask" as MainTab, label: "Ask AI", icon: "💬", badge: "AI" },
    { id: "watch" as MainTab, label: "Watch", icon: "👁️", badge: anomaliesCount > 0 ? String(anomaliesCount) : null },
    { id: "research" as MainTab, label: "Research", icon: "🔬", badge: null },
  ];

  return (
    <nav className="mobile-bottom-nav" aria-label="Mobile Navigation">
      <div className="mobile-nav-inner">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              className={`mobile-tab-btn ${isActive ? "active" : ""}`}
              onClick={() => onSelectTab(tab.id)}
              aria-label={tab.label}
              aria-current={isActive ? "page" : undefined}
            >
              <div className="tab-icon-wrap">
                <span className="tab-icon">{tab.icon}</span>
                {tab.badge && (
                  <span className={`tab-badge ${tab.id === "watch" ? "badge-alert" : "badge-accent"}`}>
                    {tab.badge}
                  </span>
                )}
              </div>
              <span className="tab-label">{tab.label}</span>
              {isActive && <span className="tab-active-indicator" />}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
