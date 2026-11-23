# BLE GATT Protocol v0.3 — ESP32-C6 monitor service

## Implemented read-only service
Telemetry and boot diagnostics only. No BLE write/control characteristics; relay/contactor switching, configuration writes and OTA are not exposed.

| Item | UUID bytes in BLE wire order | Properties |
|---|---|---|
| SBP telemetry service | 9A 70 10 01 62 9B 4D 83 9A 2C 11 22 33 44 55 66 | Primary service |
| LiveTelemetry | 9A 70 10 02 62 9B 4D 83 9A 2C 11 22 33 44 55 66 | Read, Notify |
| BootDiagnostics | 9A 70 10 03 62 9B 4D 83 9A 2C 11 22 33 44 55 66 | Read |

Advertising name: SBP-CTRL. It is fixed and not a unique device identity.

## LiveTelemetry payload v1
The wire keys are abbreviated; values are observational, not commands.

| Key | Meaning | Unit / values |
|---|---|---|
| v | schema version | integer 1 |
| n | telemetry sequence | unsigned; wraps modulo 32-bit |
| bv | battery voltage | V, decimal; vv indicates validity |
| vv | voltage validity | boolean |
| ba | battery current | A, signed decimal; av indicates validity |
| av | current validity | boolean |
| tc | temperature | integer 0.1°C; tv indicates validity |
| tv | temperature validity | boolean |
| e | engine state | 0 UNKNOWN, 1 OFF, 2 RUNNING |
| s | controller state | numeric sbp_state_t value |
| vc | system voltage class | 0 UNKNOWN, 12 or 24 |
| pe | protection enabled | boolean; always false in the current monitor-only application |

Invalid/unconfigured sensor values are JSON null. Null is not zero and is not proof of safe physical measurement.

## BootDiagnostics payload v1
| Key | Meaning |
|---|---|
| v | schema version (1) |
| rr | reset reason: 0 unknown, 1 power-on, 2 external, 3 software, 4 panic, 5 interrupt watchdog, 6 task watchdog, 7 other watchdog, 8 deep sleep, 9 brownout, 10 SDIO, 11 other |
| nv | NVS state: 0 unknown, 1 missing, 2 valid-but-not-applied, 3 invalid, 4 error |
| sn | sensor state: 0 unknown, 1 ready, 2 init failed, 3 bus failed, 4 INA228 failed, 5 TMP117 failed, 6 INA228 configuration failed |
| mo | mode; currently 0 MONITOR_ONLY |
| rf | reason bitmask: bit 0 protection forced off; bit 1 configuration not applied; bit 2 sensor initialization failed; bit 3 shunt unconfigured; bit 4 actuator not implemented |
| cg | stored config generation; validated but not applied |

Initial diagnostics before boot publication use flags 19 (bits 0, 1 and 4).

## Security and safety boundary
- Telemetry and diagnostics are READ/NOTIFY only; no GATT write characteristic exists.
- BLE link/application payloads are not encrypted or authenticated in this build. Nearby clients may read data. The fixed name does not identify a unique device. Do not include secrets, claim codes or personal identifiers.
- This unsecured read-only service is development telemetry and must be replaced or secured before commercial deployment.
- Future control/configuration characteristics require authenticated encrypted pairing, authorization, anti-replay, expiry, idempotency and the same local firmware safety gate.
- Disconnect must not change local protection state. Phone/cloud control must never override engine-state interlocks or hardware fault lockout.

## Planned
DeviceInfo, authenticated configuration, manual command request/result, fault-log pagination, OTA manifest and signed OTA flow remain unimplemented. Do not build mobile dependencies until UUIDs, security, semantics and versioning are frozen.
