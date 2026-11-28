from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
MQTT_CONTRACT = (REPOSITORY_ROOT / "protocol" / "MQTT_CONTRACT.md").read_text(
    encoding="utf-8"
)
API_CONTRACT = (REPOSITORY_ROOT / "protocol" / "API_CONTRACT.md").read_text(
    encoding="utf-8"
)


def test_mqtt_contract_declares_only_scoped_device_topics():
    expected_topics = {
        "sbp/v1/devices/{deviceId}/telemetry",
        "sbp/v1/devices/{deviceId}/events",
        "sbp/v1/devices/{deviceId}/commands",
        "sbp/v1/devices/{deviceId}/command-results",
        "sbp/v1/devices/{deviceId}/config",
    }
    declared_topics = {
        line.split("`")[1]
        for line in MQTT_CONTRACT.splitlines()
        if line.startswith("- `sbp/")
    }

    assert declared_topics == expected_topics


def test_mqtt_contract_requires_device_isolation_and_transport_security():
    required_rules = (
        "TLS transport and per-device credentials",
        "Broker ACL restricts each device to its own topics",
        "Expired, duplicate, unauthorized or schema-invalid commands are rejected",
        "Retained messages must never be used to replay power-control commands",
    )

    for rule in required_rules:
        assert rule in MQTT_CONTRACT


def test_mqtt_command_delivery_is_not_equivalent_to_actuation():
    assert "Cloud delivery means only that a request was transported" in MQTT_CONTRACT
    assert "Device-local safety gate is authoritative" in MQTT_CONTRACT
    assert "Telemetry and events are observational" in API_CONTRACT
    assert "MQTT broker/client integration are not exposed" in API_CONTRACT


def test_mqtt_telemetry_units_match_system_contract():
    required_units = (
        "battery_voltage_v: volts (V)",
        "battery_current_a: amperes (A)",
        "temperature_deci_c: integer units of 0.1°C",
        "system_voltage_class: 12, 24, or null",
    )

    for unit in required_units:
        assert unit in MQTT_CONTRACT
