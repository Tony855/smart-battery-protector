# Implementation Batch 40 — BLE Enum and Migration Documentation Consistency

Date: 2026-11-25

## BLE voltage-class mismatch

### Finding
The C wire enum defines:
- SBP_VOLTAGE_UNKNOWN = 0
- SBP_VOLTAGE_12V = 12
- SBP_VOLTAGE_24V = 24

The BLE telemetry guide incorrectly documented 1 as 12V and 2 as 24V, and its sample payload used vc=1. The firmware publishes the enum value directly, so a client following the guide could misdecode 12V/24V classification.

### Change
- Correct the BLE telemetry guide to document 0 UNKNOWN, 12 12V and 24 24V.
- Correct the example payload to vc=12.
- Make the BLE protocol contract explicit about the numeric values.
- Extend the BLE schema validator to read the C enum header and assert that both client-facing documents match it.

## PostgreSQL migration guide drift

### Finding
The migration guide still told operators to verify migrations 001–007 even though the current repository contains migrations 008 and 009.

### Change
- Update the fresh-install verification step to migrations 001–009.
- Document migration 008's NOT VALID temperature-range constraint and its legacy-row behavior.
- Document migration 009's partial unique indexes and the need for separately reviewed duplicate-row reconciliation if index creation fails.
- Do not run migrations against any production database as part of this batch.

## Verification boundary
Firmware and backend workflows are triggered by the changed paths. Their results must be checked against the resulting PR head. No production database migration, destructive data cleanup, BLE client release, hardware, OTA or eFuse operation was performed.
