from datetime import datetime, timedelta, timezone
import sqlite3

from fastapi.testclient import TestClient

from app.db import init_db
from app.digest import build_source_items, rank_event, select_digest_items
from app.main import app

AS_OF = datetime(2026, 10, 31, tzinfo=timezone.utc)


def make_item(id, ticker="INFY", category="results", materiality=7, days=0, **extra):
    value = {"id": id, "ticker": ticker, "company_name": "Infosys Limited", "kind": "filing",
             "category": category, "headline": id, "materiality_score": materiality,
             "occurred_at": AS_OF - timedelta(days=days), "summary": "Source summary",
             "source_reference": "fixture-1", "attachment_url": None, "data_source": "fixture",
             "demo_mode": True, "citations": [], "supporting_details": {}, "priority": "medium", "collapsed_count": 1}
    value.update(extra)
    return value


def test_rank_is_materiality_category_recency_and_portfolio_explainable():
    high = rank_event(make_item("high", materiality=9, days=1), as_of=AS_OF, portfolio_tickers={"INFY"})
    low = rank_event(make_item("low", category="agm_egm", materiality=1, days=40), as_of=AS_OF)
    assert high["rank_score"] > low["rank_score"]
    assert any("Source materiality 9/10" in reason for reason in high["rank_reasons"])
    assert "Company is marked in the portfolio" in high["rank_reasons"]


def test_missing_materiality_remains_unavailable_for_anomaly():
    anomaly = make_item("anom", category="price_volume_anomaly", materiality=None, priority=None)
    result = rank_event(anomaly, as_of=AS_OF)
    assert result["materiality_score"] is None
    assert result["priority"] == "high"


def test_anomalies_same_ticker_session_are_grouped_once():
    rows = [
        {"id": "v", "ticker": "INFY", "anomaly_type": "volume_spike", "detected_at": "2026-10-30", "explanation": "Volume 3x", "data_source": "fixture-csv", "demo_mode": True},
        {"id": "p", "ticker": "INFY", "anomaly_type": "price_move", "detected_at": "2026-10-30", "explanation": "Price +4%", "data_source": "fixture-csv", "demo_mode": True},
    ]
    items, collapsed = build_source_items(announcements=[], anomalies=rows, management_events=[], results_cards=[],
        enriched_filings=[], company_names={"INFY": "Infosys Limited"}, portfolio_tickers=set(), as_of=AS_OF)
    assert len(items) == 1
    assert items[0]["category"] == "price_volume_anomaly"
    assert len(items[0]["supporting_details"]["anomalies"]) == 2
    assert collapsed == 0


def test_related_routine_announcements_collapse():
    items = [make_item("one", category="postal_ballot", materiality=1), make_item("two", category="postal_ballot", materiality=1, days=1)]
    grouped, collapsed = build_source_items(announcements=items, anomalies=[], management_events=[], results_cards=[],
        enriched_filings=[], company_names={}, portfolio_tickers=set(), as_of=AS_OF)
    assert len(grouped) == 1
    assert grouped[0]["collapsed_count"] == 2
    assert collapsed == 1


def test_duplicate_announcements_suppress_same_ticker_category_headline():
    rows = [make_item("first", headline="Duplicate filing"), make_item("second", headline="Duplicate filing", days=1)]
    items, collapsed = build_source_items(announcements=rows, anomalies=[], management_events=[], results_cards=[],
        enriched_filings=[], company_names={}, portfolio_tickers=set(), as_of=AS_OF)
    assert len(items) == 1
    assert items[0]["supporting_details"]["duplicate_count"] == 2
    assert collapsed == 1


def test_management_event_enriches_announcement_without_duplicate_card():
    announcement = {"id": "ann1", "ticker": "INFY", "company_name": "Infosys Limited", "timestamp": "2026-10-30T10:00:00Z",
        "headline": "CEO appointed", "classification": "management_change", "materiality_score": 8,
        "source_identifier": "filing-1", "source": "fixture", "raw_metadata": {}}
    management = {"announcement_id": "ann1", "explanation": "A CEO was appointed", "person_name": None,
        "role_category": "md_ceo", "change_type": "appointment", "effective_date": None, "extraction_status": "incomplete"}
    items, _ = build_source_items(announcements=[announcement], anomalies=[], management_events=[management],
        results_cards=[], enriched_filings=[], company_names={}, portfolio_tickers=set(), as_of=AS_OF)
    assert len(items) == 1
    assert items[0]["summary"] == "A CEO was appointed"
    assert "management_change" in items[0]["supporting_details"]


