import asyncio
import sys
import types

import pytest

from app import results_card as rc
from app.db import init_db, connect


def model_data(*, wrong=False):
    values = {"revenue_from_operations": "1,000", "other_income": "20", "total_expenses": "800",
              "finance_costs": "10", "depreciation": "30", "profit_before_tax": "200",
              "tax_expense": "50", "profit_after_tax": "150"}
    periods = {
        "current": {"period_label": "Quarter ended 30 September 2026", "unit_as_printed": "₹ crore", "values": values, "ebitda": None},
        "preceding_quarter": {"period_label": "Quarter ended 30 June 2026", "unit_as_printed": "₹ crore", "values": values, "ebitda": None},
        "corresponding_previous_year": {"period_label": "Quarter ended 30 September 2025", "unit_as_printed": "₹ crore", "values": values, "ebitda": None},
    }
    citations = []
    for role, period in periods.items():
        for field, value in period["values"].items():
            citations.append({"field": field, "period_role": role, "page": 2,
                              "quote": f"{field} {value}"})
    pages = [{"page": 2, "text": "Total Income Revenue from operations Profit before tax Finance costs Depreciation\n" + " ".join(x["quote"] for x in citations), "tables": []}]
    if wrong:
        periods["current"]["values"]["profit_after_tax"] = "250"
    return {"reporting_basis": "consolidated", "periods": periods, "citations": citations, "confidence": .95}, pages


@pytest.mark.parametrize("unit,factor", [("₹ crore", 1), ("INR lakhs", .01), ("INR million", .1), ("INR", 1e-7)])
def test_unit_normalization(unit, factor):
    assert rc.unit_factor(unit) == factor


def test_amount_and_missing_values():
    assert rc.amount("(1,234.5)") == -1234.5
    assert rc.amount("-") is None
    assert rc.amount(None) is None


def test_relevant_page_identification():
    pages = [
        {"page": 1, "text": "Auditor report"},
        {"page": 3, "text": "Revenue from operations and Profit before tax"},
        {"page": 4, "text": "", "tables": [["Revenue from operations", "Profit before tax", "Depreciation"]]},
    ]
    assert [p["page"] for p in rc.relevant_pages(pages)] == [3, 4]


def test_pdf_page_text_and_table_extraction(monkeypatch, tmp_path):
    class Page:
        def get_text(self, _): return "Revenue from operations; Profit before tax"
    class Doc(list):
        def close(self): pass
    class Plumber:
        pages = [types.SimpleNamespace(extract_tables=lambda: [[['Revenue', '100']]])]
        def __enter__(self): return self
        def __exit__(self, *_): pass
    monkeypatch.setitem(sys.modules, "fitz", types.SimpleNamespace(open=lambda _: Doc([Page()])))
    monkeypatch.setitem(sys.modules, "pdfplumber", types.SimpleNamespace(open=lambda _: Plumber()))
    assert rc.extract_pdf(tmp_path / "some.pdf") == [{"page": 1, "text": "Revenue from operations; Profit before tax", "tables": [[['Revenue', '100']]]}]


def test_financial_calculations_and_ebitda_derivation():
    extracted, pages = model_data()
    obj = rc.Extraction.model_validate(extracted)
    citations = {(c.period_role, c.field): c.model_dump() for c in obj.citations}
    assert rc.validate_extraction(obj, pages) == []
    calc = rc._period_payload(obj, citations)
    current = calc["periods"]["current"]
    assert current["ebitda"]["value_inr_crore"] == 220
    assert current["ebitda"]["derived"] is True
    assert calc["changes"]["revenue_from_operations"] == {"qoq_pct": 0, "yoy_pct": 0}
    assert rc.margin(150, 1000) == 15
    assert rc.percent_change(100, 0) is None
    assert rc.margin(1, 0) is None


def test_reported_ebitda_not_marked_derived():
    data, _ = model_data()
    data["periods"]["current"]["ebitda"] = "230"
    data["citations"].append({"field": "ebitda", "period_role": "current", "page": 2, "quote": "EBITDA 230"})
    obj = rc.Extraction.model_validate(data)
    cit = {(c.period_role, c.field): c.model_dump() for c in obj.citations}
    assert rc._period_payload(obj, cit)["periods"]["current"]["ebitda"]["derived"] is False


def test_consolidated_selection_field():
    data, pages = model_data()
    assert rc.validate_extraction(rc.Extraction.model_validate(data), pages) == []
    data["reporting_basis"] = "standalone"
    assert rc.Extraction.model_validate(data).reporting_basis == "standalone"


