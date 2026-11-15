# Implementation Batch 14 — User identity and device ownership

## Delivered
- Added OIDC/JWKS-backed user access-token verification using PyJWT.
- Tokens require configured issuer, audience, expiration, issued-at and subject claims; only RS256/ES256 are accepted.
- Added authenticated `GET /api/v1/me/devices` to list the caller's active device bindings.
- Added `POST /api/v1/me/devices/bind` to claim a device using its serial number and one-time enrollment code.
- Enrollment code comparison uses SHA-256 digests and constant-time comparison; the raw code is not stored.
- Device row and claim row are locked during claim; claim code consumption, device activation and owner binding are committed in one transaction.
- Added migration 004 for expiring, single-use claim-code records.
- Added strict request-schema tests and OIDC token-validation tests.

## Required configuration
- `SBP_JWT_JWKS_URL`: trusted identity provider JWKS endpoint.
- `SBP_JWT_ISSUER`: exact expected issuer.
- `SBP_JWT_AUDIENCE`: API audience.
- User tokens must be minted by the configured identity provider. Do not accept arbitrary client-created JWTs.

## Enrollment/provisioning boundary
Manufacturing or a trusted provisioning station must generate a high-entropy one-time claim code, store only its SHA-256 digest in `device_claim_codes.code_hash`, and set a short expiry. The raw code should be delivered to the owner through a protected channel and never logged. A provisioning workflow and operational admin authorization are not yet implemented; do not insert claim codes manually in production without a controlled procedure.

## Security boundaries
- Device ownership APIs do not expose remote power switching.
- Owner claim is allowed only while the device is in `provisioning`; already active/suspended/retired devices cannot be claimed by this endpoint.
- OIDC/JWKS availability and key rotation need staging validation against the chosen identity provider.
- Rate limits for user-facing endpoints, refresh-token handling, account recovery and multi-factor policy remain identity-provider responsibilities or future integration work.
- Tests validate token-verification composition and request schemas; they do not prove a live OIDC provider or MariaDB transaction under concurrency.
