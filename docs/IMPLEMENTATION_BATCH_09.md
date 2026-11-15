# Implementation Batch 09 — Ed25519 device request authentication

## Delivered
- Added Ed25519 request-signature verification with timestamp freshness, nonce syntax checks and body-digest binding.
- Added a replay-store interface and a thread-safe in-memory implementation for tests.
- Added unit tests for valid signatures, replay rejection, body tampering and expired timestamps.
- Added migration 003 for per-device Ed25519 public keys and signature algorithm metadata.
- Documented the canonical request format and production deployment requirements.

## Security boundary
The in-memory replay store is not production-safe across multiple workers. No device HTTP endpoint is enabled. Database key lookup, Redis atomic nonce claims, revocation checks, rate limiting, enrollment/provisioning and audit integration remain required before route exposure.
