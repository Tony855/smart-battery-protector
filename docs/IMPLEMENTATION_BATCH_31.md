# Implementation Batch 31 — Transactional device-account audit trail

Date: 2026-11-23

## Changes
- Device claim now inserts a user-actor audit row with action device.claim and metadata for device ID/owner role.
- Member add and revoke operations insert audit rows with device ID, target subject and role.
- Audit insertions use the same PostgreSQL transaction as the corresponding membership/claim mutation; audit failure therefore rolls the mutation back.
- Metadata excludes claim codes and other secrets.
- Added a unit test for audit SQL/metadata serialization.

## Verification boundary
The new backend CI run must validate the test suite, dependency audit, OpenAPI validation and container build. The unit test does not replace full endpoint/database concurrency testing.
