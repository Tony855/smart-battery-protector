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
## Device telemetry payload
The signed device telemetry endpoint is POST /api/v1/device/telemetry.
- battery_voltage_v: volts (V), decimal number.
- battery_current_a: amperes (A), signed decimal number.
- temperature_deci_c: integer count of 0.1°C; 253 means 25.3°C.
- observed_at must include a timezone.
Telemetry never authorizes or triggers power-stage actuation.
