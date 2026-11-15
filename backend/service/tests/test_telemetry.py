import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.telemetry import TelemetrySample


def valid_sample(**overrides):
    payload = {
        "sample_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "observed_at": "2026-11-15T12:00:00Z",
        "battery_voltage_v": 12.800,
        "battery_current_a": -1.200,
        "temperature_c": 25.3,
        "state_code": "normal",
        "engine_running": "unknown",
    }
    payload.update(overrides)
    return payload


def test_telemetry_sample_accepts_new_engineering_units():
    sample = TelemetrySample.model_validate(valid_sample())
    assert sample.battery_voltage_v == Decimal("12.8")
    assert sample.battery_current_a == Decimal("-1.2")
    assert sample.temperature_c == Decimal("25.3")
    assert sample.observed_at.tzinfo is not None


@pytest.mark.parametrize("overrides", [
    {"battery_voltage_v": 60.001},
    {"battery_current_a": 1000.001},
    {"temperature_c": 200.1},
    {"temperature_c": 25.34},
    {"state_code": "switch_power_now"},
    {"engine_running": "maybe"},
    {"unexpected": "field"},
])
def test_telemetry_sample_rejects_out_of_range_precision_or_unknown_fields(overrides):
    with pytest.raises(ValidationError):
        TelemetrySample.model_validate(valid_sample(**overrides))


def test_telemetry_timestamp_requires_timezone_at_route_boundary():
    sample = TelemetrySample.model_validate(valid_sample(observed_at="2026-11-15T12:00:00"))
    assert sample.observed_at.tzinfo is None
