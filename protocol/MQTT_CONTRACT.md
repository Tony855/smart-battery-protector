# MQTT Contract Draft v0.1

## Topic layout
- `sbp/v1/devices/{deviceId}/telemetry` — device publish
- `sbp/v1/devices/{deviceId}/events` — device publish
- `sbp/v1/devices/{deviceId}/commands` — authorized service publish
- `sbp/v1/devices/{deviceId}/command-results` — device publish
- `sbp/v1/devices/{deviceId}/config` — authorized service publish

## Envelope
Every message includes `schemaVersion`, `messageId`, `deviceId`, `sentAt`, and payload. Command messages additionally include `requestId`, `expiresAt`, and `action`.

## Rules
- TLS transport and per-device credentials.
- Broker ACL restricts each device to its own topics.
- Commands are QoS 1 at most; consumers must be idempotent.
- Expired, duplicate, unauthorized or schema-invalid commands are rejected.
- Retained messages must never be used to replay power-control commands.
- Cloud delivery means only that a request was transported, not that a relay/contactor moved.
- Device-local safety gate is authoritative; telemetry and command-result events report actual state separately.
