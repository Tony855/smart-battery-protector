# SBP API service

## Local run
1. Install Python 3.11+ and PostgreSQL 15+.
2. From backend/service, create a virtual environment and install with pip install -e '.[test]'.
3. Set SBP_DATABASE_URL to a PostgreSQL connection string and SBP_REDIS_URL to Redis.
4. Run python -m app.migrate, then uvicorn app.main:app --reload.
5. Run pytest.

PostgreSQL 15+ is the only supported application database. Use sslmode=verify-full in SBP_DATABASE_URL for remote production connections. The API does not run migrations automatically.

## Database migrations
Canonical PostgreSQL migrations are in backend/db/postgresql/migrations/. Run python -m app.migrate explicitly before deploying a new API version. The runner uses a PostgreSQL advisory lock and checks immutable migration checksums. Never edit an applied migration; add a new numbered migration instead.

Connection settings:
- Preferred: SBP_DATABASE_URL (PostgreSQL libpq DSN; supports sslmode).
- Alternative: SBP_DB_HOST, SBP_DB_PORT (default 5432), SBP_DB_USER, SBP_DB_PASSWORD, SBP_DB_NAME.
- SBP_REDIS_URL remains required for replay protection and rate limiting.

## Safety and security boundary
No device command route is implemented. Do not expose this scaffold as a production API until identity, authorization, rate limits, audit logging, secrets management and live integration tests are complete. Device-local interlocks remain authoritative.

## User authentication and device ownership
Configure a trusted OIDC provider using SBP_JWT_JWKS_URL, SBP_JWT_ISSUER and SBP_JWT_AUDIENCE.
Routes include GET /api/v1/me/devices and POST /api/v1/me/devices/bind. Raw device claim codes are never persisted or logged.

## Device claim-code provisioning
Run on a controlled provisioning station:
python scripts/provision_claim_code.py --serial SBP-000001 --ttl-hours 24
The command stores only the SHA-256 digest and prints the high-entropy code once. Do not run it in CI or capture stdout in logs.

## Telemetry units and API
- Device-signed POST /api/v1/device/telemetry
- Owner-scoped GET /api/v1/me/devices/{serial_number}/telemetry?limit=100
- battery_voltage_v: volts (V), decimal resolution 0.001 V.
- battery_current_a: amperes (A), signed decimal resolution 0.001 A.
- temperature_deci_c: integer count of 0.1°C; 253 means 25.3°C.
- observed_at is timezone-aware; database timestamps use TIMESTAMPTZ.
- Measurements are observational only and cannot trigger relay/contactor switching.

## Device presence and shared access
A device is online only after a valid signed event or telemetry is received in the preceding 90 seconds.
Owner/admin member routes list, add and revoke memberships. Owners may add admins and viewers. Admins may add/remove viewers only.

## Dashboard and event history
GET /api/v1/me/devices/{serial_number}/status
GET /api/v1/me/devices/{serial_number}/events?limit=50&before_id=123
Both require a valid OIDC bearer token and an active device binding.
