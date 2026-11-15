# Implementation Batch 15 — Provisioning and telemetry

## Delivered
- Added migration 005 with an append-only device telemetry table, per-device sample UUID idempotency and time-series index.
- Added device-signed `POST /api/v1/device/telemetry` with Ed25519 authentication, Redis replay protection, rate limiting, strict field validation, timezone enforcement and duplicate suppression.
- Added authenticated owner-scoped `GET /api/v1/me/devices/{serial_number}/telemetry` with bounded page size (1–500).
- Added a trusted provisioning-station CLI to create a high-entropy, one-time device claim code. Only the SHA-256 digest is persisted; previous unused codes are invalidated; raw code is printed once.
- Added tests for measurement bounds, enum allowlists, unknown fields and timestamp timezone handling.
- Registered telemetry routes in API v0.4.0 and updated operational documentation.

## Telemetry units and limits
- Battery voltage: integer millivolts, 0–60,000.
- Battery current: signed integer milliamps, -1,000,000 to 1,000,000.
- Temperature: signed centi-degrees Celsius, -5,000 to 20,000.
- Engine-running state is explicit yes/no/unknown; unknown is not interpreted as safe.
- State codes are observational labels only. They do not authorize or trigger power switching.

## Provisioning command
`python scripts/provision_claim_code.py --serial SBP-000001 --ttl-hours 24`

The command requires trusted database access and should run only on a controlled manufacturing/provisioning station. The one-time output must be delivered through a protected channel. Do not run it in CI or capture its stdout in logs.

## Verification boundaries
GitHub Actions validates schema-level behavior. Live MariaDB/Redis integration, concurrent claim-code redemption, real identity-provider JWKS validation, device key provisioning, MQTT delivery and hardware-in-the-loop tests remain outstanding.
