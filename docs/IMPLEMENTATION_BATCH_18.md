# Implementation Batch 18 — Full audit hardening

Date: 2026-11-20

## Findings fixed in this batch
- Controller state regression: a controller already in DISCONNECTED or RECOVERY_QUALIFY could continue returning `disconnect_request=true` after engine state changed to RUNNING or UNKNOWN. The state now stops emitting a disconnect request immediately and latches the engine-interlock fault until a valid OFF state is observed.
- Defensive enum validation: corrupted/out-of-range controller state, engine state, actuator feedback or request values now fail closed with no disconnect request.
- INA228 measurement integrity: signed VSHUNT ADC rail codes (0x7FFFF and 0x80000) are invalidated as saturation. Returning a clipped value could otherwise hide overcurrent when the configured threshold exceeded the sensor's measurable range.
- API memory safety: event and telemetry routes previously called `request.body()` before checking size, so the application buffered an arbitrarily large body before rejecting it. Both routes now stream into a bounded buffer and reject at 16 KiB / 8 KiB.
- Device request signing: signature parsing now requires canonical unpadded Base64URL, timestamps use ASCII decimal digits, and signed request targets include the raw query string.
- Credential algorithm binding: active key lookup now requires both public-key and signature algorithm metadata to be explicitly `ed25519`.
- Transport security: remote OIDC JWKS endpoints require HTTPS, remote PostgreSQL requires `sslmode=verify-full`, and remote Redis requires `rediss://` with certificate and hostname verification. Loopback development remains supported.
- Provisioning safety: the claim-code CLI now uses the same TLS-enforcing PostgreSQL connection factory as the API.
- Membership integrity: migration 009 adds partial unique indexes for one active binding per device/user and one active owner per device. It does not delete existing data; duplicate legacy rows must be reconciled before applying the migration. Unique races now return HTTP 409.
- Unit contract: backend Pydantic validation and PostgreSQL constraint now match TMP117/firmware valid range -55.0°C to +150.0°C via additive migration 008. The constraint is added `NOT VALID`: new writes are checked immediately, existing rows are not rewritten or scanned by the migration. Review legacy out-of-range rows before manually validating the constraint.
- Hardware documentation: BOM connector J4 corrected from 3-pin to 4-pin and the duplicate J7 row removed.
- API contract and device-auth/security documents synchronized to implemented routes and current Ed25519 behavior; unimplemented command, remote config, MQTT and OTA routes are explicitly marked future work.

## Added/updated tests
- Controller regression tests for engine RUNNING/UNKNOWN after disconnect and during recovery, plus invalid enum values.
- INA228 positive/negative saturation tests and near-rail valid samples.
- Request-body streaming tests for exact limit, limit+1 and Content-Length preflight.
- Ed25519 canonical Base64URL and request-target query tests.
- Credential algorithm allowlist assertions.
- PostgreSQL migration integration assertion for the TMP117 range, NOT VALID state, rejection of out-of-range new rows and uniqueness of active bindings/owners.
- OpenAPI route/method/version parity tests.
- Runtime tests for remote PostgreSQL, Redis and JWKS TLS requirements with loopback development exceptions.

## Verification status
Host C tests and backend unit/integration tests are running in the PR workflows. No hardware, HIL, vehicle, production key, OTA or eFuse operation is part of this batch.
