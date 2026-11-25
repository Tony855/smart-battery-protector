# Implementation Batch 41 — Restore Audit Validation Before Database Access

Date: 2026-11-25

## CI finding
The Backend workflow exposed a regression in the standalone audit writer after adding the cursor-scoped insert helper. Invalid audit classifications were still rejected, but validation happened after calling the connection factory. The existing contract and regression test require invalid classifications to be rejected before any database access.

## Fix
- Extract shared actor/result classification validation.
- Validate in the cursor-scoped helper before issuing SQL.
- Validate in the standalone writer before opening a database connection.
- Preserve same-transaction insertion for device-event ingestion.

## Verification
The failing backend test was test_invalid_audit_classification_is_rejected_before_db_access. The CI run also reported 78 passing tests, including the new device-event atomicity tests. The fix is committed and the Backend workflow must be rechecked on the new head before this regression is considered closed.

No production database, device, OTA, eFuse or hardware action was performed.