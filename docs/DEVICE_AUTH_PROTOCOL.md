# Device request authentication protocol v0.2

## Signature scheme
Device ingestion uses Ed25519 request signatures. Each device has a unique key identifier and 32-byte Ed25519 public key stored by the backend. The private key must remain inside the device provisioning boundary and must never be stored in Git, API logs or ordinary cloud application storage.

## Canonical message
The signed UTF-8 bytes are six newline-separated fields:
1. key identifier
2. Unix timestamp in seconds (1–12 ASCII decimal digits)
3. per-request random nonce (16–128 URL-safe characters)
4. uppercase HTTP method
5. exact request path plus raw query string, if present
6. lowercase hex SHA-256 digest of the exact raw request body

The signature is canonical unpadded Base64URL for a 64-byte Ed25519 signature. The server rejects padding, non-Base64URL characters and non-canonical encodings. Timestamp skew is limited to ±300 seconds by default. The server verifies the signature before atomically claiming `key_id:nonce` in Redis with an expiry covering the accepted timestamp window.

## Implemented server path
- Active credential lookup requires an active device, active credential, and explicit `ed25519` public-key and signature algorithm labels.
- Device event and telemetry routes use Redis-backed fixed-window rate limiting and Redis SET NX replay protection.
- Raw request bodies are streamed with hard 16 KiB event / 8 KiB telemetry limits before authentication or JSON parsing.
- Event and telemetry persistence is idempotent by device-scoped UUID.
- Device event ingestion writes a security audit record after successful persistence.
- User-facing device ownership and history routes use OIDC bearer authentication and active device bindings.

## Deployment and remaining gates
- Use a shared Redis instance for all API workers; the in-memory replay store is test-only.
- Enforce TLS at ingress and use PostgreSQL `sslmode=verify-full` for remote database connections.
- The repository has a one-time claim-code provisioning script, but a reviewed Ed25519 key-generation, secure-element injection, public-key enrollment, rotation and recovery workflow is still missing.
- Production key custody, credential revocation operations, TLS deployment, broker ACLs and MQTT integration require separate implementation and review.
- Device APIs do not expose power commands. Device-local safety logic remains authoritative.
