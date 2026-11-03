import json
import sqlite3

from fastapi.testclient import TestClient

from app.db import init_db
from app.main import app
from app.management_changes import _extract, list_management_changes, process_management_changes


def announcement(headline, metadata=None, score=4):
    return {"headline": headline, "raw_metadata": metadata or {}, "materiality_score": score}


def test_appointment_and_role_classification():
    event = _extract(announcement("Mr. Rohan Mehta appointed as Chief Financial Officer effective 2026-08-01"))
    assert event["person_name"] == "Mr. Rohan Mehta"
    assert event["role_category"] == "cfo"
    assert event["change_type"] == "appointment"
    assert event["effective_date"] == "2026-08-01"
    assert event["materiality_score"] == 7


def test_resignation_and_explicit_reason_only():
    event = _extract(announcement("Ms. Anita Rao resigns as Independent Director due to personal reasons with effect from 31/07/2026"))
    assert event["change_type"] == "resignation"
    assert event["role_category"] == "independent_director"
    assert event["reason"] == "personal reasons with effect from 31/07/2026"
    assert event["effective_date"] == "2026-07-31"


def test_board_change_retirement_and_reappointment():
    assert _extract(announcement("Dr. Kiran Shah appointed to the Board as Director"))["role_category"] == "director"
    assert _extract(announcement("Mr. Kiran Shah retires as Chairman on 30 Sep 2026"))["change_type"] == "retirement"
    assert _extract(announcement("Mr. Kiran Shah re-appointed as Managing Director"))["change_type"] == "reappointment"


def test_missing_names_and_ambiguous_names_are_safe():
    missing = _extract(announcement("Appointment of Chief Executive Officer effective 2026-05-01"))
    assert missing["person_name"] is None
    assert missing["extraction_status"] == "incomplete"
    ambiguous = _extract(announcement("Mr. A Kumar and Ms. B Nair appointed as Directors"))
    assert ambiguous["person_name"] is None
    assert ambiguous["extraction_status"] == "ambiguous"


def test_invalid_or_absent_date_is_null():
    assert _extract(announcement("Mr. A Kumar appointed as CFO effective 31/02/2026"))["effective_date"] is None
    assert _extract(announcement("Ms. A Nair appointed as CFO"))["effective_date"] is None


def test_reason_is_not_inferred():
    event = _extract(announcement("Mr. A Kumar resigns as CFO"))
    assert event["reason"] is None


def _seed(path, headline):
    init_db(str(path))
    with sqlite3.connect(path) as conn:
        conn.execute("INSERT INTO companies(ticker,name) VALUES('INFY','Infosys Limited')")
        conn.execute("""INSERT INTO announcements
            (id,ticker,timestamp,headline,source,raw_metadata_json,fingerprint,cross_source_fingerprint,classification,materiality_score)
            VALUES ('ann-1','INFY','2026-10-20T12:00:00Z',?,'fixture',?,'fingerprint-1','cross-1','management_change',5)""",
                     (headline, json.dumps({"details": "Board filing"})))


def test_duplicate_processing_is_idempotent(tmp_path):
    db = tmp_path / "mgmt.db"
    _seed(db, "Mr. A Kumar appointed as Chief Financial Officer")
    assert process_management_changes(db_path=str(db)) == {"scanned": 1, "inserted": 1}
    assert process_management_changes(db_path=str(db)) == {"scanned": 1, "inserted": 0}
    assert len(list_management_changes(db_path=str(db))) == 1
    assert len(list_management_changes(ticker="INFY", change_type="appointment", min_materiality=5, db_path=str(db))) == 1
    assert list_management_changes(ticker="TCS", db_path=str(db)) == []


def test_empty_list_and_api_response(tmp_path, monkeypatch):
    from app import main
    monkeypatch.setattr(main, "list_management_changes", lambda **kwargs: [])
    with TestClient(app) as client:
        response = client.get("/management-changes")
        assert response.status_code == 200
        assert response.json()["count"] == 0
        assert response.json()["events"] == []


def test_materiality_clamped_to_ten():
    event = _extract(announcement("Mr. A Kumar appointed CEO", score=20))
    assert event["materiality_score"] == 10
