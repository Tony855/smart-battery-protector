# Implementation Batch 28 — scheduled verification and evidence refresh

Date: 2026-11-22

## Changes
- Added daily scheduled triggers to the firmware/ESP-IDF validation workflow at 01:15 UTC.
- Added daily scheduled triggers to backend tests, PostgreSQL integration and strict dependency audit at 01:20 UTC.
- Added daily scheduled triggers to host safety-gate tests at 01:25 UTC.
- Kept existing push, pull-request and manual workflow triggers.
- Updated PROJECT_STATUS.md to reflect the live repository state and latest verified PR head evidence.

## Activation boundary
GitHub scheduled workflows run from the repository's default branch. These schedule changes are committed to the audit branch and are not active for daily runs until the changes are merged into main. This batch does not merge PR #8 and does not alter main.

## Latest verified evidence before Batch 28 workflow edits
- PR #8 head: bc7d5324d92aff86493274c99e534b6f9d7bc742.
- Backend run 44972401774: success.
- Host safety run 44972401765: success.
- Firmware run 44972401724: success, including ESP32-C6 ESP-IDF build, OTA slot size check, safe commissioning defaults and artifact upload.
- Artifact sbp-esp32c6-firmware: 419,667 bytes; SHA-256 83920fa6a96e7aa5959da1598c8a8e824e5aeee9746bc986a98afa5d9a41456e.

## Safety and validation limits
- Scheduled CI validates repository tests/builds only; it does not perform physical hardware, HIL, vehicle, EMC, certification or production tests.
- No production OTA, Secure Boot, Flash/NVS encryption enablement, eFuse programming, production credential operation or hardware actuation was performed.
- Re-run CI on the resulting Batch 28 head before treating the workflow edits and documentation as validated.
