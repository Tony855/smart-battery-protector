# BLE telemetry protocol v1

Status: read-only monitoring interface. This document describes the firmware payload; it is not a commissioning or control protocol.

## GATT

- Device name: `SBP-CTRL`
- Service UUID: `9a701001-629b-4d83-9a2c-112233445566`
- Telemetry characteristic UUID: `9a701002-629b-4d83-9a2c-112233445566`
- Characteristic permissions: READ and NOTIFY only
- No BLE write characteristic is exposed for switching, configuration, fault clearing or commissioning.

## JSON payload

The characteristic returns a UTF-8 JSON object. Example:

```json
{
  "schema_version": 1,
  "sequence": 104,
  "battery_voltage_v": 12.641,
  "voltage_valid": true,
  "battery_current_a": null,
  "current_valid": false,
  "temperature_deci_c": 253,
  "temperature_valid": true,
  "engine_state": 1,
  "controller_state": 2,
  "system_voltage_class": 1,
  "protection_enabled": false
}
```

### Field definitions

| Field | Type | Meaning |
|---|---|---|
| schema_version | integer | Payload schema; currently 1 |
| sequence | unsigned integer | Increments once per published sample; wraps at 32 bits |
| battery_voltage_v | number or null | Battery bus voltage in volts |
| voltage_valid | boolean | Voltage measurement is currently valid |
| battery_current_a | number or null | Shunt current in amperes; null if shunt is unconfigured or read fails |
| current_valid | boolean | Current measurement is currently valid |
| temperature_deci_c | integer or null | Temperature in 0.1 °C units |
| temperature_valid | boolean | Temperature measurement is currently valid |
| engine_state | integer | 0 unknown, 1 off, 2 running |
| controller_state | integer | See state mapping below |
| system_voltage_class | integer | 0 unknown, 1 12V, 2 24V |
| protection_enabled | boolean | False in the current firmware; no physical switching is implemented |

A numeric sensor field MUST be treated as unusable when its corresponding `*_valid` flag is false, even if a client receives a stale cached value. A `null` numeric field is the expected representation for an invalid reading.

### Controller state mapping

| Value | State |
|---:|---|
| 0 | BOOT |
| 1 | SELF_TEST |
| 2 | MONITOR_ONLY |
| 3 | MONITOR |
| 4 | LOW_VOLTAGE_QUALIFY |
| 5 | DISCONNECTED (logical state only) |
| 6 | RECOVERY_QUALIFY |
| 7 | FAULT_LOCKED |

## Client behavior

- Check `schema_version` before decoding fields.
- Use `sequence` to detect missed notifications; wraparound is expected.
- Treat unknown enum values as unknown, not as a safe state.
- Display sensor validity separately from the numeric value.
- BLE disconnection must not change local controller behavior.
- This characteristic is intentionally unauthenticated read-only telemetry in this development build. Do not include secrets or personally identifying information.
- Do not infer that a displayed logical controller state means a physical contactor has switched.

## Current limitations

- Firmware protection remains disabled by default and the application currently forces `protection_enabled=false`.
- No authenticated commissioning, remote control, configuration write, fault-clear or OTA operation is exposed.
- BLE payload integration requires device-level validation with a real phone and HIL test evidence before release.
