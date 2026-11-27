# Implementation Batch 44 — Telemetry History Account Lockout

Date: 2026-11-27

## Finding
The historical telemetry GET route joined active device bindings but did not constrain the associated user status. Batch 42's shared device-data and member-management checks did not cover this separate telemetry history route.

## Remediation
- Refactored telemetry history to reuse the shared _authorized_device gate.
- The shared gate requires the account status to be active and returns a non-disclosing 404 for locked/deleted users or missing bindings.
- The history query now uses the authorized device ID, avoiding a second, divergent authorization query.
- Added a route-level SQL-contract regression test.
- Batch 43's isolated PostgreSQL integration test also executes the shared gate with active, locked and deleted users.

## Verification boundary
The tests are committed and wired into the backend workflow. No production database was accessed. CI results for the latest head must be checked before declaring the batch verified.
