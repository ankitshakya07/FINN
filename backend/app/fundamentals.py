from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .db import connect

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parents[1]
FIXTURE_PATH = ROOT_DIR / "data" / "fixtures" / "fundamentals.json"
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        val = float(value)
        return round(val, 2) if math.isfinite(val) else None
    except (ValueError, TypeError):
        return None


def calculate_derived_metrics(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, bool]]:
    """Calculate derived financial metrics deterministically and track provenance."""
    record = dict(data)
    is_calc: dict[str, bool] = {}

    revenue = _safe_float(record.get("revenue"))
    expenses = _safe_float(record.get("total_expenses"))
    other_income = _safe_float(record.get("other_income"))
    operating_profit = _safe_float(record.get("operating_profit"))
    ebitda = _safe_float(record.get("ebitda"))
    depreciation = _safe_float(record.get("depreciation"))
    finance_costs = _safe_float(record.get("finance_costs"))
    pbt = _safe_float(record.get("pbt"))
    tax = _safe_float(record.get("tax"))
    pat = _safe_float(record.get("pat"))

    total_assets = _safe_float(record.get("total_assets"))
    total_equity = _safe_float(record.get("total_equity"))
    total_borrowings = _safe_float(record.get("total_borrowings"))
    cash = _safe_float(record.get("cash_and_equivalents"))
    net_debt = _safe_float(record.get("net_debt"))

    cfo = _safe_float(record.get("cash_from_operations"))
    capex = _safe_float(record.get("capex"))
    fcf = _safe_float(record.get("free_cash_flow"))

    # 1. Operating Profit
    if operating_profit is None and revenue is not None and expenses is not None:
        operating_profit = round(revenue - expenses, 2)
        is_calc["operating_profit"] = True
    else:
        is_calc["operating_profit"] = False
    record["operating_profit"] = operating_profit

    # 2. EBITDA
    if ebitda is None:
        if operating_profit is not None and other_income is not None:
            ebitda = round(operating_profit + other_income, 2)
            is_calc["ebitda"] = True
        elif pbt is not None and depreciation is not None:
            ebitda = round(pbt + depreciation + (finance_costs or 0.0), 2)
            is_calc["ebitda"] = True
        else:
            is_calc["ebitda"] = False
    else:
        is_calc["ebitda"] = False
    record["ebitda"] = ebitda

    # 3. Net Debt
    if net_debt is None and total_borrowings is not None and cash is not None:
        net_debt = round(total_borrowings - cash, 2)
        is_calc["net_debt"] = True
    else:
        is_calc["net_debt"] = False
    record["net_debt"] = net_debt

    # 4. Free Cash Flow
    if fcf is None and cfo is not None and capex is not None:
        fcf = round(cfo - capex, 2)
        is_calc["free_cash_flow"] = True
    else:
        is_calc["free_cash_flow"] = False
    record["free_cash_flow"] = fcf

    # 5. Margins
    if record.get("operating_margin_pct") is None:
        if revenue and revenue > 0 and operating_profit is not None:
            record["operating_margin_pct"] = round((operating_profit / revenue) * 100.0, 2)
            is_calc["operating_margin_pct"] = True
        else:
            record["operating_margin_pct"] = None
            is_calc["operating_margin_pct"] = False
    else:
        is_calc["operating_margin_pct"] = False

    if record.get("ebitda_margin_pct") is None:
        if revenue and revenue > 0 and ebitda is not None:
            record["ebitda_margin_pct"] = round((ebitda / revenue) * 100.0, 2)
            is_calc["ebitda_margin_pct"] = True
        else:
            record["ebitda_margin_pct"] = None
            is_calc["ebitda_margin_pct"] = False
    else:
        is_calc["ebitda_margin_pct"] = False

    if record.get("net_profit_margin_pct") is None:
        if revenue and revenue > 0 and pat is not None:
            record["net_profit_margin_pct"] = round((pat / revenue) * 100.0, 2)
            is_calc["net_profit_margin_pct"] = True
        else:
            record["net_profit_margin_pct"] = None
            is_calc["net_profit_margin_pct"] = False
    else:
        is_calc["net_profit_margin_pct"] = False

    # 6. Returns (ROE & ROCE)
    if record.get("roe_pct") is None:
        if pat is not None and total_equity and total_equity > 0:
            record["roe_pct"] = round((pat / total_equity) * 100.0, 2)
            is_calc["roe_pct"] = True
        else:
            record["roe_pct"] = None
            is_calc["roe_pct"] = False
    else:
        is_calc["roe_pct"] = False

    if record.get("roce_pct") is None:
        capital_employed = (total_equity or 0.0) + (total_borrowings or 0.0)
        ebit = (operating_profit or 0.0) + (other_income or 0.0)
        if capital_employed > 0 and ebit != 0:
            record["roce_pct"] = round((ebit / capital_employed) * 100.0, 2)
            is_calc["roce_pct"] = True
        else:
            record["roce_pct"] = None
            is_calc["roce_pct"] = False
    else:
        is_calc["roce_pct"] = False

    return record, is_calc


