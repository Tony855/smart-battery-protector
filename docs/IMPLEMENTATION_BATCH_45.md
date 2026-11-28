# Implementation Batch 45 — Live CI, Artifact Verification and Lifecycle Policy Review

Date: 2026-11-28

## Validation baseline
Validated PR #8 head `a30f865d01ca6a436e7d36cb15ea2b073e2ae66c` (not main).

- Host Safety Gate run 45924653753: success; Configure, Build and CTest passed.
- Backend run 45924653708: success. pip-audit reported no known vulnerabilities; Pytest reported 83 passed, 1 warning; OpenAPI validation and Docker build succeeded.
- Firmware run 45924653767: success. Partition layout and BLE schema validators passed; CMake build/CTest passed; ESP32-C6 ESP-IDF build succeeded; application slot-size and safe-default checks passed; artifact upload succeeded.
- Combined commit status contexts were empty. These workflow runs are the actual CI evidence.
- Main SHA `cc309fa69e49dab4ca53a8c71ee8c73524bcb95c` has no attached workflow runs or status contexts in the queried data.

## Firmware artifact
- Artifact: `sbp-esp32c6-firmware`
- Artifact ID: 15165892547
- ZIP size: 419,706 bytes
- ZIP SHA-256: `3011d6b6bc7897e16335f003463f6128883b4b3112930fbbaacac849345280fd`
- Application binary: 667,120 bytes (`0xa2df0`)
- Smallest OTA slot: 1,900,544 bytes (`0x1d0000`); 1,233,424 bytes (65%) free.
- Archive contains bootloader, partition table, initial OTA data, project description, flash arguments and application image.
- Flash metadata marks the bootloader, app, partition table and OTA data unencrypted. No flashing, release or production OTA occurred.

## Whole-project review
No new code defect was confirmed in the files examined during this run. The following policy gap is recorded for qualified review, not changed without a product decision:

- User/device data authorization helpers currently gate on active user and active binding but do not explicitly filter device lifecycle status. Suspended/retired devices may remain visible to a still-active bound user. Decide whether historical/status access is retained or denied after device suspension/retirement, then implement and test consistently.

## Remaining evidence gaps
- No native electrical schematic, routed PCB, ERC/DRC or manufacturing outputs.
- No power-stage, load-dump/reverse-polarity, contactor, shunt or engine-valid isolation validation.
- BLE remains read-only, unauthenticated and unencrypted.
- MQTT runtime is not implemented.
- Secure Boot, Flash/NVS Encryption, signed production OTA and eFuse provisioning are not enabled.
- No physical flash power-cut, HIL, vehicle, EMC, thermal or certification tests.

## Boundary
This batch records verified CI and artifact evidence only. It does not approve vehicle use, production firmware, flashing, OTA, hardware ratings or certification.
