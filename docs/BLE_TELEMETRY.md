# BLE telemetry protocol v1

Status: read-only monitoring interface. This is not a commissioning or control protocol.

## GATT

- Device name: `SBP-CTRL`
- Service UUID: `9a701001-629b-4d83-9a2c-112233445566`
- Telemetry characteristic UUID: `9a701002-629b-4d83-9a2c-112233445566`
- Telemetry characteristic permissions: READ and NOTIFY only
- Diagnostics characteristic UUID: `9a701003-629b-4d83-9a2c-112233445566`
- Diagnostics characteristic permissions: READ only (no NOTIFY and no WRITE)
- Preferred ATT MTU: 128 bytes
- No BLE write characteristic exists for switching, configuration, fault clearing or commissioning.

## Telemetry JSON payload

The characteristic returns a compact UTF-8 JSON object. Compact keys keep the notification payload small enough for a 128-byte ATT MTU.

```json
{
  "v": 1,
  "n": 104,
  "bv": 12.641,
  "vv": true,
  "ba": null,
  "av": false,
  "tc": 253,
  "tv": true,
  "e": 1,
  "s": 2,
  "vc": 12,
  "pe": false
}
```

| Key | Type | Meaning |
|---|---|---|
| v | integer | Schema version; currently 1 |
| n | unsigned integer | Sequence increments per sample and wraps at 32 bits |
| bv | number or null | Battery voltage in volts |
| vv | boolean | Voltage measurement validity |
| ba | number or null | Shunt current in amperes; null if shunt is unconfigured or read fails |
| av | boolean | Current measurement validity |
| tc | integer or null | Temperature in 0.1°C units |
| tv | boolean | Temperature measurement validity |
| e | integer | Engine: 0 unknown, 1 off, 2 running |
| s | integer | Controller state (see below) |
| vc | integer | Voltage class: 0 UNKNOWN, 12 12V, 24 24V |
| pe | boolean | Protection enabled; false in current engineering firmware |

A numeric sensor field MUST be treated as unusable when its corresponding validity flag is false, even if a client receives a cached value. A `null` numeric field is the expected representation for an invalid reading. TMP117 values outside -55.0°C to +150.0°C are invalid. INA228 signed VSHUNT rail codes (0x7FFFF and 0x80000) are treated as saturated/invalid current readings; the firmware does not publish a clipped rail value as valid.

### Controller state mapping (`s`)

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

## Boot diagnostics characteristic

The same GATT service exposes a separate boot-diagnostics characteristic:
- UUID: `9a701003-629b-4d83-9a2c-112233445566`
- Permissions: READ only (no NOTIFY and no WRITE)
- Payload schema: diagnostics schema version 1
- Read it after connecting to inspect the most recent boot. The payload is assembled once during startup; it is not a live event stream.

Example:

```json
{
  "v": 1,
  "rr": 9,
  "nv": 2,
  "sn": 1,
  "mo": 0,
  "rf": 27,
  "cg": 42
}
```

| Key | Meaning |
|---|---|
| v | Diagnostics schema version; currently 1 |
| rr | Reset reason: 0 unknown, 1 power-on, 2 external, 3 software, 4 panic, 5 interrupt watchdog, 6 task watchdog, 7 other watchdog, 8 deep sleep, 9 brownout, 10 SDIO, 11 other |
| nv | NVS state: 0 unknown, 1 no record, 2 valid record found but not applied, 3 corrupt/conflicting record, 4 NVS initialization/read error |
| sn | Sensor initialization: 0 unknown, 1 ready, 2 generic initialization failure, 3 I2C bus failure, 4 INA228 unavailable/identity mismatch, 5 TMP117 unavailable/identity mismatch, 6 INA228 ADC configuration write/read-back failure. This does not guarantee every later sample is valid; use telemetry validity flags for live samples |
| mo | Operating mode: 0 monitor-only |
| rf | Reason bitmask: bit 0 protection forced off; bit 1 stored configuration deliberately not applied; bit 2 sensor initialization failed; bit 3 shunt not configured; bit 4 physical actuator driver not implemented |
| cg | Stored configuration generation; meaningful only when `nv` is 2. A value of 0 with another NVS state means no valid generation was loaded. A valid record is still not active |

Clients MUST treat unknown codes as unknown and MUST NOT infer that a valid NVS record is active. The diagnostics characteristic contains no secrets, credentials or personal data. It is unauthenticated read-only engineering telemetry and is not a control or commissioning interface.

## Client behavior

- Check `v` before decoding fields.
- Use `n` to detect missed notifications; wraparound is expected.
- Treat unknown enum values as unknown, not as a safe state.
- Display sensor validity separately from the numeric value.
- Negotiate an ATT MTU of at least 128 bytes where supported; clients with a smaller MTU may use characteristic reads and must not assume every notification can be delivered.
- BLE disconnection must not change local controller behavior.
- This development characteristic is unauthenticated read-only telemetry. Do not include secrets or personally identifying information.
- Do not infer that a displayed logical controller state means a physical contactor has switched.

## Security and safety boundary

- Live telemetry is not encrypted at the application layer and may be visible to nearby BLE scanners; do not include secrets, claim codes or personal identifiers.
- Any future control/configuration characteristic must require authenticated encrypted pairing, authorization, anti-replay, expiry, idempotency and the same local firmware safety gate.
- Phone/cloud control must never override engine-state interlocks or hardware fault lockout.

## Current limitations

- Firmware protection remains disabled by default and the application currently forces protection off.
- No authenticated commissioning, remote control, configuration write, fault-clear or OTA operation is exposed.
- Phone interoperability and notification delivery require device-level validation with HIL evidence before release.
