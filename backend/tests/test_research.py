from __future__ import annotations

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.research import MODULE_METADATA, list_research_modules, synthesize_research
from app.schemas import ResearchModule


def test_list_research_modules() -> None:
    modules = list_research_modules()
    assert len(modules) == 8
    expected_keys = {"id", "title", "description", "icon", "category"}
    for mod in modules:
        assert expected_keys.issubset(mod.keys())
        assert mod["id"] in MODULE_METADATA


def test_synthesize_all_eight_modules_infy() -> None:
    modules: list[ResearchModule] = [
        "business_snapshot",
        "financial_snapshot",
        "trajectory",
        "balance_sheet",
        "cash_quality",
        "narrative_vs_numbers",
        "guidance",
        "bull_vs_bear",
    ]
    for mod in modules:
        result = synthesize_research("INFY", mod)
        assert result.ticker == "INFY"
        assert result.module == mod
        assert result.status == "complete"
        assert len(result.answer) > 50
        assert isinstance(result.findings, list)
        assert isinstance(result.citations, list)


def test_synthesize_other_covered_companies() -> None:
    for ticker in ["TCS", "RELIANCE", "HDFCBANK"]:
        res_snap = synthesize_research(ticker, "financial_snapshot")
        assert res_snap.ticker == ticker
        assert res_snap.status == "complete"
        assert len(res_snap.answer) > 20

        res_bull = synthesize_research(ticker, "bull_vs_bear")
        assert res_bull.ticker == ticker
        assert res_bull.status == "complete"


def test_synthesize_unknown_company_not_found() -> None:
    result = synthesize_research("NONEXISTENT_TICKER", "business_snapshot")
    assert result.ticker == "NONEXISTENT_TICKER"
    assert result.status == "not_found"
    assert "No reported financial filings" in result.answer


def test_fastapi_research_modules_endpoint() -> None:
    with TestClient(app) as client:
        resp = client.get("/research/modules")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 8
        assert len(data["modules"]) == 8


def test_fastapi_research_rest_and_streaming() -> None:
    with TestClient(app) as client:
        # 1. Direct REST endpoint
        rest_resp = client.get("/research/INFY/financial_snapshot")
        assert rest_resp.status_code == 200
        rest_data = rest_resp.json()
        assert rest_data["ticker"] == "INFY"
        assert rest_data["module"] == "financial_snapshot"
        assert rest_data["status"] == "complete"

        # 2. SSE streaming endpoint
        stream_resp = client.post("/research", json={"ticker": "INFY", "module": "bull_vs_bear"})
        assert stream_resp.status_code == 200
        assert "text/event-stream" in stream_resp.headers["content-type"]
        body = stream_resp.text
        assert "event: progress" in body
        assert "event: result" in body
        assert "source_discovery" in body
        assert "synthesis" in body
        assert "### Infosys Limited" in body
