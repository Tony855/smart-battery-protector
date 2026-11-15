import pytest
from pydantic import ValidationError

from app.telemetry import TelemetrySample


def valid_sample(**overrides):
    payload = {
        "sample_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "observed_at": "2026-11-15T12:00:00Z",
        "battery_voltage_mv": 12800,
        "battery_current_ma": -1200,
        "temperature_centi_c": 2534,
        "state_code": "normal",
        "engine_running": "unknown",
    }
    payload.update(overrides)
    return payload


def test_telemetry_sample_accepts_valid_snapshot():
    sample = TelemetrySample.model_validate(valid_sample())
    assert sample.battery_voltage_mv == 12800
    assert sample.observed_at.tzinfo is not None


@pytest.mark.parametrize("overrides", [
    {"battery_voltage_mv": 60001},
    {"battery_current_ma": 1000001},
    {"temperature_centi_c": 20001},
    {"state_code": "switch_power_now"},
    {"engine_running": "maybe"},
    {"unexpected": "field"},
])
def test_telemetry_sample_rejects_out_of_range_or_unknown_fields(overrides):
    with pytest.raises(ValidationError):
        TelemetrySample.model_validate(valid_sample(**overrides))


def test_telemetry_timestamp_requires_timezone_at_route_boundary():
    sample = TelemetrySample.model_validate(valid_sample(observed_at="2026-11-15T12:00:00"))
    assert sample.observed_at.tzinfo is None
