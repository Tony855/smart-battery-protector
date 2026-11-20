# Implementation Batch 19 — measurement validity and deployment hardening

Date: 2026-11-20

## Full-repository audit fixes

- INA228 VBUS conversion now rejects measurements above the Rev A protected battery-sense contract of 60.0 V. Invalid readings leave the caller's output value untouched; tests cover the exact 60.0 V boundary, one ADC step above it, full-scale saturation and out-of-width raw input.
- The explicit PostgreSQL migration CLI now delegates connection creation to the same shared runtime factory as the API and claim-code tool. Remote DSNs therefore require `sslmode=verify-full`; local loopback development remains supported.
- Backend CI now actually installs and runs `pip-audit --strict`, matching the supply-chain gate already described in the project status and audit notes.
- OpenAPI parity testing now requires exact equality of HTTP methods for each runtime route, rather than only checking that runtime methods are a subset of the manually maintained contract.
- Added regression tests for the migration CLI's secure shared connection factory and missing secure-configuration behavior.

## Baseline verification before this batch

On PR head `c7c39239b586f5d28cd9af04188c6c197e492fda`:
- Firmware workflow run [44655300110](https://github.com/Tony855/smart-battery-protector/actions/runs/44655300110) passed: portable C build/tests, ESP-IDF 5.4 ESP32-C6 build, partition validation, OTA-slot size check and safe commissioning defaults.
- Built app image was 667,024 bytes of 1,900,544 bytes (35.1% of one OTA slot).
- Firmware artifact was uploaded successfully: [sbp-esp32c6-firmware](https://github.com/Tony855/smart-battery-protector/actions/runs/44655300110/artifacts/14593620102).
- Backend workflow run [44655300098](https://github.com/Tony855/smart-battery-protector/actions/runs/44655300098) passed: Python tests, PostgreSQL 16 migration integration, OpenAPI YAML validation and API container build.
- The latest PR head check-runs were successful before this batch. New checks for this batch are pending until GitHub Actions finishes.

## Remaining engineering gates

- Firmware remains monitor-only in engineering defaults; NVS configuration is validated but not applied to live protection settings.
- No physical actuator driver, production power stage, vehicle transient front end, calibrated shunt or approved current rating exists.
- The Rev A KiCad PCB is a mechanical/layout template, not a routed electrical design. Native schematic capture, footprints, ERC/DRC, Gerbers and drill files remain incomplete.
- Signed OTA runtime, boot confirmation/rollback, Secure Boot, Flash/NVS Encryption and eFuse provisioning remain disabled or unimplemented.
- Device-side Ed25519 key generation, secure-element injection, enrollment, rotation and recovery are not implemented.
- MQTT broker/client/ACL/offline queue, mobile application, WeChat Mini Program and admin application are not implemented.
- HIL, physical NVS power-loss/endurance, real-device flashing, vehicle, environmental, EMC, thermal and certification tests have not been executed.

No production credentials, irreversible hardware configuration, production OTA, eFuse operation, hardware switching or vehicle test was performed in this batch.
