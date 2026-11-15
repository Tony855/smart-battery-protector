from fastapi.testclient import TestClient

from app.main import app


def test_device_status_requires_authentication():
    response = TestClient(app).get("/api/v1/me/devices/SBP-000001/status")
    assert response.status_code == 401


def test_device_events_requires_authentication():
    response = TestClient(app).get("/api/v1/me/devices/SBP-000001/events")
    assert response.status_code == 401


def test_device_events_rejects_invalid_pagination():
    client = TestClient(app)
    response = client.get(
        "/api/v1/me/devices/SBP-000001/events?limit=201",
        headers={"Authorization": "Bearer invalid"},
    )
    # Query validation occurs before route authentication.
    assert response.status_code == 422
