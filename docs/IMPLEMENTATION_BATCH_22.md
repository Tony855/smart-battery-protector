# Implementation Batch 22 — Latest-head review and telemetry trust findings (2026-11-21)

## Repository / PR snapshot
- Repository default branch: `main`; visible branches: `main`, `audit/2026-11-20-safety-hardening`.
- Open PR: #8, base `main`, head before this documentation batch `99aec71b3bedbaef174daee1c9fa45a120cecfbf`.
- PR #8 currently reports open and mergeable=true. This is not approval to merge; it remains intentionally open.
- Main head remains `cc309fa69e49dab4ca53a8c71ee8c73524bcb95c` per the PR base metadata.
- Latest head combined commit statuses endpoint returned no status entries. Workflow runs are authoritative for the checks available through this integration.

## Latest-head workflow evidence (head 99aec71...)
- Host safety gate run 44854427466: completed successfully; host-tests job succeeded.
- Backend service run 44854427543: completed successfully; install, pip-audit, tests, OpenAPI YAML validation and API container build all succeeded.
- Firmware run 44854427559: host tests, partition validation, BLE schema validation, configure/build/test succeeded; ESP32-C6 ESP-IDF application build was still in progress at review time. OTA slot size, safe commissioning defaults and artifact upload had not yet run.
- No artifact was listed yet for run 44854427559. Do not reuse the older run's artifact as evidence for this head.

## Full-repository code review — additional finding
Reviewed the portable C controller and tests, backend telemetry ingestion, and Rev A hardware design statement.

### Telemetry time-trust gap (needs policy decision before code enforcement)
- Telemetry requires timezone-aware `observed_at`, and device requests have signed timestamps/replay protection, but ingestion does not currently enforce a maximum age/future-skew relationship between sample observation time and authenticated request time/server receive time.
- This can allow stale or future-dated samples to be accepted and affect history ordering / downstream freshness interpretation.
- Do not blindly reject samples using a hard-coded wall-clock window: device RTC accuracy, time synchronization, offline buffering and reconnect behavior need an explicit contract.
- Follow-up should define: trusted time source, allowed future skew, offline retention window, monotonic sequence fallback, duplicate handling and server receive timestamp. Add tests for old/future samples and clock-unsynchronized devices once policy is approved.

### Hardware and safety boundary reconfirmed
- Rev A is a low-voltage controller/sensor proposal only. External vehicle supply protection, power regulator, analog front-end, contactor driver and high-current path remain outside released design.
- Current firmware remains monitor-oriented with physical actuator output unimplemented. The controller unit tests do not establish external hardware fail-safe behavior.
- No hardware, HIL, vehicle, EMC, environmental or certification evidence was generated.

## Actions taken
- Recorded this batch as an engineering finding; no behavior-changing timestamp policy was guessed.
- No production database migration, secrets, key material, OTA, eFuse, encryption enablement, device flashing or merge was performed.

## Next priorities
1. Recheck firmware run 44854427559 until ESP-IDF build, slot-size, safe-default and artifact steps finish; investigate any failure from job logs.
2. Design telemetry time/freshness contract before enforcing age limits.
3. Add deterministic controller tests for all fault transitions and rollover boundaries.
4. Continue review of NVS journal power-loss semantics, MQTT implementation gap and hardware input protection design.
