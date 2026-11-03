from __future__ import annotations

import asyncio
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import announcements as ann
from app.db import connect, init_db


def _raw(headline: str, *, timestamp="2026-10-31T10:00:00+05:30", **extra):
    return {"headline": headline, "timestamp": timestamp, **extra}


def _item(headline="Unrecognized disclosure", ticker="INFY", **extra):
    return ann.normalize_announcement(_raw(headline, **extra), ticker, "bse")


def test_timestamp_parsing_returns_aware_utc_for_exchange_formats():
    parsed = ann.parse_timestamp("31-10-2026 10:00:00")
    assert parsed.tzinfo is timezone.utc
    assert parsed.isoformat() == "2026-10-31T04:30:00+00:00"
    assert ann.parse_timestamp("2026-10-31T10:00:00+05:30").isoformat() == parsed.isoformat()


def test_normalization_preserves_identifier_metadata_and_attachment():
    normalized = ann.normalize_announcement({
        "NEWSID": "bse-778", "DT_TM": "31 Oct 2026 10:00:00", "NEWSSUB": "  Board   declares dividend ",
        "CATEGORYNAME": "Corp. Action", "ATTACHMENTNAME": "files/demo.pdf", "SCRIP_CD": "500209",
    }, "INFY.NS", "bse")
    assert normalized["ticker"] == "INFY"
    assert normalized["source_identifier"] == "bse-778"
    assert normalized["timestamp"] == "2026-10-31T04:30:00Z"
    assert normalized["headline"] == "Board declares dividend"
    assert normalized["raw_category"] == "Corp. Action"
    assert normalized["attachment_url"].endswith("/files/demo.pdf")
    assert normalized["raw_metadata"]["SCRIP_CD"] == "500209"


def test_normalization_rejects_missing_timestamp_and_headline():
    with pytest.raises(ValueError, match="headline"):
        ann.normalize_announcement({"DT": "31-10-2026"}, "INFY", "nse")
    with pytest.raises(ValueError, match="timestamp"):
        ann.normalize_announcement({"DESC": "some notice"}, "INFY", "nse")


@pytest.mark.parametrize(("headline", "category"), [
    ("Board approves quarterly financial results", "results"),
    ("Subsidiary enters into an acquisition agreement", "M&A"),
    ("Board approves qualified institutional placement", "fund_raise"),
    ("Chief Financial Officer resigns", "management_change"),
    ("Independent director appointed", "management_change"),
    ("Tribunal issues regulatory order", "litigation"),
    ("Disclosure of acquisition of shares by designated person", "insider_trading"),
    ("Earnings conference call scheduled", "earnings_call"),
    ("Investor meeting participation notice", "investor_meetings"),
    ("Credit rating downgraded", "credit_rating"),
    ("Board declares interim dividend", "dividend"),
    ("Bonus issue of equity shares", "bonus_split"),
    ("Capacity expansion at new plant", "capex"),
    ("Press release on operating update", "press_release"),
    ("Notice of postal ballot", "postal_ballot"),
    ("Annual general meeting notice", "agm_egm"),
    ("Promoter reports change in pledge", "pledging"),
    ("Secretarial compliance certificate filed", "unclassified"),
])
def test_taxonomy_rules_cover_categories_and_routine_compliance(headline, category):
    assert ann.classify_rules(headline)["classification"] == category


@pytest.mark.parametrize(("category", "headline", "expected"), [
    ("results", "Quarterly results", 9), ("M&A", "Merger", 8),
    ("fund_raise", "QIP", 7), ("management_change", "CEO resignation", 8),
    ("management_change", "Director appointment", 5), ("litigation", "Court order", 7),
    ("fund_raise", "Rights issue", 7), ("credit_rating", "Rating downgrade", 7),
    ("credit_rating", "Rating upgrade", 6), ("credit_rating", "Rating reaffirmed", 3),
    ("capex", "Capacity expansion", 6), ("dividend", "Interim dividend", 5),
    ("pledging", "Pledge change", 6), ("insider_trading", "Insider trade disclosure", 4),
    ("earnings_call", "Earnings call", 3), ("investor_meetings", "Investor meeting", 2),
    ("postal_ballot", "Postal ballot", 1), ("agm_egm", "AGM", 1),
    ("bonus_split", "Bonus issue", 4), ("press_release", "Press release", 2),
    ("unclassified", "Secretarial compliance certificate", 1),
    ("unclassified", "Employee stock options exercised and shares allotted", 1),
    ("unclassified", "Unknown disclosure", 0),
])
def test_materiality_base_scores(category, headline, expected):
    score, _ = ann.materiality_base_score(category, headline)
    assert score == expected


