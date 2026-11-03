from fastapi.testclient import TestClient
from app.main import app
from app.db import init_db, connect
from app.fundamentals import load_fundamentals_fixture
from app.promised_vs_delivered import load_commitments_fixture


def test_health_endpoint_reports_database_and_metadata():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "finn-api"
        assert data["database_connected"] is True
        assert data["tables_count"] >= 9
        assert "timestamp" in data
        assert data["version"] == "1.0.0"


def test_cors_headers_present_on_cross_origin_request():
    with TestClient(app) as client:
        response = client.options(
            "/digest",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers


def test_idempotent_init_db_and_fixture_loads(tmp_path):
    test_db = str(tmp_path / "prod_test.db")
    init_db(test_db)
    # Re-initialization should be safe and idempotent
    init_db(test_db)

    with connect(test_db) as conn:
        tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        assert "companies" in tables
        assert "company_fundamentals" in tables
        assert "company_commitments" in tables
        assert "ask_messages" in tables
        assert "prices" in tables
        assert "announcements" in tables
