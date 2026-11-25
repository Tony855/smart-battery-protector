# Implementation Batch 39 — Measurement Failure Semantics and Atomic Event Audit

Date: 2026-11-25

## Firmware sensor conversion

### Finding
The INA228 current conversion helper assigned the calculated value to the caller's output before checking whether the result was finite. An extremely small but positive shunt calibration could overflow the derived current to infinity while the function returned false. Callers that inspect the output after a failed conversion could therefore observe a non-finite value instead of the prior value.

### Change
- Compute the derived current into a local variable.
- Reject non-finite results before modifying the caller's output.
- Add a regression test using the smallest positive subnormal float as a shunt value and a near-rail non-saturated VSHUNT sample.
- Assert that the caller's output remains unchanged when conversion fails.

This does not approve any shunt value or current rating. The shunt, power path and analog front end remain unselected/unverified.

## Backend device event audit atomicity

### Finding
Device event ingestion committed the event and device last-seen update, then opened a second database connection to write the audit row. If the audit insert failed, the API returned 503 even though the event was already committed and no audit row existed. That left an accepted event without its intended audit trail.

### Change
- Add a cursor-scoped audit insert helper.
- Insert the event, update last-seen, and write the audit row using the same database transaction.
- Commit only after all three operations succeed.
- Roll back all three if the audit insert fails.
- Add route-level tests proving same-transaction ordering and rollback on simulated audit failure.

The standalone audit writer remains available for operations that do not already own a business transaction.

## Verification boundary
The changes are committed to the existing PR audit branch. GitHub Actions must validate the new head. No production database migration, production credential, device, OTA, eFuse or hardware operation was performed. No HIL, vehicle, EMC, thermal or certification evidence is implied.
