from fastapi.testclient import TestClient
from app.main import app
import app.main as main_module

client = TestClient(app)

def test_liveness_is_available():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "sbp-api"

def test_readiness_fails_closed_when_database_is_unavailable(monkeypatch):
    monkeypatch.setattr(main_module, "ping_database", lambda: False)
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["detail"] == "database_not_ready"

def test_readiness_succeeds_when_database_probe_succeeds(monkeypatch):
    monkeypatch.setattr(main_module, "ping_database", lambda: True)
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
