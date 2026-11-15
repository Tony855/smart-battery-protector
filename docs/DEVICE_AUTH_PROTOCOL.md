# Device request authentication protocol v0.1

## Signature scheme
Device requests use Ed25519 signatures. The device keeps its private key in protected device storage; the backend stores only the 32-byte public key (Base64 representation) against a unique key identifier. Raw private keys must never leave the device provisioning boundary.

## Canonical message
The signed UTF-8 bytes are six newline-separated fields:
1. key identifier
2. Unix timestamp in seconds (decimal)
3. per-request random nonce (16–128 URL-safe characters)
4. uppercase HTTP method
5. exact request path, including query string if present
6. lowercase hex SHA-256 digest of the exact raw request body

Signature is Base64URL without required padding. Server checks timestamp skew (default ±300 seconds), verifies Ed25519, then atomically claims `key_id:nonce` for at least the full accepted time window. Invalid signatures must not consume nonces.

## Deployment requirements
- Use a shared atomic replay store (e.g. Redis SET NX with expiry) across all API workers. The included in-memory store is for tests/single-process development only.
- Enforce TLS, credential status/revocation, per-device rate limits, body-size limits, strict path canonicalization and audit logging.
- Keep private keys in a secure element or platform-protected storage where available; define factory provisioning and recovery procedures.
- Do not accept device commands based solely on signature validity. Device authorization and local safety-state validation remain separate gates.

## Current boundary
The verification primitive and unit tests are implemented, but no HTTP route, database key lookup, Redis adapter, rate limiter, enrollment service or production key custody is wired yet. Do not expose device APIs until those components are completed and independently reviewed.