def save_fundamentals_records(records: list[dict[str, Any]], db_path: str | None = None) -> int:
    """Insert or update fundamentals records with duplicate prevention."""
    inserted = 0
    with connect(db_path) as conn:
        for raw in records:
            ticker = raw["ticker"].upper()
            basis = raw.get("basis", "consolidated").lower()
            period_type = raw.get("period_type", "annual").lower()
            period_end = raw["period_end"]
            rec_id = raw.get("id") or f"{ticker}:{basis}:{period_type}:{period_end}"

            calc_record, is_calc = calculate_derived_metrics(raw)
            is_calc_json = json.dumps(is_calc)
            raw_meta_json = json.dumps(raw.get("raw_metadata", {}))

            # Ensure company exists in companies table to satisfy foreign key
            conn.execute(
                "INSERT OR IGNORE INTO companies (ticker, name, sector, industry) VALUES (?, ?, ?, ?)",
                (ticker, raw.get("company_name", ticker), raw.get("sector"), raw.get("industry")),
            )

            conn.execute(
                """INSERT INTO company_fundamentals (
                    id, ticker, basis, period_type, period_end, period_label,
                    fiscal_year, fiscal_quarter, revenue, other_income, total_expenses,
                    operating_profit, ebitda, depreciation, finance_costs, pbt, tax, pat, eps,
                    total_assets, total_equity, total_borrowings, cash_and_equivalents, net_debt,
                    cash_from_operations, capex, free_cash_flow,
                    operating_margin_pct, ebitda_margin_pct, net_profit_margin_pct, roe_pct, roce_pct,
                    currency, unit, source, source_url, is_calculated_json, raw_metadata_json, updated_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
                ) ON CONFLICT(ticker, basis, period_type, period_end) DO UPDATE SET
                    period_label=excluded.period_label,
                    fiscal_year=excluded.fiscal_year,
                    fiscal_quarter=excluded.fiscal_quarter,
                    revenue=excluded.revenue,
                    other_income=excluded.other_income,
                    total_expenses=excluded.total_expenses,
                    operating_profit=excluded.operating_profit,
                    ebitda=excluded.ebitda,
                    depreciation=excluded.depreciation,
                    finance_costs=excluded.finance_costs,
                    pbt=excluded.pbt,
                    tax=excluded.tax,
                    pat=excluded.pat,
                    eps=excluded.eps,
                    total_assets=excluded.total_assets,
                    total_equity=excluded.total_equity,
                    total_borrowings=excluded.total_borrowings,
                    cash_and_equivalents=excluded.cash_and_equivalents,
                    net_debt=excluded.net_debt,
                    cash_from_operations=excluded.cash_from_operations,
                    capex=excluded.capex,
                    free_cash_flow=excluded.free_cash_flow,
                    operating_margin_pct=excluded.operating_margin_pct,
                    ebitda_margin_pct=excluded.ebitda_margin_pct,
                    net_profit_margin_pct=excluded.net_profit_margin_pct,
                    roe_pct=excluded.roe_pct,
                    roce_pct=excluded.roce_pct,
                    source=excluded.source,
                    source_url=excluded.source_url,
                    is_calculated_json=excluded.is_calculated_json,
                    raw_metadata_json=excluded.raw_metadata_json,
                    updated_at=CURRENT_TIMESTAMP""",
                (
                    rec_id, ticker, basis, period_type, period_end, calc_record.get("period_label", period_end),
                    calc_record.get("fiscal_year", 2026), calc_record.get("fiscal_quarter"),
                    calc_record.get("revenue"), calc_record.get("other_income"), calc_record.get("total_expenses"),
                    calc_record.get("operating_profit"), calc_record.get("ebitda"), calc_record.get("depreciation"),
                    calc_record.get("finance_costs"), calc_record.get("pbt"), calc_record.get("tax"),
                    calc_record.get("pat"), calc_record.get("eps"),
                    calc_record.get("total_assets"), calc_record.get("total_equity"), calc_record.get("total_borrowings"),
                    calc_record.get("cash_and_equivalents"), calc_record.get("net_debt"),
                    calc_record.get("cash_from_operations"), calc_record.get("capex"), calc_record.get("free_cash_flow"),
                    calc_record.get("operating_margin_pct"), calc_record.get("ebitda_margin_pct"),
                    calc_record.get("net_profit_margin_pct"), calc_record.get("roe_pct"), calc_record.get("roce_pct"),
                    calc_record.get("currency", "INR"), calc_record.get("unit", "INR Crore"),
                    calc_record.get("source", "screener"), calc_record.get("source_url"),
                    is_calc_json, raw_meta_json,
                ),
            )
            inserted += 1
        conn.commit()
    return inserted


