# Firmware implementation batch 02 — persistent configuration foundation

Date: 2026-11-17

## Delivered in source

- Added portable configuration record v1 in `firmware/core/include/sbp_config_record.h` and `firmware/core/src/sbp_config_record.c`.
- The record is serialized explicitly as a 56-byte little-endian payload. It does not persist a native C struct, so compiler padding and target ABI changes cannot silently alter the storage format.
- The record includes magic, format version, exact payload length, generation counter, product variant, protection enable flag, separate 12V/24V thresholds, current and temperature limits, qualification times, shunt calibration and CRC32.
- Decoder rejects wrong size, magic, version, non-zero reserved bytes, invalid boolean values, CRC mismatch and invalid configuration ranges. Signed temperature decoding is explicit and range-safe; protection-enabled records require a positive temperature limit.
- Added host test coverage for round-trip encoding, corrupted payload, truncated payload, invalid hysteresis and monitor-only uncommissioned records.
- Added ESP-IDF NVS adapter in `firmware/esp-idf/main/config_store.c` with load/save operations.
- Firmware startup attempts to load and validate an existing record. It logs the record generation but deliberately does not apply it to protection logic in this increment. The runtime remains monitor-only.
- NVS initialization never erases the partition automatically on version or space errors. Such conditions are reported and leave protection disabled.

## Security and safety limits

- CRC32 detects accidental corruption; it is not a cryptographic authenticity mechanism.
- The NVS save API is not exposed through BLE, MQTT or a mobile command path.
- NVS writes reject a generation number that is not strictly newer than the stored record. If the existing record cannot be read or validated, the save path refuses to overwrite it; this avoids treating corruption as permission to reset configuration.
- No credentials, keys or personally identifying information are stored in this record.
- Protection remains disabled in the application even if a valid record exists. A later commissioning phase must add authenticated authorization, configuration review, safe range checks and explicit activation policy.
- NVS encryption, secure boot, flash encryption, signed OTA and anti-rollback are not yet commissioned.
- The physical actuator remains unimplemented and is not driven.

## Verification

- Host CI now includes `sbp_config_record_test`, including the standard CRC32 `123456789` known vector, invalid variant and invalid temperature-limit cases.
- ESP-IDF CI compiles the same portable record code into the ESP32-C6 target and checks safe defaults against the generated `sdkconfig` file.
- The prior ESP-IDF compile/link completed successfully, but the earlier CI run failed in its post-build grep because it inspected generated header formatting and expected a disabled Kconfig boolean to be represented as numeric zero. The verification script now checks the authoritative `sdkconfig` representation, including the standard “is not set” boolean form.
- The latest CI run for this batch must be checked before calling the host test, ESP-IDF build or artifact upload successful.

## Next engineering batch

1. Confirm latest host tests, ESP-IDF build, safe-default assertions and artifact upload.
2. Add power-loss-safe NVS write strategy and generation selection if redundant slots are adopted.
3. Add authenticated local commissioning with no unauthenticated BLE control.
4. Add independent tests for invalid NVS payloads and power-cycle recovery.
5. Keep protection output disabled until external power stage, engine interlock hardware and HIL acceptance criteria are reviewed.
