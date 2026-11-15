# Implementation Batch 06

## Delivered
- Added a MariaDB connectivity probe using PyMySQL.
- Readiness endpoint now executes a bounded-time `SELECT 1` probe when all required DB environment variables exist.
- Readiness fails closed with HTTP 503 when database configuration is absent or the connection/probe fails.
- Tests cover liveness, unavailable database and successful mocked database probe.

## Environment variables
- `SBP_DB_HOST`
- `SBP_DB_PORT` (optional; defaults to 3306)
- `SBP_DB_USER`
- `SBP_DB_PASSWORD`
- `SBP_DB_NAME`
- `SBP_ENV` (optional; defaults to development)

Do not commit credentials. Use deployment secret storage.

## Verification note
The three API tests passed locally with a temporary import stub for PyMySQL because this execution environment could not reach package indexes to install the driver. This verifies endpoint branching and response behavior, not an actual MariaDB connection. GitHub Actions installs the declared PyMySQL dependency; its cloud result must be checked separately.

## Remaining work
- Add schema migration runner and database integration tests against a real MariaDB service.
- Implement authentication and per-device authorization before any user/device routes.
- Implement MQTT broker health probe and tenant/device ACL.
