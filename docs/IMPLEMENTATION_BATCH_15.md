# Implementation Batch 15 — Provisioning and telemetry (updated for PostgreSQL)

## Delivered
- PostgreSQL migration 005 creates an append-only telemetry table with per-device sample UUID idempotency and a time-series index.
- Device-signed POST /api/v1/device/telemetry uses Ed25519 authentication, Redis replay protection, rate limiting, strict validation, timezone enforcement and duplicate suppression.
- Authenticated owner-scoped GET /api/v1/me/devices/{serial_number}/telemetry supports bounded page size (1–500).
- Provisioning CLI creates a high-entropy one-time device claim code; only its SHA-256 digest is stored and raw code is printed once.
- Telemetry routes are observational only; they cannot trigger relay/contactor switching.

## Telemetry units and limits
- battery_voltage_v: decimal volts (V), 0–60 V, resolution 0.001 V.
- battery_current_a: signed decimal amperes (A), -1000–1000 A, resolution 0.001 A.
- temperature_deci_c: signed integer in 0.1°C units, -500 to 2000 (equivalent to -50.0°C to 200.0°C); 253 means 25.3°C.
- Engine-running state is explicit yes/no/unknown; unknown is not interpreted as safe.
- State codes are observational labels only and do not authorize power switching.

## Database transition
PostgreSQL 15+ is the only supported backend database. The new canonical migrations live under backend/db/postgresql/migrations. Do not run the former MariaDB SQL migrations against PostgreSQL. Any legacy export must convert the three measurement units before import.

## Verification boundaries
Automated schema and unit tests are not a substitute for live PostgreSQL/Redis integration, concurrent claim-code redemption, real identity-provider JWKS validation, device key provisioning, MQTT delivery or hardware-in-the-loop tests.