def test_credit_rating_action_directions_have_distinct_scores():
    assert ann.materiality_base_score("credit_rating", "Rating downgraded")[0] == 7
    assert ann.materiality_base_score("credit_rating", "Rating upgraded")[0] == 6
    assert ann.materiality_base_score("credit_rating", "Rating reaffirmed")[0] == 3


@pytest.mark.parametrize(("requested", "expected"), [(9, 2), (-8, -2), (1.5, 1.5), (float("inf"), 0)])
def test_model_adjustment_is_clamped_to_two_points(requested, expected):
    result = ann.calculate_materiality("results", "Quarterly results", model_adjustment=requested)
    assert result["model_adjustment"] == expected
    assert 0 <= result["materiality_score"] <= 10


def test_materiality_clamps_final_score_to_zero_and_ten():
    assert ann.calculate_materiality("results", "results", model_adjustment=2)["materiality_score"] == 10
    assert ann.calculate_materiality("press_release", "release", model_adjustment=-2)["materiality_score"] == 0


def test_summary_is_source_headline_only_and_requires_score_five():
    low = ann.enrich_announcement(_item("Investor meeting to be held"))
    high = ann.enrich_announcement(_item("Board declares dividend"))
    assert low["materiality_score"] == 2
    assert low["summary"] is None
    assert high["materiality_score"] == 5
    assert high["summary"] == "Board declares dividend"


def test_missing_attachment_is_normalized_to_none():
    item = ann.normalize_announcement(_raw("Dividend declared"), "INFY", "nse")
    assert item["attachment_url"] is None


def test_fingerprint_deduplicates_sources_and_headline_formatting():
    first = ann.announcement_fingerprint("INFY", "2026-10-31T10:00:00+05:30", "Dividend declared!")
    second = ann.announcement_fingerprint("INFY.NS", "2026-10-31T04:30:00Z", " dividend   DECLARED ")
    assert first == second


def test_persistence_is_idempotent_and_merges_cross_exchange_source_trace(tmp_path):
    db_path = str(tmp_path / "announcements.db")
    init_db(db_path)
    bse = ann.enrich_announcement(ann.normalize_announcement(_raw("Board declares dividend", NEWSID="BSE1"), "INFY", "bse"))
    nse = ann.enrich_announcement(ann.normalize_announcement(_raw("board declares DIVIDEND!", seq_id="NSE1"), "INFY", "nse"))
    assert ann.persist_announcements([bse], db_path=db_path) == 1
    assert ann.persist_announcements([bse], db_path=db_path) == 0
    assert ann.persist_announcements([nse], db_path=db_path) == 0
    stored = ann.list_announcements(ticker="INFY", db_path=db_path)
    assert len(stored) == 1
    assert set(stored[0]["raw_metadata"]["duplicate_sources"]) == {"bse", "nse"}
    assert "nse:NSE1" in stored[0]["raw_metadata"]["duplicate_source_identifiers"]


def test_exchange_identifier_also_deduplicates_if_headline_or_timestamp_changes(tmp_path):
    db_path = str(tmp_path / "source-id.db")
    init_db(db_path)
    first = ann.enrich_announcement(ann.normalize_announcement(
        _raw("Board declares dividend", NEWSID="BSE-SAME"), "INFY", "bse"))
    revised = ann.enrich_announcement(ann.normalize_announcement(
        _raw("Board declares final dividend", NEWSID="BSE-SAME", timestamp="2026-10-31T10:01:00+05:30"),
        "INFY", "bse"))
    assert ann.persist_announcements([first], db_path=db_path) == 1
    assert ann.persist_announcements([revised], db_path=db_path) == 0
    assert len(ann.list_announcements(ticker="INFY", db_path=db_path)) == 1