def test_results_card_merges_only_on_exact_source_reference():
    announcement = {"id": "ann1", "ticker": "INFY", "company_name": "Infosys Limited", "timestamp": "2026-10-30T10:00:00Z",
        "headline": "Results filed", "classification": "results", "materiality_score": 9,
        "attachment_url": "https://example.test/results.pdf", "source": "fixture", "raw_metadata": {}}
    card = {"parse_failed": False, "source_url": "https://example.test/results.pdf", "reporting_basis": "consolidated",
        "what_stands_out": ["Revenue increased in the reported quarter."]}
    items, _ = build_source_items(announcements=[announcement], anomalies=[], management_events=[],
        results_cards=[{"ticker": "INFY", "filing_id": "f1", "headline": "Results", "filed_at": "2026-10-30T10:00:00Z", "source": "fixture", "card": card}],
        enriched_filings=[], company_names={}, portfolio_tickers=set(), as_of=AS_OF)
    assert len(items) == 1
    assert items[0]["supporting_details"]["results_card"]["reporting_basis"] == "consolidated"


def test_filters_sort_and_pagination():
    values = [rank_event(make_item("a", ticker="INFY", materiality=9), as_of=AS_OF),
              rank_event(make_item("b", ticker="TCS", category="dividend", materiality=5, days=1), as_of=AS_OF),
              rank_event(make_item("c", ticker="INFY", category="price_anomaly", materiality=None, days=2), as_of=AS_OF)]
    page, total = select_digest_items(values, start=AS_OF - timedelta(days=7), end=AS_OF,
        ticker="INFY", min_materiality=5, limit=1, offset=0)
    assert total == 1 and [x["id"] for x in page] == ["a"]
    recent, _ = select_digest_items(values, start=AS_OF - timedelta(days=7), end=AS_OF,
        sort="recency", limit=1)
    assert recent[0]["id"] == "a"


def test_empty_and_missing_timestamp_are_safely_omitted():
    items, total = select_digest_items([make_item("missing", occurred_at=None)], start=AS_OF-timedelta(days=7), end=AS_OF)
    assert items == [] and total == 0


def test_digest_api_filters_pagination_invalid_and_custom_window(tmp_path, monkeypatch):
    from app import main
    db_path = tmp_path / "digest-api.db"
    init_db(str(db_path))
    with sqlite3.connect(db_path) as conn:
        conn.execute("INSERT INTO companies(ticker,name,is_portfolio) VALUES('INFY','Infosys Limited',1)")
    monkeypatch.setattr(main, "connect", lambda: __import__("app.db", fromlist=["connect"]).connect(str(db_path)))
    monkeypatch.setattr(main, "list_announcements", lambda **kwargs: [
        {"id": "api-a", "ticker": "INFY", "company_name": "Infosys Limited", "timestamp": "2026-10-30T10:00:00Z",
         "headline": "Quarterly results", "classification": "results", "materiality_score": 9, "source": "fixture",
         "source_identifier": "fixture-a", "raw_metadata": {}, "attachment_url": None, "summary": "Filing summary"},
        {"id": "api-b", "ticker": "TCS", "company_name": "TCS Limited", "timestamp": "2026-10-29T10:00:00Z",
         "headline": "Dividend announced", "classification": "dividend", "materiality_score": 5, "source": "fixture",
         "source_identifier": "fixture-b", "raw_metadata": {}, "attachment_url": None, "summary": "Dividend summary"},
    ])
    monkeypatch.setattr(main, "refresh_anomalies", lambda **kwargs: ([], AS_OF, True))
    monkeypatch.setattr(main, "price_data_source", lambda **kwargs: "fixture-csv")
    monkeypatch.setattr(main, "list_management_changes", lambda **kwargs: [])
    monkeypatch.setattr(main, "announcement_snapshot_as_of", lambda *args, **kwargs: AS_OF)
    with TestClient(app) as client:
        response = client.get("/digest?window=7d&ticker=INFY&category=results&min_materiality=8&limit=1")
        assert response.status_code == 200
        body = response.json()
        assert body["total_count"] == 1 and body["items"][0]["ticker"] == "INFY"
        assert body["demo_mode"] is True and body["items"][0]["source_reference"] == "fixture-a"
        assert client.get("/digest?window=7d&limit=1").json()["total_count"] == 2
        assert client.get("/digest?window=7d&limit=1&offset=1").json()["items"][0]["ticker"] == "TCS"
        assert client.get("/digest?category=unknown-value").status_code == 422
        assert client.get("/digest?window=custom&from=2026-10-01T00:00:00Z").status_code == 422
        custom = client.get("/digest?window=custom&from=2026-10-29T00:00:00Z&to=2026-10-31T00:00:00Z")
        assert custom.status_code == 200
        monkeypatch.setattr(main, "price_data_source", lambda **kwargs: "none")
        monkeypatch.setattr(main, "refresh_anomalies", lambda **kwargs: ([], datetime(2027, 1, 1, tzinfo=timezone.utc), False))
        frozen = client.get("/digest?window=7d").json()
        assert frozen["as_of"] == AS_OF.isoformat().replace("+00:00", "Z")
