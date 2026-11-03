"use client";

import React, { useEffect, useRef, useState } from "react";
import { ask, getAskSuggestions } from "../src/lib/api";
import type { AskResponse, Citation } from "../src/lib/types";

const COMPANIES = [
  { ticker: "INFY", name: "Infosys Ltd" },
  { ticker: "TCS", name: "Tata Consultancy Services" },
  { ticker: "RELIANCE", name: "Reliance Industries" },
  { ticker: "HDFCBANK", name: "HDFC Bank" },
];

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  suggestedFollowups?: string[];
  timestamp: string;
};

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

export default function AskSection() {
  const [ticker, setTicker] = useState<string>("INFY");
  const [inputQuestion, setInputQuestion] = useState<string>("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load suggestions when ticker changes
  useEffect(() => {
    getAskSuggestions(ticker)
      .then((res) => {
        if (res.suggestions && res.suggestions.length > 0) {
          setSuggestions(res.suggestions);
        }
      })
      .catch(() => {
        setSuggestions([
          `What was ${ticker}'s latest revenue and operating margin?`,
          `Did ${ticker} management deliver on its guidance promises?`,
          `What is ${ticker}'s net debt and Free Cash Flow status?`,
        ]);
      });
  }, [ticker]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = (questionToSend?: string) => {
    const q = (questionToSend || inputQuestion).trim();
    if (!q || loading) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: q,
      timestamp: new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuestion("");
    setLoading(true);

    ask({
      ticker,
      question: q,
      conversation_id: conversationId || undefined,
    })
      .then((res: AskResponse) => {
        if (res.conversation_id) {
          setConversationId(res.conversation_id);
        }
        const assistantMsg: ChatMessage = {
          id: `asst-${Date.now()}`,
          role: "assistant",
          content: res.answer,
          citations: res.citations,
          suggestedFollowups: res.suggested_followups,
          timestamp: new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }),
        };
        setMessages((prev) => [...prev, assistantMsg]);
        setLoading(false);
      })
      .catch((err) => {
        const errorMsg: ChatMessage = {
          id: `err-${Date.now()}`,
          role: "assistant",
          content: `Unable to complete query: ${err.message || "Network request failed"}. Please retry.`,
          timestamp: new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }),
        };
        setMessages((prev) => [...prev, errorMsg]);
        setLoading(false);
      });
  };

  const handleClear = () => {
    setMessages([]);
    setConversationId(null);
    setActiveCitation(null);
  };

  return (
    <section id="ask" className="section-container ask-section">
      <div className="section-header-compact">
        <div className="header-meta">
          <span className="badge badge-accent">AI Research Assistant</span>
          <span className="timestamp">Primary Source Grounded</span>
        </div>
        <h2 className="section-title">Ask FINN AI</h2>
        <p className="section-subtitle">
          Ask research questions about guidance track record, EBITDA margins, cash conversion, and balance sheet solvency. Every claim is verified with primary source citations.
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

      {/* Suggested Prompts Bar */}
      <div className="ask-suggestions-wrap">
        <span className="suggestions-label">Suggested Research Inquiries:</span>
        <div className="suggestions-chips-scroll">
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              type="button"
              className="suggestion-chip"
              onClick={() => handleSend(s)}
              disabled={loading}
            >
              <span className="chip-arrow">↳</span>
              <span className="chip-text">{s}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Chat Thread Container */}
      <div className="ask-chat-window">
        {messages.length === 0 ? (
          <div className="ask-empty-state">
            <span className="ask-empty-icon">💬</span>
            <h4 className="ask-empty-title">Investigate {ticker} with Audit-Grade Evidence</h4>
            <p className="ask-empty-desc">
              Select one of the suggested prompts above or type a specific inquiry about financial statements, guidance delivery, or management statements.
            </p>
          </div>
        ) : (
          <div className="ask-messages-list">
            {messages.map((m) => {
              const isUser = m.role === "user";
              return (
                <div key={m.id} className={`chat-message-row ${isUser ? "user-row" : "asst-row"}`}>
                  {!isUser && (
                    <div className="asst-avatar">
                      <span>f</span>
                    </div>
                  )}

                  <div className={`chat-bubble ${isUser ? "user-bubble" : "asst-bubble"}`}>
                    <div className="bubble-header">
                      <span className="bubble-author">{isUser ? "You" : `FINN AI · ${ticker}`}</span>
                      <span className="bubble-time">{m.timestamp}</span>
                    </div>

                    <div className="bubble-content">
                      {m.content.split("\n").map((line, lIdx) => {
                        const trimmed = line.trim();
                        if (!trimmed) return <div key={lIdx} className="md-spacer" />;
                        if (trimmed.startsWith("### ")) {
                          return <h3 key={lIdx} className="md-h3">{trimmed.replace("### ", "")}</h3>;
                        }
                        if (trimmed.startsWith("#### ")) {
                          return <h4 key={lIdx} className="md-h4">{trimmed.replace("#### ", "")}</h4>;
                        }
                        if (trimmed.startsWith("- ")) {
                          const content = trimmed.replace(/^- /, "");
                          return (
                            <div key={lIdx} className="md-bullet-item">
                              <span className="bullet-dot">•</span>
                              <span>{renderBoldText(content)}</span>
                            </div>
                          );
                        }
                        const numMatch = trimmed.match(/^(\d+)\.\s+(.+)$/);
                        if (numMatch) {
                          return (
                            <div key={lIdx} className="md-numbered-item">
                              <span className="num-pill">{numMatch[1]}.</span>
                              <span>{renderBoldText(numMatch[2])}</span>
                            </div>
                          );
                        }
                        return <p key={lIdx} className="md-p">{renderBoldText(trimmed)}</p>;
                      })}
                    </div>

                    {/* Citations Attached to Assistant Message */}
                    {m.citations && m.citations.length > 0 && (
                      <div className="bubble-citations">
                        <span className="citations-label">Primary Sources:</span>
                        <div className="citations-chips">
                          {m.citations.map((c, cIdx) => (
                            <button
                              key={cIdx}
                              type="button"
                              className={`citation-pill ${activeCitation === c ? "active" : ""}`}
                              onClick={() => setActiveCitation(activeCitation === c ? null : c)}
                            >
                              <span className="cit-doc">{c.document}</span>
                              <span className="cit-loc">({c.locator})</span>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Follow-up question pills */}
                    {m.suggestedFollowups && m.suggestedFollowups.length > 0 && (
                      <div className="bubble-followups">
                        <span className="followups-label">Explore Further:</span>
                        <div className="followups-chips">
                          {m.suggestedFollowups.map((f, fIdx) => (
                            <button
                              key={fIdx}
                              type="button"
                              className="followup-btn"
                              onClick={() => handleSend(f)}
                              disabled={loading}
                            >
                              + {f}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {loading && (
              <div className="chat-message-row asst-row">
                <div className="asst-avatar">
                  <span>f</span>
                </div>
                <div className="chat-bubble asst-bubble loading-bubble">
                  <div className="pulse-loader">
                    <span className="dot" />
                    <span className="dot" />
                    <span className="dot" />
                  </div>
                  <span className="loading-text">
                    Auditing primary filings and synthesizing evidence for {ticker}...
                  </span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Citation Inspector Modal / Callout */}
      {activeCitation && (
        <div className="citation-inspector-card">
          <div className="inspector-header">
            <span className="inspector-tag">Verified Document Excerpt</span>
            <button
              type="button"
              className="inspector-close"
              onClick={() => setActiveCitation(null)}
            >
              ✕
            </button>
          </div>
          <div className="inspector-doc">{activeCitation.document}</div>
          <div className="inspector-loc">Locator: {activeCitation.locator}</div>
          <blockquote className="inspector-quote">
            &ldquo;{activeCitation.quote}&rdquo;
          </blockquote>
        </div>
      )}

      {/* Input Bar */}
      <form
        className="ask-input-bar"
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
      >
        <input
          id="ask-input-field"
          type="text"
          className="ask-text-input"
          placeholder={`Ask about ${ticker} guidance, margins, cash conversion, or management promises...`}
          value={inputQuestion}
          onChange={(e) => setInputQuestion(e.target.value)}
          disabled={loading}
        />
        <div className="ask-actions-group">
          <button
            type="submit"
            className="ask-submit-btn"
            disabled={!inputQuestion.trim() || loading}
          >
            Ask AI →
          </button>
          {messages.length > 0 && (
            <button
              type="button"
              className="ask-clear-btn"
              onClick={handleClear}
              title="Clear conversation"
            >
              Clear
            </button>
          )}
        </div>
      </form>
    </section>
  );
}
