# Implementation Batch 25 — NVS generation exhaustion and CI closure

Date: 2026-11-21

## Changes
- Added a host regression test for a persisted configuration at generation `UINT32_MAX`.
- The test proves the current monotonic-generation policy fails closed: a wrapped generation-zero save is rejected with `ESP_ERR_INVALID_STATE`, and the final valid record remains loadable.
- No automatic generation reset, erase, or journal reinitialization is introduced. Recovery from exhausted generation space requires an explicit, separately designed maintenance/migration procedure; silently wrapping would make stale records appear newer/ambiguous.

## CI evidence reviewed before this batch
For PR head `a3363d4be122a03bda7e74fca95f5b3105d19712`:
- Host safety gate run 44854864027: success.
- Backend service run 44854864140: success.
- Firmware portable core run 44854864039: success; ESP-IDF build, OTA-slot size check, safe commissioning defaults and artifact upload all completed.
- A second firmware run 44854854626 also completed all listed steps successfully.
- Artifact `sbp-esp32c6-firmware` from run 44854864039: 419,663 bytes; SHA-256 `7cf7574bc6edecf720ba66bbe7ecd377e4f508882ac47cbdfed48f244acf074a`.

## Limits
- The artifact and checks are CI evidence only; no physical ESP32-C6 flash, NVS power-cut, endurance, HIL, vehicle, EMC or certification test was performed.
- NVS mock still does not model byte/erase-level flash interruption or true flash wear. Further fault injection must not be described as hardware power-loss proof.
- Generation exhaustion is intentionally unrecoverable by ordinary save; a maintenance strategy remains open.
- PR #8 remains open and unmerged. No production keys, OTA rollout, eFuse or encryption provisioning were performed.
