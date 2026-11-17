# Firmware implementation batch 03 — dual-slot NVS journal

Date: 2026-11-17

## Delivered in source

- Replaced the single mutable \`record_v1\` save target with two alternating NVS slots: \`record_a\` and \`record_b\`.
- Kept \`record_v1\` as a read-only migration/fallback source. New writes never modify the legacy key.
- Load scans both slots and the legacy record, validates the complete 56-byte encoding and CRC, and selects the highest valid generation.
- If the newest slot is corrupt but another valid generation remains, the valid record is used. If no valid record remains and any stored record is corrupt, load/save fail closed.
- Save rejects non-increasing generations, writes the older/inactive slot, commits, then reads the exact bytes back for verification.
- A failed write/commit targets only the inactive slot; the previously newest committed slot is left untouched.
- Equal-generation records must be byte-identical. Conflicting payloads at the same generation fail closed.
- Generation wraparound is not supported. \`UINT32_MAX\` is a terminal generation until a separately reviewed service/re-provisioning process exists.
- Added a host-side NVS mock with durable and pending storage so a simulated commit interruption can verify that the old committed slot remains available.
- Added tests for first save, failed commit, successful retry, stale-generation rejection, corrupt-newest fallback, legacy migration, corrupt-only storage and equal-generation conflict.
- Extended the HIL plan with dual-slot rotation, corruption fallback, legacy migration and generation-conflict cases.

## Safety and security limits

- CRC32 detects accidental corruption only; it does not authenticate a configuration against an attacker.
- No BLE, MQTT, mobile or cloud configuration-write path is exposed.
- A valid stored record is still not applied to live protection settings. The ESP32-C6 application remains monitor-only and the physical actuator output is not implemented.
- Host NVS mock tests are not a substitute for real flash power-interruption, brownout, endurance or hardware-in-loop testing.
- Do not enable NVS encryption, secure boot, flash encryption or OTA by changing a build flag alone; production key provisioning, recovery and rollback policy must be designed and verified together.

## Verification

- Host CMake configuration and build passed after correcting the test source path.
- The host CTest step passed for commit \`59e2ecb0f05b7d266a9b8dedbb616e5483e1045f\`.
- The ESP32-C6 ESP-IDF build, safe-default verification and artifact upload are being checked in GitHub Actions run [44070631764](https://github.com/Tony855/smart-battery-protector/actions/runs/44070631764). Do not treat this batch as fully CI-verified until that run completes successfully.
- No physical ESP32-C6 flash, power-cut test, HIL or vehicle test has been performed.

## Next engineering batch

1. Confirm the ESP32-C6 build, safe-default check and artifact upload for the current commit.
2. Add structured boot diagnostics for NVS state, sensor initialization and safe monitor-only fallback.
3. Define production Secure Boot, flash encryption, NVS encryption, signed OTA and anti-rollback as one manufacturing lifecycle.
4. Keep remote control and live configuration activation disabled until authenticated commissioning and independent safety review are complete.
