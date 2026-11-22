# Implementation Batch 27 — NVS read fault and post-commit verification coverage

Date: 2026-11-22

## NVS journal host tests
- Added one-shot injection for blob-size query errors and blob data-read errors.
- Added tests that verify load and save fail closed on transient NVS read errors and do not overwrite the existing journal generation.
- Added post-commit readback failure injection. The test deliberately distinguishes a failed verification from a failed commit: the mock commits generation 71, the verification read fails, save returns an error, and a later load resolves the persisted generation. The test then advances to generation 72.
- This exposes the ambiguous-result semantics of a commit followed by failed readback: callers must re-read before retrying the same generation; an immediate duplicate save is rejected by monotonic generation validation.

## Validation evidence before this batch
- PR head `e35c529acd9b392fb9150aea8ddbbdae9d73bcb9` was checked on 2026-11-22.
- Firmware portable core/ESP-IDF run 44855793708 passed configure, build, tests, ESP-IDF app build, OTA slot sizing, safe-default verification and artifact upload.
- Host safety gate run 44855793711 passed.
- Backend run 44855793741 passed dependency audit, unit/integration tests, OpenAPI validation and container build.
- Duplicate runs 44855788125 and 44855788138 also passed on the same SHA.
- Firmware artifact from run 44855793708: 419,664 bytes; GitHub artifact digest SHA-256 `58756ed4a874177cbe3d17a10d8dfedc18a9c1778331300b774cd16f48dec13e`.

## Remaining limitations
- These are mock-level fault tests. They do not simulate real NVS page erasure/programming, brownout, byte-level power loss, wear, concurrency or flash recovery.
- A save returning an error after successful commit and failed verification can have an uncertain outcome. Re-read the journal and inspect generation before retrying.
- MQTT is still a contract draft only; broker/client/credential lifecycle/ACL implementation remains unverified.
- No actuator output, HIL, vehicle, EMC, certification, production OTA, eFuse or production-key operation is claimed.
- PR #8 remains open and unmerged; this batch does not merge it.
