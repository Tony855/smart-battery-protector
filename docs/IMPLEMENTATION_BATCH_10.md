# Implementation Batch 10 — Credential lookup and distributed replay protection

## Delivered
- Added read-only lookup of an Ed25519 public key by key ID.
- Lookup requires both credential status and device lifecycle status to be active.
- Public-key Base64 decoding is strict and accepts only 32-byte Ed25519 keys.
- Added Redis replay-store adapter using atomic SET NX with expiry, suitable for multiple API workers.
- Added unit tests for active/inactive/malformed credential handling and duplicate nonce rejection.

## Security and deployment boundaries
- Production must use a private Redis endpoint, authentication, TLS where applicable, bounded connection/read timeouts, monitoring and persistence/availability decisions.
- Redis failures must reject device requests; never fall back to the process-local in-memory store in production.
- Credential lookup must use a least-privilege PostgreSQL account.
- Enrollment, key rotation, rate limiting, audit events and API route integration remain outstanding.
- Device-local protection remains authoritative; cloud authentication cannot override the ESP32 safety state machine.

## Validation
Tests use injected fake database/Redis clients. The PostgreSQL migration and live schema test are separate CI coverage; they do not prove full production identity, Redis failover or hardware interoperability.
