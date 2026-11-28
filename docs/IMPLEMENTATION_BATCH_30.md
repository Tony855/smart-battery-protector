# Implementation Batch 30 — BLE wire-contract alignment

Date: 2026-11-23

## Changes
- Correct the initial BootDiagnostics reason bitmask from 3 to 19 so its default flags include monitor-only, configuration-not-applied and actuator-not-implemented (bits 0, 1 and 4).
- Rewrite BLE protocol v0.3 documentation to describe the actual short JSON keys and units, diagnostics fields and enums, all three GATT UUIDs, characteristic permissions and current security limitations.
- Strengthen the BLE validator to check both initial payloads, buffer sizes, read-only characteristic flags, UUID byte strings, contract field mappings and documentation disclosure.
- Add protocol/BLE_PROTOCOL.md to the firmware workflow push/PR path filters so contract changes trigger validation.

## Safety/security status
- BLE remains unauthenticated and unencrypted read-only telemetry/diagnostics; the documentation now makes that explicit. No control characteristic is added.
- This batch does not change power-control behavior, commissioning, security configuration or OTA.

## Verification
- New validator and ESP-IDF/host tests are triggered by the batch. Results must be reported only after they complete on the latest PR head.