def load_fundamentals_fixture(db_path: str | None = None) -> int:
    """Load the frozen demo fixture into SQLite."""
    if not FIXTURE_PATH.exists():
        return 0
    try:
        data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        records = data.get("records", [])
        return save_fundamentals_records(records, db_path=db_path)
    except (OSError, json.JSONDecodeError):
        return 0


def _row_to_period(row: Any) -> dict[str, Any]:
    item = dict(row)
    try:
        item["is_calculated"] = json.loads(item.pop("is_calculated_json", "{}"))
    except (TypeError, json.JSONDecodeError):
        item["is_calculated"] = {}
    item.pop("raw_metadata_json", None)
    return item


def get_fundamentals(ticker: str, basis: str = "consolidated", db_path: str | None = None) -> dict[str, Any] | None:
    """Return overview and latest period fundamentals for a ticker."""
    ticker_clean = ticker.strip().upper()
    basis_clean = basis.strip().lower()
    if basis_clean not in ("consolidated", "standalone"):
        basis_clean = "consolidated"

    with connect(db_path) as conn:
        company = conn.execute(
            "SELECT ticker, name, sector, industry, metadata_json FROM companies WHERE ticker = ?",
            (ticker_clean,),
        ).fetchone()

        if not company:
            # Fall back to checking if records exist in company_fundamentals
            fund_exists = conn.execute(
                "SELECT ticker FROM company_fundamentals WHERE ticker = ? LIMIT 1",
                (ticker_clean,),
            ).fetchone()
            if not fund_exists:
                # Try loading fixtures if not already present
                load_fundamentals_fixture(db_path)
                company = conn.execute(
                    "SELECT ticker, name, sector, industry, metadata_json FROM companies WHERE ticker = ?",
                    (ticker_clean,),
                ).fetchone()
                if not company:
                    fund_exists = conn.execute(
                        "SELECT ticker FROM company_fundamentals WHERE ticker = ? LIMIT 1",
                        (ticker_clean,),
                    ).fetchone()
                    if not fund_exists:
                        return None

        # Fetch latest quarterly record
        latest_q = conn.execute(
            """SELECT * FROM company_fundamentals
            WHERE ticker = ? AND basis = ? AND period_type = 'quarterly'
            ORDER BY period_end DESC LIMIT 1""",
            (ticker_clean, basis_clean),
        ).fetchone()

        # If chosen basis has no quarter, fall back to any basis
        if not latest_q:
            latest_q = conn.execute(
                """SELECT * FROM company_fundamentals
                WHERE ticker = ? AND period_type = 'quarterly'
                ORDER BY period_end DESC LIMIT 1""",
                (ticker_clean,),
            ).fetchone()

        # Fetch latest annual record
        latest_a = conn.execute(
            """SELECT * FROM company_fundamentals
            WHERE ticker = ? AND basis = ? AND period_type = 'annual'
            ORDER BY period_end DESC LIMIT 1""",
            (ticker_clean, basis_clean),
        ).fetchone()

        if not latest_a:
            latest_a = conn.execute(
                """SELECT * FROM company_fundamentals
                WHERE ticker = ? AND period_type = 'annual'
                ORDER BY period_end DESC LIMIT 1""",
                (ticker_clean,),
            ).fetchone()

        # Fetch latest price
        price_row = conn.execute(
            "SELECT close, trading_date FROM prices WHERE ticker = ? ORDER BY trading_date DESC LIMIT 1",
            (ticker_clean,),
        ).fetchone()

    company_name = company["name"] if company else ticker_clean
    sector = company["sector"] if company else None
    industry = company["industry"] if company else None
    current_price = float(price_row["close"]) if price_row else None

    # Derive PE and PB from latest annual data if available
    latest_a_dict = _row_to_period(latest_a) if latest_a else None
    latest_q_dict = _row_to_period(latest_q) if latest_q else None

    pe_ratio = None
    pb_ratio = None
    market_cap_inr_cr = None
    roe_pct = latest_a_dict.get("roe_pct") if latest_a_dict else (latest_q_dict.get("roe_pct") if latest_q_dict else None)
    roce_pct = latest_a_dict.get("roce_pct") if latest_a_dict else (latest_q_dict.get("roce_pct") if latest_q_dict else None)

    if latest_a_dict:
        eps = latest_a_dict.get("eps")
        if current_price and eps and eps > 0:
            pe_ratio = round(current_price / eps, 2)
        total_equity = latest_a_dict.get("total_equity")
        # Estimate market cap if PE and PAT available: market_cap = PE * PAT or equity * PB
        if pe_ratio and latest_a_dict.get("pat"):
            market_cap_inr_cr = round(pe_ratio * latest_a_dict["pat"], 2)
            if total_equity and total_equity > 0:
                pb_ratio = round(market_cap_inr_cr / total_equity, 2)

    return {
        "ticker": ticker_clean,
        "company_name": company_name,
        "sector": sector,
        "industry": industry,
        "basis": basis_clean,
        "market_cap_inr_cr": market_cap_inr_cr,
        "current_price": current_price,
        "pe_ratio": pe_ratio,
        "pb_ratio": pb_ratio,
        "roe_pct": roe_pct,
        "roce_pct": roce_pct,
        "dividend_yield_pct": 1.25,  # representative standard yield for Indian bluechips
        "latest_quarter": latest_q_dict,
        "latest_annual": latest_a_dict,
        "as_of": now_utc(),
        "demo_mode": DEMO_MODE,
        "source": "screener",
    }


