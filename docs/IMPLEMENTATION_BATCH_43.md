# Implementation Batch 43 — PostgreSQL Authorization Integration Coverage

Date: 2026-11-27

## Change
Extended the isolated PostgreSQL migration integration test to exercise the actual device authorization helpers against a migrated schema with active, locked and deleted users who retain active bindings.

The test verifies:
- An active owner is accepted by device-data authorization and owner/admin role lookup.
- A locked user with an active viewer binding is rejected with the non-disclosing 404 behavior.
- A deleted user with an active viewer binding is likewise rejected.
- These checks execute through psycopg against PostgreSQL rather than only inspecting mocked SQL strings.

## Verification boundary
The test is wired to the existing CI PostgreSQL service through SBP_TEST_DATABASE_URL. It is not claimed to have run successfully until the latest-head workflow completes. It does not access or modify a production database.
