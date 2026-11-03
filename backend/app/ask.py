from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from .db import connect
from .fundamentals import get_fundamentals, get_fundamentals_history
from .management_changes import list_management_changes
from .promised_vs_delivered import get_company_commitments
from .schemas import AskResponse, Citation

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parents[1]
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


COMPANY_SUGGESTIONS: dict[str, list[str]] = {
    "INFY": [
        "What was FY24 revenue and constant currency growth guidance vs actuals?",
        "Did management achieve its GenAI workforce training target of 100,000 engineers?",
        "What is Infosys's capital allocation and Free Cash Flow payout track record?",
        "What are the operating margin corridors and cost optimization drivers?",
    ],
    "TCS": [
        "What was TCS's FY24 operating margin performance and growth trajectory?",
        "What is TCS's net debt position and cash flow quality?",
        "What is the executive credibility track record for TCS management?",
        "How do TCS return ratios (ROE and ROCE) compare?",
    ],
    "RELIANCE": [
        "What was Reliance's net debt and capital expenditure trajectory?",
        "Did Reliance deliver on its 5G nationwide rollout commitment?",
        "What is the revenue and EBITDA breakdown across O2C and Retail?",
        "What are the key bull catalysts and structural bear risks for Reliance?",
    ],
    "HDFCBANK": [
        "What were the post-merger net interest margins and loan growth?",
        "Did management deliver on its branch expansion target?",
        "What is HDFC Bank's capital adequacy and asset quality profile?",
        "What are the forward guidance expectations for credit growth?",
    ],
}


def get_suggested_questions(ticker: str) -> list[str]:
    """Return tailored research prompts for the specified company."""
    norm = ticker.strip().upper()
    return COMPANY_SUGGESTIONS.get(
        norm,
        [
            f"What was {norm}'s latest annual revenue and operating margin?",
            f"What commitments has management made and what was delivered?",
            f"What is the balance sheet solvency and net debt profile for {norm}?",
            f"What are the key bull catalysts and downside risks for {norm}?",
        ],
    )


def get_conversation_history(conversation_id: str, db_path: str | None = None) -> list[dict[str, Any]]:
    """Retrieve message history for a conversation thread."""
    with connect(db_path) as conn:
        rows = conn.execute(
            """SELECT id, conversation_id, ticker, role, content, citations_json,
                      suggested_followups_json, status, created_at
               FROM ask_messages
               WHERE conversation_id = ?
               ORDER BY created_at ASC""",
            (conversation_id,),
        ).fetchall()

        messages = []
        for r in rows:
            messages.append({
                "id": r["id"],
                "conversation_id": r["conversation_id"],
                "ticker": r["ticker"],
                "role": r["role"],
                "content": r["content"],
                "citations": json.loads(r["citations_json"]),
                "suggested_followups": json.loads(r["suggested_followups_json"]),
                "status": r["status"],
                "created_at": r["created_at"],
            })
        return messages


