from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_liveness_is_available():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "sbp-api"

def test_readiness_fails_closed_until_dependencies_exist():
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["detail"] == "dependencies_not_configured"
