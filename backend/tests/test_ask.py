from __future__ import annotations

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

from app.ask import get_conversation_history, get_suggested_questions, process_ask_query
from app.main import app


def test_get_suggested_questions() -> None:
    for ticker in ["INFY", "TCS", "RELIANCE", "HDFCBANK"]:
        suggestions = get_suggested_questions(ticker)
        assert len(suggestions) >= 3
        assert any(ticker in s or "management" in s.lower() or "revenue" in s.lower() for s in suggestions)


def test_ask_revenue_query_infy(tmp_path) -> None:
    db_file = str(tmp_path / "test_ask.db")
    from app.db import init_db
    from app.fundamentals import load_fundamentals_fixture
    from app.promised_vs_delivered import load_commitments_fixture

    init_db(db_file)
    load_fundamentals_fixture(db_file)
    load_commitments_fixture(db_file)

    resp = process_ask_query(
        ticker="INFY",
        question="What was Infosys FY24 revenue and growth guidance?",
        db_path=db_file,
    )
    assert resp.ticker == "INFY"
    assert resp.status == "answered"
    assert "₹174,400" in resp.answer or "Revenue" in resp.answer
    assert len(resp.citations) >= 1
    assert resp.citations[0].document != ""
    assert resp.citations[0].quote != ""
    assert len(resp.suggested_followups) >= 2


def test_ask_margin_and_ebitda_query_infy(tmp_path) -> None:
    db_file = str(tmp_path / "test_ask.db")
    from app.db import init_db
    from app.fundamentals import load_fundamentals_fixture
    from app.promised_vs_delivered import load_commitments_fixture

    init_db(db_file)
    load_fundamentals_fixture(db_file)
    load_commitments_fixture(db_file)

    resp = process_ask_query(
        ticker="INFY",
        question="What are the operating margins and EBITDA for Infosys?",
        db_path=db_file,
    )
    assert resp.status == "answered"
    assert "margin" in resp.answer.lower()
    assert len(resp.citations) >= 1


def test_ask_management_credibility_query_infy(tmp_path) -> None:
    db_file = str(tmp_path / "test_ask.db")
    from app.db import init_db
    from app.fundamentals import load_fundamentals_fixture
    from app.promised_vs_delivered import load_commitments_fixture

    init_db(db_file)
    load_fundamentals_fixture(db_file)
    load_commitments_fixture(db_file)

    resp = process_ask_query(
        ticker="INFY",
        question="Did management deliver on its commitments and what was missed?",
        db_path=db_file,
    )
    assert resp.status == "answered"
    assert "75.0%" in resp.answer or "Delivery Score" in resp.answer
    assert "MISSED" in resp.answer or "Constant Currency" in resp.answer
    assert len(resp.citations) >= 1


def test_ask_unknown_ticker_returns_not_found(tmp_path) -> None:
    db_file = str(tmp_path / "test_ask.db")
    from app.db import init_db

    init_db(db_file)
    resp = process_ask_query(
        ticker="UNKNOWN_CORP",
        question="What was last quarter net profit?",
        db_path=db_file,
    )
    assert resp.status == "not_found"
    assert "not found in sources" in resp.answer


def test_ask_conversation_persistence_and_multi_turn(tmp_path) -> None:
    db_file = str(tmp_path / "test_ask.db")
    from app.db import init_db
    from app.fundamentals import load_fundamentals_fixture
    from app.promised_vs_delivered import load_commitments_fixture

    init_db(db_file)
    load_fundamentals_fixture(db_file)
    load_commitments_fixture(db_file)

    conv_id = "test_conversation_123"

    # Turn 1
    resp1 = process_ask_query(
        ticker="INFY",
        question="What was FY24 revenue?",
        conversation_id=conv_id,
        db_path=db_file,
    )
    assert resp1.conversation_id == conv_id

    # Turn 2
    resp2 = process_ask_query(
        ticker="INFY",
        question="What is the net debt on the balance sheet?",
        conversation_id=conv_id,
        db_path=db_file,
    )
    assert resp2.conversation_id == conv_id

    # Verify history
    history = get_conversation_history(conv_id, db_path=db_file)
    assert len(history) == 4  # 2 user messages + 2 assistant responses
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
    assert history[2]["role"] == "user"
    assert history[3]["role"] == "assistant"


def test_fastapi_ask_routes() -> None:
    with TestClient(app) as client:
        # 1. Suggestions route
        sugg_resp = client.get("/ask/suggestions/INFY")
        assert sugg_resp.status_code == 200
        assert len(sugg_resp.json()["suggestions"]) >= 3

        # 2. Ask query route
        ask_resp = client.post("/ask", json={
            "ticker": "INFY",
            "question": "What is the Free Cash Flow conversion and capital return?",
        })
        assert ask_resp.status_code == 200
        body = ask_resp.json()
        assert body["status"] == "answered"
        assert body["ticker"] == "INFY"
        assert len(body["answer"]) > 50
        assert len(body["citations"]) >= 1
        conv_id = body["conversation_id"]

        # 3. History route
        hist_resp = client.get(f"/ask/history/{conv_id}")
        assert hist_resp.status_code == 200
        assert hist_resp.json()["count"] >= 2
