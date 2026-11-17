# BLE GATT Protocol v0.2 — ESP32-C6 monitor service

## Implemented read-only service
The first ESP32-C6 firmware increment exposes a read-only live telemetry characteristic. No BLE characteristic can switch a relay/contactor, change protection thresholds, or trigger OTA.

| Item | UUID bytes in BLE wire order | Properties |
|---|---|---|
| SBP telemetry service | 9A 70 10 01 62 9B 4D 83 9A 2C 11 22 33 44 55 66 | Primary service |
| LiveTelemetry | 9A 70 10 02 62 9B 4D 83 9A 2C 11 22 33 44 55 66 | Read, Notify |

Device advertising name: `SBP-CTRL`.

### LiveTelemetry payload
UTF-8 JSON. Numeric fields use the system-wide unit contract:
- `battery_voltage_v`: volts (V), decimal.
- `battery_current_a`: amperes (A), signed decimal.
- `temperature_deci_c`: integer units of 0.1°C; 253 means 25.3°C.
- `engine_state`: 0 UNKNOWN, 1 OFF, 2 RUNNING.
- `controller_state`: numeric `sbp_state_t` value from firmware.\n- `system_voltage_class`: 0 UNKNOWN, 12 for 12V, 24 for 24V; once classified at boot it stays locked until restart.

Example:
```json
{"battery_voltage_v":12.345,"battery_current_a":-1.234,"temperature_deci_c":253,"engine_state":1,"controller_state":3}
```

A field is JSON `null` if its sensor value is invalid or not commissioned. Do not interpret `null` as zero.

## Security and safety boundary
- This initial service is telemetry-only and read-only. It intentionally exposes no command/write characteristic.
- Live telemetry is not encrypted at the application layer and may be visible to nearby BLE scanners; do not include secrets, claim codes or personal identifiers.
- Any future control/configuration characteristic must require authenticated encrypted pairing, authorization, anti-replay, expiry, idempotency and the same local firmware safety gate.
- BLE disconnect must not change the local protection state.
- Phone/cloud control must never override engine-state interlocks or hardware fault lockout.

## Planned, not yet implemented
DeviceInfo, authenticated configuration, manual command request/result, fault-log pagination, OTA manifest and signed OTA flow remain future increments. Do not build mobile app dependencies against these planned characteristics until their UUIDs and versioning are frozen.