def test_mapping_prefers_isin_and_persists_verification_metadata(tmp_path):
    db_path = str(tmp_path / "mapping.db")
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute("INSERT INTO companies(ticker,name,isin) VALUES('INFY','Infosys Limited','INE009A01021')")
    now = datetime.now(timezone.utc)
    report = ann.refresh_bse_mappings([{
        "SCRIP_CD": "500209", "SCRIP_NAME": "Infosys Ltd", "ISIN_CODE": "INE009A01021",
    }], db_path=db_path, now=now)
    mapping = ann.get_bse_mapping("INFY", db_path=db_path)
    assert report["updated"] == 1
    assert mapping["bse_scrip_code"] == "500209"
    assert mapping["nse_symbol"] == "INFY"
    assert mapping["mapping_source"] == "bse_security_master:isin"
    assert mapping["last_verified_at"] == now.isoformat(timespec="seconds").replace("+00:00", "Z")


def test_mapping_supports_verified_nse_symbol_and_name_match(tmp_path):
    db_path = str(tmp_path / "mapping.db")
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute("INSERT INTO companies(ticker,name) VALUES('ABC','Alpha Beta Corporation')")
        conn.execute("INSERT INTO companies(ticker,name) VALUES('XYZ','XYZ Holdings Limited')")
    report = ann.refresh_bse_mappings([
        {"SCRIP_CD": "111111", "NAME": "Different name", "NSE_SYMBOL": "ABC"},
        {"SCRIP_CD": "222222", "NAME": "XYZ Holdings Limited"},
    ], db_path=db_path)
    assert report["updated"] == 2
    assert ann.get_bse_mapping("ABC", db_path=db_path)["mapping_source"].endswith(":nse_symbol")
    assert ann.get_bse_mapping("XYZ", db_path=db_path)["mapping_source"].endswith(":company_name_exact")


def test_ambiguous_company_name_mapping_is_not_saved(tmp_path):
    db_path = str(tmp_path / "mapping.db")
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute("INSERT INTO companies(ticker,name) VALUES('ABC','Alpha Beta Limited')")
    report = ann.refresh_bse_mappings([
        {"SCRIP_CD": "111111", "NAME": "Alpha Beta Ltd"},
        {"SCRIP_CD": "222222", "NAME": "Alpha Beta Ltd"},
    ], db_path=db_path)
    assert "ABC" in report["ambiguous"]
    with pytest.raises(ann.MappingNotFound):
        ann.get_bse_mapping("ABC", db_path=db_path)


def test_stale_mapping_is_not_silently_used(tmp_path):
    db_path = str(tmp_path / "stale.db")
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute("""INSERT INTO announcement_mappings
          (ticker,nse_symbol,company_name,bse_scrip_code,mapping_source,mapping_confidence,last_verified_at)
          VALUES('INFY','INFY','Infosys Limited','500209','test_master',1,'2020-01-01T00:00:00Z')""")
    with pytest.raises(ann.MappingNotFound, match="refresh the security master"):
        ann.get_bse_mapping("INFY", db_path=db_path)


def test_name_mapping_refuses_weak_or_ambiguous_close_candidates(tmp_path):
    db_path = str(tmp_path / "mapping.db")
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute("INSERT INTO companies(ticker,name) VALUES('ABC','Alpha Beta Limited')")
    report = ann.refresh_bse_mappings([
        {"SCRIP_CD": "111111", "NAME": "Alpha Beta Industries"},
        {"SCRIP_CD": "222222", "NAME": "Alpha Beta Industrial"},
    ], db_path=db_path)
    assert "ABC" in report["ambiguous"] or "ABC" in report["missing"]
    with pytest.raises(ann.MappingNotFound):
        ann.get_bse_mapping("ABC", db_path=db_path)


def test_security_master_csv_is_parsed():
    rows = ann.parse_security_master(b"SCRIP_CD,ISIN_CODE,SCRIP_NAME\r\n500209,INE009A01021,Infosys Ltd\r\n")
    assert rows[0]["SCRIP_CD"] == "500209"


