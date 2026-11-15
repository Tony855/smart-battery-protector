# API Contract Draft

Prefix: `/api/v1`

- `POST /auth/session`
- `POST /devices/bind`
- `DELETE /devices/{deviceId}/binding`
- `GET /devices`
- `GET /devices/{deviceId}`
- `GET /devices/{deviceId}/events`
- `GET /devices/{deviceId}/firmware`
- `POST /devices/{deviceId}/commands`
- `GET /models/{modelId}/protection-profile`

Cloud commands never bypass the device-local safety state machine. Production contract must add OpenAPI schema, authorization matrix, audit trail, rate limits, idempotency and error codes.