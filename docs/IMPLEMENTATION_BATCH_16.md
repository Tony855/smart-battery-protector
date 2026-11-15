# Implementation Batch 16 — Device presence and membership roles

## Delivered
- Added migration 006 with `devices.last_seen_at` and an index for presence queries.
- Accepted signed device events and telemetry update server-side last-seen time; device-provided clocks are not used for online status.
- Device list now returns last-seen timestamp and a 90-second online/offline classification.
- Added owner/admin member listing, member addition and membership revocation.
- Role policy: owner may add admin/viewer; admin may add/remove viewer only; viewer cannot manage members; owner binding cannot be revoked through member management.
- Added strict role allowlist tests to prevent privilege escalation.

## API additions
- `GET /api/v1/me/devices/{serial_number}/members`
- `POST /api/v1/me/devices/{serial_number}/members`
- `DELETE /api/v1/me/devices/{serial_number}/members/{member_subject}`

## Security and product boundaries
- These are account-level data permissions only. No remote switching or configuration-write capability is enabled.
- Presence means the server received a valid signed device event or telemetry within the last 90 seconds. It is not a guarantee that the physical device is healthy or reachable for commands.
- Owner transfer, owner self-removal, device resale/reset workflows and user notification are not implemented yet.
- Live database concurrency tests and identity-provider integration remain required before production.
