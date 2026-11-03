import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import init_db
from app.fundamentals import (
    calculate_derived_metrics,
    get_fundamentals,
    get_fundamentals_history,
    get_fundamentals_ratios,
    load_fundamentals_fixture,
    save_fundamentals_records,
)
from app.main import app


@pytest.fixture
def test_db(tmp_path):
    db_file = str(tmp_path / "test_fundamentals.db")
    init_db(db_file)
    load_fundamentals_fixture(db_path=db_file)
    return db_file


def test_calculate_derived_metrics():
    raw = {
        "revenue": 1000.0,
        "total_expenses": 750.0,
        "other_income": 50.0,
        "operating_profit": None,  # should be calculated as 250.0
        "ebitda": None,            # should be calculated as 300.0 (250 + 50)
        "depreciation": 40.0,
        "finance_costs": 10.0,
        "pbt": 250.0,
        "tax": 60.0,
        "pat": 190.0,
        "total_equity": 800.0,
        "total_borrowings": 200.0,
        "cash_and_equivalents": 50.0,
        "net_debt": None,          # should be 150.0 (200 - 50)
        "cash_from_operations": 220.0,
        "capex": 70.0,
        "free_cash_flow": None,    # should be 150.0 (220 - 70)
    }
    calc, is_calc = calculate_derived_metrics(raw)

    assert calc["operating_profit"] == 250.0
    assert is_calc["operating_profit"] is True

    assert calc["ebitda"] == 300.0
    assert is_calc["ebitda"] is True

    assert calc["operating_margin_pct"] == 25.0
    assert is_calc["operating_margin_pct"] is True

    assert calc["ebitda_margin_pct"] == 30.0
    assert is_calc["ebitda_margin_pct"] is True

    assert calc["net_profit_margin_pct"] == 19.0
    assert is_calc["net_profit_margin_pct"] is True

    assert calc["net_debt"] == 150.0
    assert is_calc["net_debt"] is True

    assert calc["free_cash_flow"] == 150.0
    assert is_calc["free_cash_flow"] is True

    assert calc["roe_pct"] == 23.75  # 190 / 800 * 100
    assert is_calc["roe_pct"] is True

    # ROCE: EBIT (250 + 50 = 300) / Capital Employed (800 + 200 = 1000) = 30.0%
    assert calc["roce_pct"] == 30.0
    assert is_calc["roce_pct"] is True


def test_missing_data_handled_safely():
    sparse = {"revenue": 0.0}
    calc, is_calc = calculate_derived_metrics(sparse)
    assert calc["operating_margin_pct"] is None
    assert calc["ebitda"] is None
    assert calc["net_debt"] is None
    assert calc["free_cash_flow"] is None


def test_save_and_duplicate_prevention(test_db):
    rec = {
        "ticker": "INFY",
        "basis": "consolidated",
        "period_type": "annual",
        "period_end": "2030-03-31",
        "period_label": "FY30",
        "revenue": 200000.0,
        "pat": 35000.0,
    }
    # First insert
    count1 = save_fundamentals_records([rec], db_path=test_db)
    assert count1 == 1

    history1 = get_fundamentals_history("INFY", "annual", "consolidated", db_path=test_db)
    fy30 = next(p for p in history1["periods"] if p["period_end"] == "2030-03-31")
    assert fy30["revenue"] == 200000.0

    # Upsert with updated revenue (duplicate prevention)
    rec["revenue"] = 210000.0
    count2 = save_fundamentals_records([rec], db_path=test_db)
    assert count2 == 1

    history2 = get_fundamentals_history("INFY", "annual", "consolidated", db_path=test_db)
    matching = [p for p in history2["periods"] if p["period_end"] == "2030-03-31"]
    assert len(matching) == 1
    assert matching[0]["revenue"] == 210000.0


def test_get_fundamentals_overview(test_db):
    overview = get_fundamentals("INFY", basis="consolidated", db_path=test_db)
    assert overview is not None
    assert overview["ticker"] == "INFY"
    assert overview["company_name"] == "Infosys Limited"
    assert overview["latest_annual"] is not None
    assert overview["latest_annual"]["period_label"] == "FY26"
    assert overview["latest_annual"]["revenue"] == 174400.0
    assert overview["latest_quarter"] is not None
    assert overview["latest_quarter"]["period_label"] == "Q2 FY27"
    assert overview["latest_quarter"]["revenue"] == 45850.0
    assert overview["roe_pct"] is not None
    assert overview["roce_pct"] is not None


def test_get_fundamentals_history_quarterly_and_annual(test_db):
    annual_data = get_fundamentals_history("INFY", period_type="annual", basis="consolidated", db_path=test_db)
    assert annual_data["count"] >= 4
    assert [p["period_label"] for p in annual_data["periods"][:4]] == ["FY23", "FY24", "FY25", "FY26"]

    quarterly_data = get_fundamentals_history("INFY", period_type="quarterly", basis="consolidated", db_path=test_db)
    assert quarterly_data["count"] >= 6
    quarter_labels = [p["period_label"] for p in quarterly_data["periods"]]
    assert "Q1 FY26" in quarter_labels
    assert "Q2 FY27" in quarter_labels


def test_get_fundamentals_ratios_and_trends(test_db):
    ratios = get_fundamentals_ratios("INFY", basis="consolidated", db_path=test_db)
    assert ratios["ticker"] == "INFY"
    assert len(ratios["trends"]) > 0
    assert "operating_margin_pct" in ratios["current_ratios"]
    assert "ebitda_margin_pct" in ratios["current_ratios"]
    assert "net_profit_margin_pct" in ratios["current_ratios"]
    assert "roe_pct" in ratios["current_ratios"]
    assert "roce_pct" in ratios["current_ratios"]


def test_api_fundamentals_routes():
    with TestClient(app) as client:
        # 1. Overview
        r1 = client.get("/fundamentals/INFY")
        assert r1.status_code == 200
        data1 = r1.json()
        assert data1["ticker"] == "INFY"
        assert data1["company_name"] == "Infosys Limited"
        assert data1["latest_annual"]["period_label"] == "FY26"

        # 2. History (quarterly & annual)
        r2 = client.get("/fundamentals/INFY/history?period_type=quarterly&basis=consolidated")
        assert r2.status_code == 200
        data2 = r2.json()
        assert data2["count"] >= 6
        assert data2["periods"][-1]["period_label"] == "Q2 FY27"

        # 3. Ratios
        r3 = client.get("/fundamentals/INFY/ratios")
        assert r3.status_code == 200
        data3 = r3.json()
        assert "trends" in data3
        assert len(data3["trends"]) > 0

        # 4. Unknown ticker returns 404
        r4 = client.get("/fundamentals/UNKNOWNXYZ")
        assert r4.status_code == 404
