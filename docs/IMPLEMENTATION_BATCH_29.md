# Implementation Batch 29 — MQTT contract checks

Date: 2026-11-22

This batch adds backend contract tests for the MQTT draft without implementing or enabling a broker, client, or command path.

- Checks the five documented device-scoped topic suffixes and rejects broad/global topic patterns in the draft contract.
- Checks TLS, per-device credential/ACL requirements, rejection of expired/duplicate/unauthorized/schema-invalid commands and prohibition on retained power-control commands.
- Checks that transport delivery is not treated as actuation and that the local firmware safety gate remains authoritative.
- Checks telemetry units and 12V/24V classification against the documented contract.

Validation: test code is committed at the PR head. CI at head 50917e2712fb8ceb7c1d7ebbeacf37bcd0fa0b63 completed backend tests, host-safety tests and firmware build/checks successfully.

Limitations: contract tests are not runtime MQTT security evidence. Broker ACLs, TLS/client provisioning, integration, replay handling, offline queue and commands remain unimplemented.