def get_fundamentals_history(
    ticker: str,
    period_type: str = "annual",
    basis: str = "consolidated",
    limit: int = 12,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Return historical financial statements (income statement, balance sheet, cash flow)."""
    ticker_clean = ticker.strip().upper()
    basis_clean = basis.strip().lower()
    period_type_clean = period_type.strip().lower()

    if basis_clean not in ("consolidated", "standalone"):
        basis_clean = "consolidated"
    if period_type_clean not in ("annual", "quarterly"):
        period_type_clean = "annual"

    with connect(db_path) as conn:
        company = conn.execute(
            "SELECT name FROM companies WHERE ticker = ?",
            (ticker_clean,),
        ).fetchone()

        rows = conn.execute(
            """SELECT * FROM company_fundamentals
            WHERE ticker = ? AND basis = ? AND period_type = ?
            ORDER BY period_end ASC LIMIT ?""",
            (ticker_clean, basis_clean, period_type_clean, limit),
        ).fetchall()

        if not rows and basis_clean == "standalone":
            # If standalone not populated for this period_type, check consolidated
            rows = conn.execute(
                """SELECT * FROM company_fundamentals
                WHERE ticker = ? AND basis = 'consolidated' AND period_type = ?
                ORDER BY period_end ASC LIMIT ?""",
                (ticker_clean, period_type_clean, limit),
            ).fetchall()
            if rows:
                basis_clean = "consolidated"

    company_name = company["name"] if company else ticker_clean
    periods = [_row_to_period(r) for r in rows]

    return {
        "ticker": ticker_clean,
        "company_name": company_name,
        "basis": basis_clean,
        "period_type": period_type_clean,
        "count": len(periods),
        "as_of": now_utc(),
        "demo_mode": DEMO_MODE,
        "periods": periods,
    }


def get_fundamentals_ratios(
    ticker: str,
    basis: str = "consolidated",
    db_path: str | None = None,
) -> dict[str, Any]:
    """Return profitability ratios, margin trends, and financial health metrics."""
    ticker_clean = ticker.strip().upper()
    basis_clean = basis.strip().lower()
    if basis_clean not in ("consolidated", "standalone"):
        basis_clean = "consolidated"

    with connect(db_path) as conn:
        company = conn.execute(
            "SELECT name FROM companies WHERE ticker = ?",
            (ticker_clean,),
        ).fetchone()

        rows = conn.execute(
            """SELECT * FROM company_fundamentals
            WHERE ticker = ? AND basis = ?
            ORDER BY period_end ASC""",
            (ticker_clean, basis_clean),
        ).fetchall()

    company_name = company["name"] if company else ticker_clean

    trends = []
    latest_ratios: dict[str, float | None] = {
        "operating_margin_pct": None,
        "ebitda_margin_pct": None,
        "net_profit_margin_pct": None,
        "roe_pct": None,
        "roce_pct": None,
        "debt_to_equity": None,
        "interest_coverage": None,
    }

    for r in rows:
        row_dict = dict(r)
        borrowings = row_dict.get("total_borrowings")
        equity = row_dict.get("total_equity")
        d_e = round(borrowings / equity, 2) if (borrowings is not None and equity and equity > 0) else None

        ebit = (row_dict.get("operating_profit") or 0.0) + (row_dict.get("other_income") or 0.0)
        finance_costs = row_dict.get("finance_costs")
        int_cov = round(ebit / finance_costs, 2) if (finance_costs and finance_costs > 0 and ebit != 0) else None

        trend_pt = {
            "period_label": row_dict["period_label"],
            "period_end": row_dict["period_end"],
            "operating_margin_pct": row_dict.get("operating_margin_pct"),
            "ebitda_margin_pct": row_dict.get("ebitda_margin_pct"),
            "net_profit_margin_pct": row_dict.get("net_profit_margin_pct"),
            "roe_pct": row_dict.get("roe_pct"),
            "roce_pct": row_dict.get("roce_pct"),
            "debt_to_equity": d_e,
            "interest_coverage": int_cov,
        }
        trends.append(trend_pt)

    if trends:
        last = trends[-1]
        latest_ratios = {
            "operating_margin_pct": last.get("operating_margin_pct"),
            "ebitda_margin_pct": last.get("ebitda_margin_pct"),
            "net_profit_margin_pct": last.get("net_profit_margin_pct"),
            "roe_pct": last.get("roe_pct"),
            "roce_pct": last.get("roce_pct"),
            "debt_to_equity": last.get("debt_to_equity"),
            "interest_coverage": last.get("interest_coverage"),
        }

    return {
        "ticker": ticker_clean,
        "company_name": company_name,
        "basis": basis_clean,
        "as_of": now_utc(),
        "demo_mode": DEMO_MODE,
        "current_ratios": latest_ratios,
        "trends": trends,
    }
