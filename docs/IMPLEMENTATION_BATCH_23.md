# Implementation Batch 23 — Telemetry time provenance contract (2026-11-21)

## Scope
This batch defines a non-enforcing design contract for telemetry time provenance. It intentionally does not change ingestion acceptance behavior or database schema until device clock and offline-buffer requirements are approved.

## Finding confirmed in current implementation
- `TelemetrySample.observed_at` is timezone-aware at the route boundary.
- Device requests are authenticated with a signed request timestamp and replay nonce.
- The ingestion row stores the device-provided `observed_at`, but does not persist an independent server `received_at` timestamp or a device sequence counter.
- Consequently, the backend cannot reliably distinguish delayed offline samples from a device clock that is wrong or maliciously far in the future. Sorting only by `observed_at` can misrepresent freshness.

## Proposed telemetry time model
Every accepted sample should carry three independent provenance values:
1. `observed_at`: device wall-clock time when the measurement was sampled; informational until the device clock is synchronized.
2. `received_at`: server-generated UTC timestamp captured at ingestion; authoritative for arrival ordering and backend receipt freshness.
3. `sample_sequence`: monotonically increasing unsigned per-device counter, persisted across reboot; authoritative for device-local sample ordering when available.

The authenticated request timestamp is a fourth value: it proves request freshness under the device-auth protocol, but MUST NOT be silently substituted for sample time. A cached sample may be transmitted later in a newly signed request.

## Required device-time states
- `synchronized`: device has a trusted time source and reports its synchronization state.
- `unsynchronized`: device clock has no trustworthy epoch; it must not invent a UTC observation time. A monotonic uptime/sample counter may still be reported.
- `recovered`: device has regained trusted time after an unsynchronized interval; old buffered samples retain their original provenance and must not be rewritten to appear newly observed.

The exact source of trusted time (authenticated network time, secure RTC provisioning, or another approved mechanism), its uncertainty, and how it survives reboot remain open engineering decisions.

## Acceptance and freshness rules to implement only after approval
- Always stamp `received_at` on the server; never accept a device-supplied value for it.
- Preserve the original `observed_at`; never overwrite it with receive time.
- Enforce a maximum future skew only when the device reports synchronized time and the permitted clock uncertainty is defined.
- Define a bounded offline retention period. Expired buffered telemetry may be rejected or retained in a separately marked archival path; it must not silently become current telemetry.
- Use `sample_sequence` to detect duplicate, replayed, missing and out-of-order samples. Define wraparound and factory-reset behavior before making it mandatory.
- Freshness APIs and dashboards must use server receipt time plus synchronization/sequence metadata, not just `MAX(observed_at)`.
- A duplicate sample identifier remains idempotent; conflicting payload reuse of an identifier should be observable as an integrity event rather than silently reported as an ordinary duplicate.

## Required test matrix
- Correctly synchronized sample arriving immediately.
- Correctly synchronized sample delivered after an offline interval within retention.
- Sample older than the approved retention period.
- Device wall clock far in the future and far in the past.
- Unsynchronized device with no valid epoch.
- Clock jumps forward/backward after synchronization recovery.
- Duplicate identifier with identical payload and with conflicting payload.
- Sequence gaps, reordering, reboot persistence and defined wraparound.
- Server clock and device clock timezone/DST representation differences.

## Decisions still required
Before implementing enforcement, approve:
- trusted time source and synchronization uncertainty;
- maximum future skew;
- offline retention duration and expired-sample handling;
- sequence width, persistence, wrap/reset and factory-reset semantics;
- whether unsynchronized samples are accepted with null `observed_at` or held locally until time is trusted;
- database retention and audit policy for timestamp/sequence anomalies.

## Safety and validation boundary
This is a design-only batch. No migration, API behavior change, production data rewrite, device firmware time-sync implementation, HIL or vehicle validation was performed. Current API still requires timezone-aware `observed_at` and has no age/future-skew enforcement. This must not be interpreted as time-freshness protection being implemented.
