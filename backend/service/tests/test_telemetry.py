import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.telemetry import TelemetrySample, get_device_telemetry


def valid_sample(**overrides):
    payload = {
        "sample_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "observed_at": "2026-11-15T12:00:00Z",
        "battery_voltage_v": 12.800,
        "battery_current_a": -1.200,
        "temperature_deci_c": 253,
        "state_code": "normal",
        "engine_running": "unknown",
        "system_voltage_class": 12,
    }
    payload.update(overrides)
    return payload


def test_telemetry_sample_accepts_requested_engineering_units():
    sample = TelemetrySample.model_validate(valid_sample())
    assert sample.battery_voltage_v == Decimal("12.8")
    assert sample.battery_current_a == Decimal("-1.2")
    assert sample.temperature_deci_c == 253
    assert sample.system_voltage_class == 12
    assert sample.observed_at.tzinfo is not None


def test_telemetry_temperature_matches_tmp117_measurement_envelope():
    assert TelemetrySample.model_validate(valid_sample(temperature_deci_c=-550)).temperature_deci_c == -550
    assert TelemetrySample.model_validate(valid_sample(temperature_deci_c=1500)).temperature_deci_c == 1500


@pytest.mark.parametrize("overrides", [
    {"battery_voltage_v": 60.001},
    {"battery_current_a": 1000.001},
    {"temperature_deci_c": 1501},
    {"temperature_deci_c": -551},
    {"temperature_deci_c": 253.1},
    {"state_code": "switch_power_now"},
    {"engine_running": "maybe"},
    {"system_voltage_class": 18},
    {"unexpected": "field"},
])
def test_telemetry_sample_rejects_out_of_range_precision_or_unknown_fields(overrides):
    with pytest.raises(ValidationError):
        TelemetrySample.model_validate(valid_sample(**overrides))


def test_telemetry_timestamp_requires_timezone_at_route_boundary():
    sample = TelemetrySample.model_validate(valid_sample(observed_at="2026-11-15T12:00:00"))
    assert sample.observed_at.tzinfo is None


def test_telemetry_history_reuses_active_user_authorization(monkeypatch):
    import app.telemetry as telemetry

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
            return {"id": 9}

        def fetchall(self):
            return [{"battery_voltage_v": Decimal("12.8")}]

    class FakeConnection:
        def __init__(self):
            self.db_cursor = FakeCursor()
            self.closed = False

        def cursor(self):
            return self.db_cursor

        def close(self):
            self.closed = True

    connection = FakeConnection()
    monkeypatch.setattr(telemetry, "require_user_subject", lambda authorization: "locked-subject")
    monkeypatch.setattr(telemetry, "database_connection", lambda: connection)

    result = get_device_telemetry(
        "SBP-000001", authorization="Bearer test", limit=25
    )

    authorization_query, authorization_params = connection.db_cursor.queries[0]
    telemetry_query, telemetry_params = connection.db_cursor.queries[1]
    assert "u.status='active'" in authorization_query
    assert authorization_params == ("SBP-000001", "locked-subject")
    assert "WHERE device_id=%s" in telemetry_query
    assert telemetry_params == (9, 25)
    assert result["samples"] == [{"battery_voltage_v": Decimal("12.8")}]
    assert connection.closed
