# Implementation Batch 13 — Authenticated device event ingestion

## Delivered
- Added lazy MariaDB and Redis runtime factories; importing the API does not open network connections.
- Added `POST /api/v1/device/events` with Ed25519 request authentication, Redis-backed rate limiting and nonce replay protection.
- Enforces a 16 KiB request body limit, strict event payload fields, UUID event identity, event-type syntax and timezone-aware occurrence timestamps.
- Stores events with a per-device idempotency key; duplicate event UUIDs do not create duplicate rows.
- Writes a security audit record after event persistence.
- Normalizes event timestamps to UTC before MariaDB insertion.
- Power-control endpoints remain disabled.

## Required database rollout
Apply migrations 001, 002 and 003 in order before enabling the endpoint. Migration 003 adds the Ed25519 public-key columns required by the authentication repository. The credential enrollment/provisioning workflow that populates those public keys is not yet implemented.

## Required runtime configuration
Set `SBP_DB_HOST`, `SBP_DB_PORT` (optional), `SBP_DB_USER`, `SBP_DB_PASSWORD`, `SBP_DB_NAME` and `SBP_REDIS_URL`. Use TLS/private networking, least-privilege accounts and managed secrets in production.

## Validation boundaries
Payload validation tests use the Pydantic model. CI does not prove live MariaDB/Redis integration, throughput, TLS configuration or end-to-end device firmware interoperability. Authentication failures are rejected; infrastructure failures return 503. Device-local safety remains authoritative.