def test_validation_rejects_bad_pat_and_uncited_value():
    data, pages = model_data(wrong=True)
    obj = rc.Extraction.model_validate(data)
    assert any("PAT exceeds" in e for e in rc.validate_extraction(obj, pages))
    data, pages = model_data()
    data["citations"] = [c for c in data["citations"] if not (c["period_role"] == "current" and c["field"] == "profit_after_tax")]
    assert any("Missing source citation" in e for e in rc.validate_extraction(rc.Extraction.model_validate(data), pages))


def test_validation_requires_matching_year_ago_quarter():
    data, pages = model_data()
    data["periods"]["corresponding_previous_year"]["period_label"] = "Quarter ended 30 June 2025"
    errors = rc.validate_extraction(rc.Extraction.model_validate(data), pages)
    assert any("twelve months" in error for error in errors)


def test_missing_values_are_null_and_ebitda_not_derived():
    data, _ = model_data()
    for p in data["periods"].values():
        p["values"]["other_income"] = None
    obj = rc.Extraction.model_validate(data)
    cit = {(c.period_role, c.field): c.model_dump() for c in obj.citations if c.field != "other_income"}
    calc = rc._period_payload(obj, cit)
    assert calc["periods"]["current"]["other_income"]["value_inr_crore"] is None
    assert calc["periods"]["current"]["ebitda"]["value_inr_crore"] is None


def test_invalid_url_and_unavailable_download(monkeypatch, tmp_path):
    with pytest.raises(ValueError): rc.download_pdf("file:///private.pdf", cache_dir=tmp_path)
    class Fail:
        def __init__(self, *a, **k): pass
        def raise_for_status(self): raise rc.httpx.ConnectError("offline")
    monkeypatch.setattr(rc.httpx, "get", lambda *a, **k: Fail())
    with pytest.raises(rc.ResultExtractionError, match="download failed"):
        rc.download_pdf("https://example.com/results.pdf", cache_dir=tmp_path, retries=0)


def test_pdf_cache_avoids_second_download(monkeypatch, tmp_path):
    calls = []
    class Response:
        content = b"%PDF-1.7 test"
        def raise_for_status(self): pass
    monkeypatch.setattr(rc.httpx, "get", lambda *a, **k: calls.append(a[0]) or Response())
    first = rc.download_pdf("https://example.com/a.pdf", cache_dir=tmp_path)
    second = rc.download_pdf("https://example.com/a.pdf", cache_dir=tmp_path)
    assert first == second
    assert calls == ["https://example.com/a.pdf"]


def test_strong_model_retry_then_parse_failed(monkeypatch, tmp_path):
    extracted, pages = model_data(wrong=True)
    calls = []
    async def model_call(**kwargs):
        calls.append(kwargs["tier"])
        return extracted
    monkeypatch.setattr(rc, "download_pdf", lambda *a, **k: (tmp_path / "file.pdf", "hash"))
    monkeypatch.setattr(rc, "extract_pdf", lambda *a, **k: pages)
    (tmp_path / "file.pdf").write_bytes(b"%PDF-test")
    result = asyncio.run(rc.generate_results_card(ticker="ABC", company_name="A", filing_id="x", source_url="https://e.test/a.pdf", cache_dir=tmp_path, model_call=model_call))
    assert calls == ["small", "strong"]
    assert result["parse_failed"] is True
    assert result["source_url"] == "https://e.test/a.pdf"


def test_success_card_and_existing_extractions_persistence(monkeypatch, tmp_path):
    db = tmp_path / "test.db"
    init_db(str(db))
    with connect(str(db)) as conn:
        conn.execute("INSERT INTO companies(ticker,name) VALUES('ABC','Alpha')")
        conn.execute("INSERT INTO filings(id,ticker,exchange,filed_at,category,headline,raw_url,attachment_url,source) VALUES('f1','ABC','NSE','2026-10-01','results','Quarter results','https://e.test','https://e.test/a.pdf','test')")
    extracted, pages = model_data()
    calls = []
    async def model_call(**kwargs):
        calls.append(kwargs["tier"])
        if kwargs["schema"] is rc.Observations: return {"lines": ["Revenue was 1,000 crore.", "PAT was 150 crore."]}
        return extracted
    monkeypatch.setattr(rc, "download_pdf", lambda *a, **k: (tmp_path / "file.pdf", "abc123"))
    monkeypatch.setattr(rc, "extract_pdf", lambda *a, **k: pages)
    (tmp_path / "file.pdf").write_bytes(b"%PDF-test")
    result = asyncio.run(rc.generate_results_card(ticker="ABC", company_name="Alpha", filing_id="f1", source_url="https://e.test/a.pdf", cache_dir=tmp_path, db_path=str(db), model_call=model_call))
    assert not result["parse_failed"]
    assert result["periods"]["current"]["ebitda"]["derived"]
    assert len(result["source_citations"]) == 24
    assert rc.get_cached_card("f1", db_path=str(db))["ticker"] == "ABC"