def test_bse_failure_uses_nse_then_persists_live_source(tmp_path):
    db_path = str(tmp_path / "fallback.db")
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute("INSERT INTO companies(ticker,name) VALUES('INFY','Infosys Limited')")
        conn.execute("""INSERT INTO announcement_mappings
          (ticker,nse_symbol,company_name,bse_scrip_code,mapping_source,mapping_confidence,last_verified_at)
          VALUES('INFY','INFY','Infosys Limited','500209','test_master',1,?)""",
          (datetime.now(timezone.utc).isoformat(),))
    calls = []

    def fail_bse(*args):
        calls.append("bse")
        raise ann.AnnouncementSourceError("rate limited")

    def use_nse(ticker, start, end):
        calls.append("nse")
        return [{"seq_id": "NSE-1", "symbol": ticker, "an_dt": "31-10-2026 10:00:00", "desc": "Board declares dividend"}]

    result = asyncio.run(ann.ingest_announcements(
        "INFY", from_date=date(2026, 10, 1), to_date=date(2026, 10, 31),
        db_path=db_path, bse_fetcher=fail_bse, nse_fetcher=use_nse,
    ))
    assert calls == ["bse", "nse"]
    assert result["source"] == "nse" and result["demo_mode"] is False
    assert result["inserted"] == 1
    assert result["announcements"][0]["source"] == "nse"


def test_fixture_fallback_is_explicit_demo_data_when_both_sources_fail(tmp_path):
    db_path = str(tmp_path / "fallback.db")
    init_db(db_path)
    def fail(*args):
        raise ann.AnnouncementSourceError("blocked")
    result = asyncio.run(ann.ingest_announcements(
        "INFY", from_date=date(2026, 10, 1), to_date=date(2026, 10, 31),
        db_path=db_path, bse_fetcher=fail, nse_fetcher=fail,
    ))
    assert result["source"] == "fixture"
    assert result["demo_mode"] is True
    assert result["received"] >= 1
    assert all(item["source"] == "fixture" for item in result["announcements"])
    assert all(item["raw_metadata"]["demo_data"] for item in result["announcements"])


def test_demo_ingestion_never_calls_live_sources(tmp_path):
    db_path = str(tmp_path / "fixture.db")
    init_db(db_path)
    def forbidden(*args):
        raise AssertionError("live source called in demo mode")
    result = asyncio.run(ann.ingest_announcements(
        "INFY", from_date=date(2026, 10, 1), to_date=date(2026, 10, 31),
        db_path=db_path, demo_mode=True, bse_fetcher=forbidden, nse_fetcher=forbidden,
    ))
    assert result["source"] == "fixture" and result["demo_mode"] is True


def test_fixture_covers_all_taxonomy_categories_and_is_labeled_demo():
    items = ann.load_fixture_announcements()
    classified = {ann.classify_rules(item["headline"], item["raw_category"])["classification"] for item in items}
    assert len(items) >= 30
    assert set(ann.TAXONOMY) <= classified
    payload = json.loads(ann.DEFAULT_FIXTURE.read_text(encoding="utf-8"))
    assert payload["demo_data"] is True
    assert "Synthetic" in payload["disclaimer"]


def test_bse_retries_rate_limit_and_uses_browser_headers():
    calls = []
    waits = []
    def handler(request):
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(429, headers={"Retry-After": "0"}, json={"error": "slow down"})
        return httpx.Response(200, json={"Table": [{"NEWSID": "x"}], "Table1": [{"ROWCNT": 1}]})
    client = httpx.Client(transport=httpx.MockTransport(handler))
    rows = ann.fetch_bse_announcements(
        "500209", date(2026, 10, 1), date(2026, 10, 31), client=client,
        retries=2, request_interval=0, sleep=waits.append,
    )
    assert len(rows) == 1
    assert len(calls) == 2
    assert calls[0].headers["origin"] == "https://www.bseindia.com"
    assert "Chrome/" in calls[0].headers["user-agent"]
    assert waits == [0.0]
    client.close()


