import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import init_db
from app.promised_vs_delivered import (
    calculate_track_record,
    get_commitment_summary,
    get_company_commitments,
    load_commitments_fixture,
    save_commitments,
)
from app.main import app


@pytest.fixture
def test_db(tmp_path):
    db_file = str(tmp_path / "test_commitments.db")
    init_db(db_file)
    load_commitments_fixture(db_path=db_file)
    return db_file


def test_track_record_calculation():
    commitments = [
        {"category": "revenue_growth", "status": "beat"},
        {"category": "revenue_growth", "status": "met"},
        {"category": "margin", "status": "missed"},
        {"category": "capex_capacity", "status": "in_progress"},
    ]
    summary = calculate_track_record(commitments)
    assert summary["total_commitments"] == 4
    assert summary["beat_count"] == 1
    assert summary["met_count"] == 1
    assert summary["delivered_count"] == 2
    assert summary["missed_count"] == 1
    assert summary["in_progress_count"] == 1
    # 2 delivered out of 3 evaluated = 66.7%
    assert summary["delivery_score_pct"] == 66.7
    assert "revenue_growth" in summary["category_breakdown"]
    assert summary["category_breakdown"]["revenue_growth"]["delivery_score_pct"] == 100.0
    assert summary["category_breakdown"]["margin"]["delivery_score_pct"] == 0.0


def test_track_record_with_no_evaluated():
    commitments = [
        {"category": "operational", "status": "in_progress"},
    ]
    summary = calculate_track_record(commitments)
    assert summary["total_commitments"] == 1
    assert summary["delivery_score_pct"] == 100.0


def test_save_and_duplicate_prevention(test_db):
    item = {
        "ticker": "INFY",
        "category": "revenue_growth",
        "promise_headline": "Test 10% Revenue Growth",
        "promised_by": "CEO",
        "promised_at": "2024-01-01T00:00:00Z",
        "promised_period": "FY25",
        "promised_document": "Transcript",
        "promised_quote": "10% growth",
        "status": "in_progress",
        "delivery_assessment": "Underway",
    }
    # First insert
    count1 = save_commitments([item], db_path=test_db)
    assert count1 == 1

    # Second insert with updated status (upsert / duplicate prevention)
    item["status"] = "met"
    item["delivered_metric"] = "10.2%"
    count2 = save_commitments([item], db_path=test_db)
    assert count2 == 1

    res = get_company_commitments("INFY", db_path=test_db)
    matching = [c for c in res["commitments"] if c["promise_headline"] == "Test 10% Revenue Growth"]
    assert len(matching) == 1
    assert matching[0]["status"] == "met"
    assert matching[0]["delivered_metric"] == "10.2%"


def test_get_company_commitments_filtering(test_db):
    all_infy = get_company_commitments("INFY", db_path=test_db)
    assert all_infy is not None
    assert all_infy["count"] >= 4
    assert all_infy["track_record"]["total_commitments"] >= 4

    # Filter by category
    growth_only = get_company_commitments("INFY", category="revenue_growth", db_path=test_db)
    assert all(c["category"] == "revenue_growth" for c in growth_only["commitments"])

    # Filter by status
    met_only = get_company_commitments("INFY", status="met", db_path=test_db)
    assert all(c["status"] == "met" for c in met_only["commitments"])


def test_get_commitment_summary(test_db):
    summary = get_commitment_summary("INFY", db_path=test_db)
    assert summary is not None
    assert summary["ticker"] == "INFY"
    assert "delivery_score_pct" in summary
    assert summary["total_commitments"] >= 4


def test_api_commitments_routes():
    with TestClient(app) as client:
        # 1. Full commitments response
        r1 = client.get("/commitments/INFY")
        assert r1.status_code == 200
        data1 = r1.json()
        assert data1["ticker"] == "INFY"
        assert "track_record" in data1
        assert len(data1["commitments"]) >= 4

        # 2. Filtered by category
        r2 = client.get("/commitments/INFY?category=revenue_growth")
        assert r2.status_code == 200
        data2 = r2.json()
        assert all(c["category"] == "revenue_growth" for c in data2["commitments"])

        # 3. Filtered by status
        r3 = client.get("/commitments/INFY?status=missed")
        assert r3.status_code == 200
        data3 = r3.json()
        assert any(c["status"] == "missed" for c in data3["commitments"])

        # 4. Summary route
        r4 = client.get("/commitments/INFY/summary")
        assert r4.status_code == 200
        data4 = r4.json()
        assert "delivery_score_pct" in data4

        # 5. Nonexistent company returns 404
        r5 = client.get("/commitments/UNKNOWNXYZ")
        assert r5.status_code == 404
