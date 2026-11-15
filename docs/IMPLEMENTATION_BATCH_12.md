# Implementation Batch 12 — Rate limiting and security audit primitives

## Delivered
- Added a Redis Lua fixed-window rate limiter. Increment and first-hit expiry are atomic across API workers.
- Subject identifiers are SHA-256 hashed before being used as Redis key names.
- Added a parameterized MariaDB audit-event writer with classification validation, commit/rollback and guaranteed connection close.
- Added tests for rate-limit boundaries, invalid policy parameters and audit SQL parameter binding.

## Integration boundary
- These primitives are not yet wired to HTTP routes or global middleware.
- Production must define separate rate limits for device authentication, telemetry and control requests; values require load testing and abuse analysis.
- Redis errors must fail closed for protected operations.
- Audit records must never contain raw secrets, signatures, authorization headers or full telemetry payloads.
- Audit write failure policy must be explicit before endpoint exposure; sensitive actions should not silently proceed without required audit persistence.
