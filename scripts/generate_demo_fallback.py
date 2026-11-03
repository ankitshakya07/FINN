"""Generate frontend/src/lib/demo-fallback.ts from the running FINN backend/fixtures

This ensures that when FINN is deployed to Vercel (where no local FastAPI daemon
is running), the Next.js frontend gracefully renders complete, authentic investment
intelligence instead of empty error cards.
"""

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_FILE = ROOT / "frontend" / "src" / "lib" / "demo-fallback.ts"

BASE_URL = "http://127.0.0.1:8013"

def get(path: str):
    try:
        with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=5) as r:
            return json.loads(r.read())
    except Exception as exc:
        print(f"Error fetching {path}: {exc}")
        return None

portfolio = get("/portfolio")
digest_24h = get("/digest?window=24h")
digest_7d = get("/digest?window=7d")
alerts = get("/alerts")
anomalies = get("/anomalies")
results_filings = get("/results-filings")
modules = get("/research/modules")
commitments_infy = get("/commitments/INFY")
commitments_summary_infy = get("/commitments/INFY/summary")
fundamentals_infy = get("/fundamentals/INFY")
fundamentals_history_infy = get("/fundamentals/INFY/history")
fundamentals_ratios_infy = get("/fundamentals/INFY/ratios")
ask_suggestions_infy = get("/ask/suggestions/INFY")

content = f"""// Standalone fallback fixtures for FINN frontend in production / Vercel
// Automatically loaded when the backend is unreachable so the UI always renders complete, high-fidelity intelligence.

import type {{
  AlertsResponse,
  AnomaliesResponse,
  AskResponse,
  CommitmentSummaryResponse,
  CompanyCommitmentsResponse,
  DigestResponse,
  FundamentalsHistoryResponse,
  FundamentalsOverview,
  FundamentalsRatiosResponse,
  PortfolioResponse,
  ResearchModuleInfo,
  ResultsFilingsResponse,
}} from "./types";

export const FALLBACK_PORTFOLIO: PortfolioResponse = {json.dumps(portfolio, indent=2)};

export const FALLBACK_DIGEST_24H: DigestResponse = {json.dumps(digest_24h, indent=2)};

export const FALLBACK_DIGEST_7D: DigestResponse = {json.dumps(digest_7d, indent=2)};

export const FALLBACK_ALERTS: AlertsResponse = {json.dumps(alerts, indent=2)};

export const FALLBACK_ANOMALIES: AnomaliesResponse = {json.dumps(anomalies, indent=2)};

export const FALLBACK_RESULTS_FILINGS: ResultsFilingsResponse = {json.dumps(results_filings, indent=2)};

export const FALLBACK_RESEARCH_MODULES: {{ modules: ResearchModuleInfo[]; count: number }} = {json.dumps(modules, indent=2)};

export const FALLBACK_COMMITMENTS_INFY: CompanyCommitmentsResponse = {json.dumps(commitments_infy, indent=2)};

export const FALLBACK_COMMITMENTS_SUMMARY_INFY: CommitmentSummaryResponse = {json.dumps(commitments_summary_infy, indent=2)};

export const FALLBACK_FUNDAMENTALS_INFY: FundamentalsOverview = {json.dumps(fundamentals_infy, indent=2)};

export const FALLBACK_FUNDAMENTALS_HISTORY_INFY: FundamentalsHistoryResponse = {json.dumps(fundamentals_history_infy, indent=2)};

export const FALLBACK_FUNDAMENTALS_RATIOS_INFY: FundamentalsRatiosResponse = {json.dumps(fundamentals_ratios_infy, indent=2)};

export const FALLBACK_ASK_SUGGESTIONS: {{ ticker: string; suggestions: string[]; count: number }} = {json.dumps(ask_suggestions_infy, indent=2)};

export function getFallbackForPath<T>(path: string): T | null {{
  const clean = path.split("?")[0];
  if (clean === "/portfolio") return FALLBACK_PORTFOLIO as unknown as T;
  if (clean === "/digest") {{
    if (path.includes("window=7d") || path.includes("window=3d")) {{
      return FALLBACK_DIGEST_7D as unknown as T;
    }}
    return FALLBACK_DIGEST_24H as unknown as T;
  }}
  if (clean === "/alerts") return FALLBACK_ALERTS as unknown as T;
  if (clean === "/anomalies") return FALLBACK_ANOMALIES as unknown as T;
  if (clean === "/results-filings") return FALLBACK_RESULTS_FILINGS as unknown as T;
  if (clean === "/research/modules") return FALLBACK_RESEARCH_MODULES as unknown as T;
  if (clean.startsWith("/commitments/") && clean.endsWith("/summary")) return FALLBACK_COMMITMENTS_SUMMARY_INFY as unknown as T;
  if (clean.startsWith("/commitments/")) return FALLBACK_COMMITMENTS_INFY as unknown as T;
  if (clean.startsWith("/fundamentals/") && clean.endsWith("/history")) return FALLBACK_FUNDAMENTALS_HISTORY_INFY as unknown as T;
  if (clean.startsWith("/fundamentals/") && clean.endsWith("/ratios")) return FALLBACK_FUNDAMENTALS_RATIOS_INFY as unknown as T;
  if (clean.startsWith("/fundamentals/")) return FALLBACK_FUNDAMENTALS_INFY as unknown as T;
  if (clean.startsWith("/ask/suggestions/")) return FALLBACK_ASK_SUGGESTIONS as unknown as T;
  return null;
}}
"""

OUT_FILE.write_text(content, encoding="utf-8")
print(f"Successfully generated {OUT_FILE} ({OUT_FILE.stat().st_size} bytes)")
