# Implementation Batch 35 — NVS post-commit CRC mismatch fault injection

Date: 2026-11-24

## Change
The NVS host mock now supports a deterministic corruption injection after a pending record is committed. The injection flips a CRC byte in the target durable mock record, allowing the read-back decoder to reject a CRC mismatch rather than only simulating a failed read.

The regression test verifies:
- Save returns an error when post-commit read-back detects a CRC mismatch.
- The previous valid slot remains loadable.
- The corrupt target can be replaced by a subsequent higher-generation save.
- The journal recovers to the newly validated generation.

## Verification boundary
This is mock fault injection only. It is not evidence of physical flash corruption, power-cut behavior, ESP-IDF NVS atomicity or flash endurance.
