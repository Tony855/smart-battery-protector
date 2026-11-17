# Firmware implementation batch 04 — structured boot diagnostics

Date: 2026-11-17

## Delivered in source

- Added a portable boot-diagnostics model with bounded enums for reset reason, NVS state, sensor initialization state and monitor-only mode.
- Added a validated compact JSON encoder with strict enum/bitmask checks and output-buffer bounds handling.
- Added host tests for the encoded schema, invalid enum values, unknown reason bits, unsupported modes, null pointers and undersized buffers.
- ESP32-C6 startup now classifies the ESP-IDF reset reason into a stable project-owned enum instead of exposing raw SDK values.
- Startup records whether NVS has no record, a valid-but-not-applied record, corrupt/conflicting data, or an initialization/read error.
- Startup distinguishes I2C bus failure, INA228 availability/identity failure, TMP117 availability/identity failure and INA228 ADC configuration write/read-back failure. Per-sample telemetry validity flags remain authoritative for live samples.
- Startup emits one machine-readable BOOT_DIAG serial log line with schema version, reset code, NVS state, sensor state, fixed monitor-only mode, reason flags and configuration generation.
- Added a separate BLE GATT boot-diagnostics characteristic (9a701003-629b-4d83-9a2c-112233445566). It is READ only; the existing telemetry characteristic remains READ/NOTIFY and unchanged.
- Documented diagnostic enums and reason flags; added HIL cases for reset classification, NVS status, detailed sensor initialization faults and GATT permissions.
- Extended the safe-default CI script to fail if Secure Boot, Flash Encryption, NVS Encryption, application rollback or anti-rollback is accidentally enabled in the engineering build.

## Safety and security limits

- Diagnostic mode is always MONITOR_ONLY. The data is descriptive and cannot activate protection.
- A valid NVS record is reported as VALID_NOT_APPLIED; generation reporting is not proof that the configuration is active.
- The diagnostics characteristic contains no secrets or personally identifying data. It remains unauthenticated read-only engineering telemetry.
- The boot diagnostic sensor state reflects initialization only. Per-sample telemetry validity flags remain authoritative for runtime measurement validity.
- No BLE write, remote control, configuration activation, fault clear or OTA capability is added.
- No physical device, BLE phone interoperability, HIL or vehicle test has been performed.

## Verification

- The previous dual-slot NVS implementation and expanded power-loss regression suite passed complete CI in run [44071200302](https://github.com/Tony855/smart-battery-protector/actions/runs/44071200302).
- The first diagnostics CI attempts exposed a C string-escaping error in the new JSON encoder. That issue was fixed in commit 2050af53122790dacb7392a7d070e26430e78055.
- CI run [44072477788](https://github.com/Tony855/smart-battery-protector/actions/runs/44072477788) was superseded and cancelled after its host tests passed while ESP32-C6 compilation was running. Latest run [44073280227](https://github.com/Tony855/smart-battery-protector/actions/runs/44073280227) includes the detailed sensor-state extension and the new secure-default guards; its host build/tests have passed and ESP32-C6 compilation is still in progress. Do not mark this batch CI-complete until that run finishes.

## Next engineering batch

1. Confirm the diagnostics CI and inspect the ESP-IDF build log/artifact.
2. Add a boot-time sensor health classification that distinguishes bus initialization, device identity, ADC configuration read-back and later sample-read failures without turning transient measurement errors into false "initialized" states.
3. Define Secure Boot, flash encryption, NVS encryption, signed OTA and anti-rollback as a manufacturing provisioning lifecycle before enabling any production security option.
4. Continue keeping protection output disabled and require HIL evidence before hardware actuation.
