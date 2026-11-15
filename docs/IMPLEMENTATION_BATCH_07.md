# Implementation Batch 07 — MariaDB schema migrations

## Delivered
- Added an explicit migration runner at `backend/service/app/migrate.py`.
- Added baseline migration `backend/db/migrations/001_initial_schema.sql`, carrying forward the logical tables from `backend/db/schema.sql`.
- Added checksum tracking in `schema_migrations`; an already-applied migration whose contents change is rejected.
- Added unit tests for SQL statement splitting, checksums and migration ordering.

## Safety and operation
- Migrations are **not** run automatically when the API starts.
- Provision the target MariaDB database and credentials separately; the migration does not issue `CREATE DATABASE` or `USE`.
- Run from the repository root with the service environment configured:
  `python -m app.migrate` (from `backend/service`).
- DDL in MariaDB can implicitly commit. Each migration must be restart-safe; this runner records a migration only after all its statements complete.
- SQL parser scope is intentionally limited: no stored procedures, delimiter directives, or semicolons inside quoted strings.
- Never edit a migration after it has been applied; add a new numbered migration instead.

## Validation boundary
Unit tests cover the deterministic helper functions. A real MariaDB integration run is still required before production use. No production database was modified by this batch.
