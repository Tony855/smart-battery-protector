# Implementation Batch 11 — Device authentication composition

## Delivered
- Credential lookup now returns the associated device ID and validated raw Ed25519 public key.
- Added an authentication service that composes active credential lookup, signature verification, timestamp freshness and replay-store nonce claims.
- Invalid/revoked credentials, malformed public keys, bad signatures and repeated nonces all reject with no device identity.
- Database and Redis infrastructure exceptions propagate; the future HTTP adapter must fail closed with a service-unavailable response rather than bypass authentication.
- Added service-level tests for accepted identity, replay rejection and invalid signatures.

## Not enabled
No telemetry, event, command, enrollment or key-rotation HTTP route is exposed yet. The composition layer is not a substitute for rate limiting, request-size limits, audit logging, Redis deployment hardening or end-to-end integration tests.
