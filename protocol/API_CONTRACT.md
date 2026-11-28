# Implemented API Contract

Base prefix: `/api/v1`. The canonical OpenAPI document is `backend/openapi.yaml`.

## Device-signed ingestion
- `POST /api/v1/device/events` — Ed25519-signed event ingestion; 16 KiB raw-body limit.
- `POST /api/v1/device/telemetry` — Ed25519-signed observational telemetry; 8 KiB raw-body limit.

Device signatures bind the key ID, Unix timestamp, nonce, uppercase method, exact path plus raw query string, and SHA-256 digest of the exact raw request body. The server verifies an active Ed25519 public-key credential, applies a per-key Redis rate limit, and claims the nonce in Redis only after signature verification.

## User/account APIs
- `GET /api/v1/me/devices`
- `POST /api/v1/me/devices/bind`
- `GET /api/v1/me/devices/{serial_number}/members`
- `POST /api/v1/me/devices/{serial_number}/members`
- `DELETE /api/v1/me/devices/{serial_number}/members/{member_subject}`

These routes require an OIDC bearer token. Owners can add admins/viewers; admins can add/remove viewers only.

## Owner/member-scoped read APIs
- `GET /api/v1/me/devices/{serial_number}/status`
- `GET /api/v1/me/devices/{serial_number}/events?limit=50&before_id=123`
- `GET /api/v1/me/devices/{serial_number}/telemetry?limit=100`

## Operations
- `GET /health/live`
- `GET /health/ready`

## Units and validation
- `battery_voltage_v`: volts (V), up to 0.001 V resolution.
- `battery_current_a`: signed amperes (A), up to 0.001 A resolution.
- `temperature_deci_c`: integer count of 0.1°C; 253 means 25.3°C. Accepted TMP117 range is -550 through +1500 deci-°C (-55.0°C to +150.0°C).
- `system_voltage_class`: 12, 24, or null when classification is UNKNOWN.
- Device timestamps must include a timezone.

Telemetry and events are observational. They do not authorize or trigger power-stage actuation.

## Not implemented
Cloud power commands, remote configuration writes, firmware-release download/OTA, generic `/devices/{deviceId}` routes, and MQTT broker/client integration are not exposed by the current service. Do not build clients against those earlier draft routes.
