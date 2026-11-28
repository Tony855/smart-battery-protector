# Implementation Batch 26 — NVS write fault injection and MQTT security gap review

Date: 2026-11-21

## NVS host-test improvement
- Added a one-shot `nvs_set_blob` failure injection hook to the NVS mock.
- Added a regression test that seeds generation 50, forces the next blob write to fail, and verifies the previous generation remains readable and the alternate slot is not spuriously created.
- The test then retries the same generation 51 save successfully.
- Existing commit-failure and generation-exhaustion tests remain in place.

## MQTT contract security review
Reviewed `protocol/MQTT_CONTRACT.md`. It remains a contract draft, not an implemented broker/client. The current draft states TLS, per-device credentials, per-device topic ACL, QoS 1 idempotency, expiry/replay rejection and prohibition of retained power-control commands. These statements are requirements only; they are not evidence that a broker, device client, credential lifecycle or ACL enforcement exists.

Before implementation, the contract still needs explicit decisions and testable requirements for:
- Credential issuance, rotation, revocation and device identity binding.
- Broker-side deny-by-default ACL tests, including wildcard/topic traversal and cross-device publish/subscribe attempts.
- TLS minimum version, trust-anchor provisioning, hostname validation and certificate rotation behavior.
- Command authorization policy, canonical message signing or authenticated broker identity, maximum payload size and schema compatibility.
- Durable deduplication/idempotency storage across reboot and bounded replay cache behavior.
- Offline command queue policy, expiry clock trust, retained-message rejection and last-will handling.
- Rate limits, connection limits, audit logging, broker outage behavior and credential compromise response.
- Separation of telemetry-only topics from any future actuator command plane.

No MQTT broker/client, credentials, production ACL or command path was added in this batch.

## Validation status
- Previous head `ae330536877a51f391c3d633589daa72ff080d19`: host safety and backend workflows passed; firmware ESP-IDF build was still running when inspected.
- This batch changes the NVS mock and tests; the new head must pass host and firmware CI before these tests are considered validated.
- Mock-level failure injection does not model real flash page programming, erase interruption, brownout, wear, or power-cut atomicity.

## Safety boundary
- Firmware remains monitor-only; no physical actuator is enabled.
- No hardware, HIL, vehicle, EMC, environmental or certification test is claimed.
- PR #8 remains open and unmerged.
