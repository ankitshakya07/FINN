import sys
import json
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("--- 1. GET /portfolio (RELIANCE) ---")
p_resp = client.get("/portfolio").json()
rel_comp = next((c for c in p_resp.get("companies", []) if c["ticker"] == "RELIANCE"), None)
print(json.dumps({
    "as_of": p_resp.get("as_of"),
    "demo_mode": p_resp.get("demo_mode"),
    "data_source": p_resp.get("data_source"),
    "company": rel_comp
}, indent=2))

print("\n--- 2. GET /digest (status block) ---")
d_resp = client.get("/digest?window=24h").json()
print(json.dumps({
    "window": d_resp.get("window"),
    "status": d_resp.get("status"),
    "last_refresh": d_resp.get("last_refresh"),
    "items_count": len(d_resp.get("items", [])),
    "total_count": d_resp.get("total_count"),
    "demo_mode": d_resp.get("demo_mode")
}, indent=2))

print("\n--- 3. GET /alerts ---")
a_resp = client.get("/alerts").json()
print(json.dumps({
    "as_of": a_resp.get("as_of"),
    "demo_mode": a_resp.get("demo_mode"),
    "alerts_count": len(a_resp.get("alerts", [])),
    "sample_alert": a_resp.get("alerts", [])[0] if a_resp.get("alerts") else None
}, indent=2))

print("\n--- 4. GET /health ---")
h_resp = client.get("/health").json()
print(json.dumps(h_resp, indent=2))

