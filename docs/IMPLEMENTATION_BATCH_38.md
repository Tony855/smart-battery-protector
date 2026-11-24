# Implementation Batch 38 — Qualification timer bounds

Date: 2026-11-24

## Findings and changes
- Controller configuration validation previously enforced minimum qualification times but no maximum for direct callers, despite the persisted-record validator bounding them at 600,000 ms.
- Voltage-classifier API previously accepted zero and arbitrary large stability intervals, including durations outside the documented settings range.
- Added consistent 1,000–600,000 ms bounds for low-voltage/recovery controller qualification and classifier stability qualification.
- Invalid classifier timing clears the active candidate and returns UNKNOWN; no class is locked from an invalid timing input.
- Added regression tests for invalid duration values, fail-closed controller configuration and valid boundary values.

## Verification boundary
These are portable host regression tests. CI is required to confirm this commit. They do not validate timing against a physical vehicle, analog front end, engine-state signal or actuator. The voltage classification windows remain preliminary.