def test_bse_paginates_until_row_count_is_satisfied():
    calls = []
    def handler(request):
        calls.append(request)
        page = int(request.url.params["pageno"])
        row = {"NEWSID": str(page)}
        return httpx.Response(200, json={"Table": [row], "Table1": [{"ROWCNT": 2}]})
    client = httpx.Client(transport=httpx.MockTransport(handler))
    rows = ann.fetch_bse_announcements("500209", date(2026, 10, 1), date(2026, 10, 31), client=client, request_interval=0)
    assert len(rows) == 2 and len(calls) == 2
    assert calls[1].url.params["pageno"] == "2"
    client.close()


def test_nse_cookie_handshake_reuses_cookie_and_browser_headers():
    seen = []
    def handler(request):
        seen.append(request)
        if request.url.host == "www.nseindia.com" and request.url.path == "/":
            return httpx.Response(200, headers={"Set-Cookie": "sessionid=warm; Path=/"}, text="home")
        return httpx.Response(200, json=[{"seq_id": "N1", "desc": "notice"}])
    client = httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)
    rows = ann.fetch_nse_announcements(
        "INFY", date(2026, 10, 1), date(2026, 10, 31), client=client,
        request_interval=0, sleep=lambda _: None,
    )
    assert rows[0]["seq_id"] == "N1"
    assert len(seen) == 2
    assert "sessionid=warm" in seen[1].headers.get("cookie", "")
    assert seen[1].headers["referer"].startswith("https://www.nseindia.com/")
    assert seen[1].url.params["symbol"] == "INFY"
    client.close()


def test_bse_access_denial_is_not_retried_or_bypassed():
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(403, text="access denied")
    client = httpx.Client(transport=httpx.MockTransport(handler))
    with pytest.raises(ann.AnnouncementSourceError, match="no access-control bypass"):
        ann.fetch_bse_announcements("500209", date(2026, 10, 1), date(2026, 10, 31), client=client, retries=3)
    assert len(calls) == 1
    client.close()


def test_bse_retries_timeout_then_reports_unavailable():
    calls = []
    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout("timeout", request=request)
    client = httpx.Client(transport=httpx.MockTransport(handler))
    with pytest.raises(ann.AnnouncementSourceError, match="after 3 attempts"):
        ann.fetch_bse_announcements("500209", date(2026, 10, 1), date(2026, 10, 31), client=client,
                                    retries=2, request_interval=0, sleep=lambda _: None)
    assert len(calls) == 3
    client.close()


def test_model_batches_are_limited_to_twenty_and_rules_are_not_overridden():
    items = [_item(f"Novel disclosure number {i}") for i in range(41)]
    items.append(_item("Board declares interim dividend"))
    batch_sizes = []
    async def fake_model(**kwargs):
        data = json.loads(kwargs["user"])["announcements"]
        batch_sizes.append(len(data))
        return {"results": [
            {"index": row["index"], "classification": "unclassified", "confidence": 0.1,
             "materiality_adjustment": 0, "reason": "uncertain"}
            for row in data
        ]}
    result = asyncio.run(ann.classify_unresolved(items, model_call=fake_model))
    assert batch_sizes == [20, 20, 1]
    assert result[-1]["classification"] == "dividend"
    assert result[-1]["classification_method"] == "rules"


def test_model_invalid_taxonomy_is_not_accepted():
    async def invalid_model(**kwargs):
        return {"results": [{"index": 0, "classification": "guessed_category", "confidence": .99,
                             "materiality_adjustment": 2, "reason": "bad output"}]}
    result = asyncio.run(ann.classify_unresolved([_item()], model_call=invalid_model))[0]
    assert result["classification"] == "unclassified"
    assert result["classification_method"] == "unclassified"
    assert result["materiality_score"] == 0
    assert result["summary"] is None


def test_model_failure_retains_unclassified_without_inventing_summary():
    async def unavailable(**kwargs):
        raise RuntimeError("model unavailable")
    result = asyncio.run(ann.classify_unresolved([_item("Novel event")], model_call=unavailable))[0]
    assert result["classification"] == "unclassified"
    assert result["materiality_score"] == 0
    assert result["summary"] is None


