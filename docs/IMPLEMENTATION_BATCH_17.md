# Implementation Batch 17 — Device dashboard read APIs

## Delivered
- Added owner/member-scoped device status endpoint.
- Added paginated device event/fault history endpoint.
- Device status combines product identity, lifecycle, server-observed presence and the latest telemetry snapshot.
- Event history supports descending ID cursor pagination with a maximum page size of 200.
- Every query is scoped by the authenticated user's active device binding; callers cannot query arbitrary serial numbers.
- Added tests for unauthenticated access and invalid pagination bounds.
- API version advanced to 0.5.0.

## API
- `GET /api/v1/me/devices/{serial_number}/status`
- `GET /api/v1/me/devices/{serial_number}/events?limit=50&before_id=123`

## Notes
- The dashboard status is observational and does not prove that a device is safe to switch.
- Event cursor is a database row ID, not a timestamp; clients should pass the returned `next_before_id` as the next request's `before_id`.
- A full page may produce a cursor even when no later page exists; clients should stop when a page is empty.
- No power control endpoint is exposed.
