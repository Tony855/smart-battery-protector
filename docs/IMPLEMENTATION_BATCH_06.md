# Implementation Batch 06 — Database readiness probe

## Delivered
- Added a bounded-time PostgreSQL connectivity probe.
- Readiness endpoint executes SELECT 1 when PostgreSQL configuration is present.
- Readiness fails closed with HTTP 503 when database configuration is absent or the connection/probe fails.
- Tests cover liveness, unavailable database and successful mocked database probe.

## Environment variables
- Preferred: SBP_DATABASE_URL (PostgreSQL DSN).
- Alternative: SBP_DB_HOST, SBP_DB_PORT (default 5432), SBP_DB_USER, SBP_DB_PASSWORD, SBP_DB_NAME.
- SBP_ENV (optional; defaults to development).

Do not commit credentials. Use deployment secret storage. Use TLS verification for remote PostgreSQL connections.

## Verification note
The endpoint tests validate readiness branching and response behavior. A live PostgreSQL integration test is now part of the backend workflow; production availability, backup and failover still require deployment-level validation.

## Current database policy
PostgreSQL 15+ is the sole supported backend database. The earlier MariaDB/PyMySQL implementation has been removed.
