# BLE telemetry protocol v1

Status: read-only monitoring interface. This is not a commissioning or control protocol.

## GATT
- Device name: `SBP-CTRL`
- Service UUID: `9a701001-629b-4d83-9a2c-112233445566`
- Telemetry characteristic UUID: `9a701002-629b-4d83-9a2c-112233445566`
- Diagnostics characteristic UUID: `9a701003-629b-4d83-9a2c-112233445566`
- Telemetry permissions: READ and NOTIFY only
- Diagnostics permissions: READ only
- Preferred ATT MTU: 128 bytes
- No BLE write characteristic exists for switching, configuration, fault clearing or commissioning.

## JSON payload
The telemetry characteristic returns a compact UTF-8 JSON object. Compact keys keep the notification payload small enough for the configured 128-byte ATT MTU.

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
  "vc": 1,
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
| vc | integer | Voltage class: 0 unknown, 1 12V, 2 24V |
| pe | boolean | Protection enabled; false in current engineering firmware |

A numeric sensor field MUST be treated as unusable when its corresponding validity flag is false. TMP117 values outside -55.0°C to +150.0°C are invalid. INA228 signed VSHUNT rail codes (0x7FFFF and 0x80000) are treated as saturated/invalid current readings; the firmware does not publish a clipped rail value as valid.

## Boot diagnostics
The separate diagnostics characteristic returns schema v1 boot/reset reason, NVS state, sensor initialization category, monitor-only mode, reason flags and validated configuration generation. It is READ only. The structured serial record uses the `BOOT_DIAG` prefix.

## Security and safety boundary
- This initial service is telemetry-only and read-only. It intentionally exposes no command/write characteristic.
- Live telemetry is not encrypted at the application layer and may be visible to nearby BLE scanners; do not include secrets, claim codes or personal identifiers.
- Any future control/configuration characteristic must require authenticated encrypted pairing, authorization, anti-replay, expiry, idempotency and the same local firmware safety gate.
- BLE disconnect must not change the local protection state.
- Phone/cloud control must never override engine-state interlocks or hardware fault lockout.

## Planned, not yet implemented
DeviceInfo, authenticated configuration, manual command request/result, fault-log pagination, OTA manifest and signed OTA flow remain future increments. Do not build mobile app dependencies against those planned characteristics until their UUIDs and versioning are frozen.
