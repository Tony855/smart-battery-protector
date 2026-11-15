# Implementation Batch 10 — Credential lookup and distributed replay protection

## Delivered
- Added read-only lookup of an Ed25519 public key by key ID.
- Lookup requires both credential status and device lifecycle status to be active.
- Public-key Base64 decoding is strict and accepts only 32-byte Ed25519 keys.
- Added Redis replay-store adapter using atomic SET NX with expiry, suitable for multiple API workers.
- Added unit tests for active/inactive/malformed credential handling and duplicate nonce rejection.

## Security and deployment boundaries
- Redis is not yet wired into application startup or an HTTP route.
- Production must use a private Redis endpoint, authentication, TLS where applicable, bounded connection/read timeouts, monitoring and persistence/availability decisions.
- Redis failures must reject device requests; never fall back to the process-local in-memory store in production.
- Credential lookup must use a least-privilege database account.
- Enrollment, key rotation, rate limiting, audit events and API route integration remain outstanding.
- Device-local protection remains authoritative; cloud authentication cannot override the ESP32 safety state machine.

## Validation
Tests in this batch use injected fake database/Redis clients. They validate repository and adapter logic, not a live MariaDB or Redis deployment.
