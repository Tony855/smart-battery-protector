# Implementation Batch 07 — PostgreSQL schema migrations

## Delivered
- Added an explicit PostgreSQL migration runner at backend/service/app/migrate.py.
- Canonical migrations are under backend/db/postgresql/migrations/.
- Added checksum tracking in schema_migrations; an already-applied migration whose contents change is rejected.
- The runner takes a PostgreSQL advisory transaction lock to prevent concurrent migration runs.
- Added unit tests for SQL statement splitting, checksums and migration ordering.

## Safety and operation
- Migrations are not run automatically when the API starts.
- Provision the PostgreSQL database and credentials separately; the migration does not create a database or database user.
- Run python -m app.migrate from backend/service with the PostgreSQL environment configured.
- PostgreSQL DDL runs transactionally in this migration runner; a failed batch is rolled back.
- SQL parser scope is intentionally limited: no stored procedures, delimiter directives, or semicolons inside quoted strings.
- Never edit a migration after it has been applied; add a new numbered migration instead.

## Validation boundary
Unit tests cover deterministic helper functions. The backend CI also applies all migrations against a real PostgreSQL service. Production backup, restore and failover remain deployment responsibilities.