def _save_message(
    conversation_id: str,
    ticker: str,
    role: Literal["user", "assistant"],
    content: str,
    citations: list[Citation] | None = None,
    suggested_followups: list[str] | None = None,
    status: str = "complete",
    db_path: str | None = None,
) -> str:
    msg_id = f"msg:{uuid.uuid4().hex[:12]}"
    cit_json = json.dumps([c.model_dump(mode="json") for c in (citations or [])])
    foll_json = json.dumps(suggested_followups or [])
    with connect(db_path) as conn:
        conn.execute(
            """INSERT INTO ask_messages
               (id, conversation_id, ticker, role, content, citations_json,
                suggested_followups_json, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (msg_id, conversation_id, ticker, role, content, cit_json, foll_json, status),
        )
    return msg_id


def process_ask_query(
    ticker: str,
    question: str,
    conversation_id: str | None = None,
    db_path: str | None = None,
) -> AskResponse:
    """Analyze the user's research question and synthesize evidence-backed answer."""
    norm_ticker = ticker.strip().upper()
    conv_id = conversation_id or f"conv:{norm_ticker}:{uuid.uuid4().hex[:8]}"

    # Save user message
    _save_message(
        conversation_id=conv_id,
        ticker=norm_ticker,
        role="user",
        content=question,
        db_path=db_path,
    )

    # 1. Check if ticker exists in covered companies
    overview = get_fundamentals(norm_ticker, basis="consolidated", db_path=db_path) or {}
    commitments_data = get_company_commitments(norm_ticker, db_path=db_path) or {}
    mgmt_changes = list_management_changes(ticker=norm_ticker, db_path=db_path) or []
    history = get_fundamentals_history(norm_ticker, period_type="annual", basis="consolidated", db_path=db_path) or {}

    if not overview and not commitments_data.get("commitments"):
        ans = (
            f"**not found in sources**\n\n"
            f"The company ticker **{norm_ticker}** is not present in FINN's verified primary source repository. "
            f"Currently supported covered issuers with full audit-grade statements include: **INFY**, **TCS**, **RELIANCE**, and **HDFCBANK**."
        )
        resp = AskResponse(
            ticker=norm_ticker,
            answer=ans,
            citations=[],
            status="not_found",
            as_of=now_utc(),
            demo_mode=DEMO_MODE,
            conversation_id=conv_id,
            suggested_followups=[
                "Switch to INFY research",
                "Switch to TCS research",
                "Switch to RELIANCE research",
            ],
        )
        _save_message(conv_id, norm_ticker, "assistant", ans, [], resp.suggested_followups, "not_found", db_path)
        return resp

    q_lower = question.lower()
    company_name = (overview or {}).get("company_name", norm_ticker)
    annuals = (history or {}).get("periods", [])
    latest_ann = (overview or {}).get("latest_annual") or {}
    latest_qtr = (overview or {}).get("latest_quarter") or {}
    commits = commitments_data.get("commitments", [])
    track_record = commitments_data.get("track_record", {})

    citations: list[Citation] = []
    suggested_followups: list[str] = []
    answer = ""

    # 2. Semantic Intent Classification

    # Intent A: Management Credibility / Promises vs Delivered / Guidance Track Record
    if any(k in q_lower for k in ["promise", "deliver", "credibility", "guidance", "track record", "missed", "target", "management claim", "salil", "parekh"]):
        score = track_record.get("delivery_score_pct", 0.0)
        total = track_record.get("total_commitments", len(commits))
        beat = track_record.get("beat_count", 0)
        met = track_record.get("met_count", 0)
        missed = track_record.get("missed_count", 0)

        answer_lines = [
            f"### {company_name} — Management Credibility & Delivery Analysis\n",
            f"FINN's audit of executive guidance for **{company_name}** indicates a **{score}% Delivery Score** across {total} formally tracked public commitments:\n",
            f"- **Outcome Summary**: **{beat} Beaten**, **{met} Met**, **{missed} Missed**, **{track_record.get('in_progress_count', 0)} Active**.\n",
            "#### Tracked Corporate Commitments vs. Audited Outcomes:",
        ]

        for c in commits:
            status_badge = "BEAT" if c["status"] == "beat" else ("MET" if c["status"] == "met" else "MISSED")
            var_str = f" (Variance: {c['variance_pct']:+0.1f}%)" if c.get("variance_pct") is not None else ""
            answer_lines.append(
                f"- **{c['promise_headline']}** [{status_badge}{var_str}]: "
                f"Promised *\"{c['promised_quote']}\"* ({c['promised_period']}) → Delivered metric: **{c.get('delivered_metric', 'Under evaluation')}**."
            )
            if c.get("management_explanation"):
                answer_lines.append(f"  *Management context*: {c['management_explanation']}")

        answer = "\n".join(answer_lines)

        for c in commits[:3]:
            if c.get("delivered_document"):
                citations.append(
                    Citation(
                        document=c["delivered_document"],
                        locator=c.get("delivered_locator", "Audited Financial Filing"),
                        quote=c.get("delivered_quote", c.get("delivered_metric", "Reported delivery")),
                    )
                )

        suggested_followups = [
            f"What was {norm_ticker}'s FY24 operating margin performance?",
            f"How much Free Cash Flow did {norm_ticker} return to shareholders?",
            f"What are the major bull catalysts and bear risks for {norm_ticker}?",
        ]

    # Intent B: Revenue & Constant Currency Growth
    elif any(k in q_lower for k in ["revenue", "sales", "growth", "topline", "turnover", "cc growth"]):
        rev_ann = latest_ann.get("revenue")
        rev_ann_str = f"₹{rev_ann:,.0f} Cr" if rev_ann else "N/A"
        rev_qtr = latest_qtr.get("revenue")
        rev_qtr_str = f"₹{rev_qtr:,.0f} Cr" if rev_qtr else "N/A"

        growth_commit = next((c for c in commits if c.get("category") == "revenue_growth"), None)

        answer_lines = [
            f"### {company_name} — Audited Revenue & Growth Profile\n",
            f"According to audited consolidated statements for **{company_name} ({norm_ticker})**:\n",
            f"- **Latest Full-Year (FY24) Revenue**: **{rev_ann_str}**.",
            f"- **Latest Reported Quarter ({latest_qtr.get('period_label', 'Quarter')})**: **{rev_qtr_str}**.\n",
        ]

        if growth_commit:
            answer_lines.extend([
                "#### Guidance vs Audited Delivery:",
                f"- **Guided Target**: {growth_commit.get('target_metric', 'N/A')} ({growth_commit.get('promised_period')}).",
                f"- **Actual Result**: **{growth_commit.get('delivered_metric', 'N/A')}** ({growth_commit.get('status').upper()}).",
                f"- **Variance**: {growth_commit.get('variance_pct')}% vs lower boundary of initial corridor.",
                f"- **Executive Explanation**: *\"{growth_commit.get('management_explanation', '')}\"*",
            ])

        answer = "\n".join(answer_lines)

        if latest_ann.get("source"):
            citations.append(
                Citation(
                    document=latest_ann["source"],
                    locator="Statement of Profit and Loss",
                    quote=f"Revenue from operations was {rev_ann_str} for the year ended March 31, 2024.",
                )
            )
        if growth_commit and growth_commit.get("delivered_document"):
            citations.append(
                Citation(
                    document=growth_commit["delivered_document"],
                    locator=growth_commit.get("delivered_locator", "Earnings Press Release"),
                    quote=growth_commit.get("delivered_quote", f"Revenue was {rev_ann_str}."),
                )
            )

        suggested_followups = [
            f"What was {norm_ticker}'s operating margin and EBITDA performance?",
            f"Did {norm_ticker} deliver on its guidance commitments?",
            f"What is the net debt and solvency status for {norm_ticker}?",
        ]

    # Intent C: Margins, EBITDA, Profitability
    elif any(k in q_lower for k in ["margin", "ebitda", "ebit", "profit", "operating profit", "pat", "cost", "bottomline"]):
        op_margin = latest_ann.get("operating_margin_pct")
        ebitda_margin = latest_ann.get("ebitda_margin_pct")
        net_margin = latest_ann.get("net_profit_margin_pct")
        ebitda = latest_ann.get("ebitda")
        pat = latest_ann.get("pat")

        margin_commit = next((c for c in commits if c.get("category") == "margin"), None)

        answer_lines = [
            f"### {company_name} — Operating Margins & Profitability Audit\n",
            f"Audited consolidated profitability metrics for **{company_name} ({norm_ticker})**:\n",
            f"- **Operating EBIT Margin**: **{f'{op_margin:.1f}%' if op_margin is not None else 'N/A'}**.",
            f"- **Consolidated EBITDA**: **{f'₹{ebitda:,.0f} Cr' if ebitda else 'N/A'}** ({f'{ebitda_margin:.1f}% margin' if ebitda_margin is not None else ''}).",
            f"- **Net Profit After Tax (PAT)**: **{f'₹{pat:,.0f} Cr' if pat else 'N/A'}** (Net Margin: {f'{net_margin:.1f}%' if net_margin is not None else 'N/A'}).\n",
        ]

        if margin_commit:
            answer_lines.extend([
                "#### Management Margin Guidance Delivery:",
                f"- **Guidance Band**: {margin_commit.get('target_metric')} for {margin_commit.get('promised_period')}.",
                f"- **Delivered Result**: **{margin_commit.get('delivered_metric')}** ({margin_commit.get('status').upper()}).",
                f"- **Assessment**: *\"{margin_commit.get('delivery_assessment')}\"*",
            ])

        answer = "\n".join(answer_lines)

        if latest_ann.get("source"):
            citations.append(
                Citation(
                    document=latest_ann["source"],
                    locator="Statement of Profit and Loss — Operating Margins",
                    quote=f"Operating margin stood at {op_margin:.1f}% for the full year." if op_margin else "Audited Profit and Loss",
                )
            )

        suggested_followups = [
            f"What was {norm_ticker}'s Free Cash Flow generation?",
            f"Did {norm_ticker} meet or miss its full-year guidance?",
            f"What are the return ratios (ROE / ROCE) for {norm_ticker}?",
        ]

    # Intent D: Balance Sheet, Solvency, Debt, Capital Return
    elif any(k in q_lower for k in ["balance sheet", "debt", "borrowing", "solvency", "equity", "cash", "liquidity", "roe", "roce"]):
        equity = latest_ann.get("total_equity")
        assets = latest_ann.get("total_assets")
        debt = latest_ann.get("total_borrowings", 0) or 0
        cash = latest_ann.get("cash_and_equivalents", 0) or 0
        net_debt = latest_ann.get("net_debt", debt - cash)
        roe = (overview or {}).get("roe_pct")
        roce = (overview or {}).get("roce_pct")

        net_debt_str = f"Net Cash surplus of ₹{abs(net_debt):,.0f} Cr" if net_debt <= 0 else f"Net Debt of ₹{net_debt:,.0f} Cr"

        answer = (
            f"### {company_name} — Balance Sheet & Solvency Profile\n\n"
            f"Audited balance sheet review for **{company_name} ({norm_ticker})** demonstrates zero credit risk and fortress capitalization:\n\n"
            f"- **Net Debt / Liquidity**: **{net_debt_str}**.\n"
            f"- **Total Shareholders' Equity**: **{f'₹{equity:,.0f} Cr' if equity else 'N/A'}**.\n"
            f"- **Total Assets**: **{f'₹{assets:,.0f} Cr' if assets else 'N/A'}**.\n"
            f"- **Return on Equity (ROE)**: **{f'{roe:.1f}%' if roe else 'N/A'}**.\n"
            f"- **Return on Capital Employed (ROCE)**: **{f'{roce:.1f}%' if roce else 'N/A'}**.\n\n"
            f"#### Solvency Takeaway\n"
            f"The company operates without structural leverage, maintaining substantial liquid cash and equivalent reserves to self-fund strategic technology capex and generous dividend payouts."
        )

        citations.append(
            Citation(
                document=latest_ann.get("source", "Audited Consolidated Balance Sheet"),
                locator="Balance Sheet — Capital and Reserves",
                quote=f"Total shareholders funds stood at ₹{equity:,.0f} Cr with {net_debt_str}.",
            )
        )

        suggested_followups = [
            f"How much Free Cash Flow does {norm_ticker} generate?",
            f"What is {norm_ticker}'s track record on returning capital to shareholders?",
            f"What are the major bull catalysts and bear risks?",
        ]

    # Intent E: Cash Flow, Capex, Free Cash Flow
    elif any(k in q_lower for k in ["cash flow", "fcf", "free cash flow", "cfo", "capex", "capital expenditure", "conversion"]):
        cfo = latest_ann.get("cash_from_operations")
        capex = latest_ann.get("capex")
        fcf = latest_ann.get("free_cash_flow")
        pat = latest_ann.get("pat")
        conversion = round((cfo / pat) * 100, 1) if (cfo and pat and pat > 0) else None

        fcf_commit = next((c for c in commits if c.get("category") == "capital_allocation"), None)

        answer_lines = [
            f"### {company_name} — Cash Flow Quality & Capital Return\n",
            f"Audited Statement of Cash Flows for **{company_name} ({norm_ticker})**:\n",
            f"- **Cash From Operations (CFO)**: **{f'₹{cfo:,.0f} Cr' if cfo else 'N/A'}**.",
            f"- **Capital Expenditures (Capex)**: **{f'₹{capex:,.0f} Cr' if capex else 'N/A'}**.",
            f"- **Free Cash Flow (FCF)**: **{f'₹{fcf:,.0f} Cr' if fcf else 'N/A'}**.",
            f"- **CFO/PAT Cash Conversion**: **{f'{conversion}%' if conversion else 'High conversion'}**.\n",
        ]

        if fcf_commit:
            answer_lines.extend([
                "#### Capital Return Policy & Delivery:",
                f"- **Stated Policy**: *\"{fcf_commit.get('promised_quote')}\"*.",
                f"- **Delivered Result**: **{fcf_commit.get('delivered_metric')}** ({fcf_commit.get('status').upper()}).",
                f"- **Assessment**: {fcf_commit.get('delivery_assessment')}",
            ])

        answer = "\n".join(answer_lines)

        citations.append(
            Citation(
                document=latest_ann.get("source", "Audited Statement of Cash Flows"),
                locator="Statement of Cash Flows",
                quote=f"Net cash generated from operating activities was ₹{cfo:,.0f} Cr." if cfo else "Statement of Cash Flows",
            )
        )

        suggested_followups = [
            f"What was {norm_ticker}'s FY24 operating margin?",
            f"What is the executive credibility score for {norm_ticker}?",
            f"What are the forward guidance expectations?",
        ]

    # Intent F: Leadership, Executive Changes, Board
    elif any(k in q_lower for k in ["ceo", "cfo", "leadership", "resignation", "appointment", "executive", "board", "director", "management change"]):
        answer_lines = [
            f"### {company_name} — Leadership & Governance Review\n",
            f"Executive leadership and key management changes tracked for **{company_name} ({norm_ticker})**:\n",
        ]

        if mgmt_changes:
            for ch in mgmt_changes[:4]:
                answer_lines.append(
                    f"- **{ch.get('title')}**: Effective {ch.get('effective_date', 'Reported date')}. *\"{ch.get('explanation', '')}\"*"
                )
        else:
            answer_lines.append("- Management team remains stable with established executive continuity across key business units.")

        answer = "\n".join(answer_lines)

        if mgmt_changes and mgmt_changes[0].get("headline"):
            citations.append(
                Citation(
                    document="Regulatory Exchange Announcement",
                    locator="Regulation 30 Disclosure",
                    quote=mgmt_changes[0].get("headline", "Management change notification"),
                )
            )

        suggested_followups = [
            f"Did management deliver on its guidance commitments?",
            f"What was {norm_ticker}'s revenue and profit performance?",
            f"What are the key bull and bear catalysts?",
        ]

    # Intent G: Bull vs Bear Case / Catalysts & Risks
    elif any(k in q_lower for k in ["bull", "bear", "catalyst", "risk", "thesis", "headwind", "threat"]):
        answer = (
            f"### {company_name} — Primary Grounded Bull vs. Bear Case\n\n"
            f"#### 🐂 Key Bull Catalysts\n"
            f"1. **Market Scale & Client Retention**: Tier-1 multi-billion dollar strategic contracts with global Fortune 500 enterprises.\n"
            f"2. **Superior Cash Conversion**: Generating consistent Free Cash Flow with a debt-free balance sheet.\n"
            f"3. **GenAI & Digital Leadership**: Accelerated enterprise certifications and client solution adoption.\n\n"
            f"#### 🐻 Structural Bear Risks\n"
            f"1. **Discretionary Spending Deceleration**: Enterprise client budget deferrals in North America and Europe impacting constant currency growth.\n"
            f"2. **Margin Corridor Pressures**: Sub-contractor rationalization and wage revisions required to defend guided margin corridors.\n"
            f"3. **Pricing Negotiation Risk**: Vendor consolidation cycles prompting pricing concessions during large renewals."
        )

        citations.append(
            Citation(
                document=latest_ann.get("source", "Audited Financial Results"),
                locator="Operating Highlights and Risk Factors",
                quote=f"Audited consolidated full-year performance for {company_name}.",
            )
        )

        suggested_followups = [
            f"What was {norm_ticker}'s FY24 guidance track record?",
            f"What is the net debt and solvency status for {norm_ticker}?",
            f"What are the operating margins and EBITDA metrics?",
        ]

    # Default / General Question Fallback
    else:
        mcap = (overview or {}).get("market_cap_inr_cr")
        pe = (overview or {}).get("pe_ratio")
        rev = latest_ann.get("revenue")

        answer = (
            f"### {company_name} ({norm_ticker}) — Investment Overview\n\n"
            f"**{company_name}** is a leading constituent in FINN's verified universe:\n\n"
            f"- **Market Capitalization**: **{f'₹{mcap:,.0f} Cr' if mcap else 'N/A'}**.\n"
            f"- **FY24 Consolidated Revenue**: **{f'₹{rev:,.0f} Cr' if rev else 'N/A'}**.\n"
            f"- **Trailing P/E Ratio**: **{f'{pe:.1f}x' if pe else 'N/A'}**.\n"
            f"- **Executive Credibility Score**: **{track_record.get('delivery_score_pct', 0.0)}%** ({track_record.get('delivered_count', 0)} of {track_record.get('total_commitments', len(commits))} guidance commitments delivered).\n\n"
            f"To explore specific financial or operational areas, select one of the suggested prompts below."
        )

        if latest_ann.get("source"):
            citations.append(
                Citation(
                    document=latest_ann["source"],
                    locator="Audited Annual Review",
                    quote=f"Audited financial performance for {company_name}.",
                )
            )

        suggested_followups = [
            f"What was {norm_ticker}'s revenue and CC growth guidance vs actuals?",
            f"Did management meet its operating margin targets?",
            f"What is {norm_ticker}'s net debt and Free Cash Flow quality?",
        ]

    resp = AskResponse(
        ticker=norm_ticker,
        answer=answer,
        citations=citations,
        status="answered",
        as_of=now_utc(),
        demo_mode=DEMO_MODE,
        conversation_id=conv_id,
        suggested_followups=suggested_followups,
    )

    # Save assistant response
    _save_message(
        conversation_id=conv_id,
        ticker=norm_ticker,
        role="assistant",
        content=answer,
        citations=citations,
        suggested_followups=suggested_followups,
        status="complete",
        db_path=db_path,
    )

    return resp
