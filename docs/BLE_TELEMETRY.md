# BLE telemetry protocol v1

Status: read-only monitoring interface. This is not a commissioning or control protocol.

## GATT

- Device name: `SBP-CTRL`
- Service UUID: `9a701001-629b-4d83-9a2c-112233445566`
- Telemetry characteristic UUID: `9a701002-629b-4d83-9a2c-112233445566`
- Characteristic permissions: READ and NOTIFY only
- Preferred ATT MTU: 128 bytes
- No BLE write characteristic exists for switching, configuration, fault clearing or commissioning.

## JSON payload

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
| tc | integer or null | Temperature in 0.1 °C units |
| tv | boolean | Temperature measurement validity |
| e | integer | Engine: 0 unknown, 1 off, 2 running |
| s | integer | Controller state (see below) |
| vc | integer | Voltage class: 0 unknown, 1 12V, 2 24V |
| pe | boolean | Protection enabled; false in this firmware |

A numeric sensor field MUST be treated as unusable when its corresponding validity flag is false, even if a client receives a cached value. A `null` numeric field is the expected representation for an invalid reading.

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

## Client behavior

- Check `v` before decoding fields.
- Use `n` to detect missed notifications; wraparound is expected.
- Treat unknown enum values as unknown, not as a safe state.
- Display sensor validity separately from the numeric value.
- Negotiate an ATT MTU of at least 128 bytes where supported; clients with a smaller MTU may use characteristic reads and must not assume every notification can be delivered.
- BLE disconnection must not change local controller behavior.
- This development characteristic is unauthenticated read-only telemetry. Do not include secrets or personally identifying information.
- Do not infer that a displayed logical controller state means a physical contactor has switched.

## Current limitations

- Firmware protection remains disabled by default and the application currently forces protection off.
- No authenticated commissioning, remote control, configuration write, fault-clear or OTA operation is exposed.
- Phone interoperability and notification delivery require device-level validation with HIL evidence before release.
