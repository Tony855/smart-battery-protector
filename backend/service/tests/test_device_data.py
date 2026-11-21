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


def test_device_status_selects_latest_observed_sample(monkeypatch):
    import app.device_data as device_data

    class FakeCursor:
        def __init__(self):
            self.queries = []
            self.fetchone_calls = 0

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def execute(self, query, params):
            self.queries.append((query, params))

        def fetchone(self):
            self.fetchone_calls += 1
            if self.fetchone_calls == 1:
                return {"id": 7}
            return {"serial_number": "SBP-000001", "battery_voltage_v": 12.8}

    class FakeConnection:
        def __init__(self):
            self.db_cursor = FakeCursor()
            self.closed = False

        def cursor(self):
            return self.db_cursor

        def close(self):
            self.closed = True

    connection = FakeConnection()
    monkeypatch.setattr(device_data, "require_user_subject", lambda authorization: "user-1")
    monkeypatch.setattr(device_data, "database_connection", lambda: connection)

    result = device_data.get_device_status("SBP-000001", authorization="Bearer test")

    status_query = connection.db_cursor.queries[1][0]
    assert "ORDER BY t2.observed_at DESC, t2.id DESC" in status_query
    assert "MAX(t2.id)" not in status_query
    assert result["device"]["battery_voltage_v"] == 12.8
    assert connection.closed