def test_high_confidence_routine_compliance_is_not_sent_to_model():
    calls = []
    async def unexpected(**kwargs):
        calls.append(kwargs)
        raise AssertionError("resolved routine compliance should not reach model")
    item = _item("Secretarial compliance certificate filed")
    result = asyncio.run(ann.classify_unresolved([item], model_call=unexpected))[0]
    assert not calls
    assert result["classification"] == "unclassified"
    assert result["classification_confidence"] == .98
    assert result["materiality_score"] == 1


def test_existing_llm_cache_avoids_repeating_model_http_call(tmp_path, monkeypatch):
    from app import llm

    db_path = str(tmp_path / "model-cache.db")
    init_db(db_path)
    monkeypatch.setenv("LLM_API_KEY", "offline-test-token")
    requests = []

    class FakeResponse:
        def raise_for_status(self):
            return None
        def json(self):
            return {"choices": [{"message": {"content": json.dumps({"results": [
                {"index": 0, "classification": "press_release", "confidence": .8,
                 "materiality_adjustment": 0, "reason": "general company update"}
            ]})}}], "usage": {"prompt_tokens": 10, "completion_tokens": 5}}

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return False
        async def post(self, *args, **kwargs):
            requests.append(kwargs)
            return FakeResponse()

    monkeypatch.setattr(llm.httpx, "AsyncClient", FakeAsyncClient)
    source = [_item("A novel corporate update")]
    first = asyncio.run(ann.classify_unresolved(source, db_path=db_path))
    second = asyncio.run(ann.classify_unresolved(source, db_path=db_path))
    assert first[0]["classification"] == second[0]["classification"] == "press_release"
    assert len(requests) == 1
    with connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM llm_cache").fetchone()[0] == 1


def test_list_filters_by_category_materiality_and_ticker(tmp_path):
    db_path = str(tmp_path / "filters.db")
    init_db(db_path)
    items = [
        ann.enrich_announcement(ann.normalize_announcement(_raw("Board declares dividend", NEWSID="1"), "INFY", "bse")),
        ann.enrich_announcement(ann.normalize_announcement(_raw("Board approves quarterly results", NEWSID="2"), "TCS", "nse")),
    ]
    ann.persist_announcements(items, db_path=db_path)
    assert len(ann.list_announcements(category="dividend", db_path=db_path)) == 1
    assert len(ann.list_announcements(ticker="TCS", min_materiality=8, db_path=db_path)) == 1
    assert ann.list_announcements(min_materiality=10, db_path=db_path) == []


def test_fastapi_announcement_refresh_and_filter_routes(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from app import main

    db_path = str(tmp_path / "api.db")
    monkeypatch.setattr(main, "DEMO_MODE", True)
    monkeypatch.setattr(main, "init_db", lambda: init_db(db_path))
    monkeypatch.setattr(main, "list_announcements", lambda **kwargs: ann.list_announcements(db_path=db_path, **kwargs))
    actual_ingest = ann.ingest_announcements

    async def ingest_for_test(ticker, **kwargs):
        return await actual_ingest(ticker, db_path=db_path, **kwargs)

    monkeypatch.setattr(main, "ingest_announcements", ingest_for_test)
    with TestClient(main.app) as client:
        response = client.post("/announcements/refresh", json={
            "ticker": "INFY", "from_date": "2026-10-01", "to_date": "2026-10-31",
        })
        assert response.status_code == 200
        body = response.json()
        assert body["demo_mode"] is True and body["source"] == "fixture"
        assert body["as_of"] == "2026-10-31T00:00:00Z"
        assert body["received"] >= 1
        assert "created_at" in body["announcements"][0]
        listed = client.get("/announcements", params={"ticker": "INFY", "category": "results"})
        assert listed.status_code == 200
        assert listed.json()["count"] >= 1
        assert listed.json()["as_of"] == "2026-10-31T00:00:00Z"
        assert all(x["classification"] == "results" for x in listed.json()["announcements"])
        high = client.get("/announcements/high-materiality", params={"min_materiality": 8})
        assert high.status_code == 200
        assert all(x["materiality_score"] >= 8 for x in high.json()["announcements"])
        invalid = client.get("/announcements", params={"category": "not-a-category"})
        assert invalid.status_code == 422

