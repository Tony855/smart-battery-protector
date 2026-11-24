# Project Status — 2026-11-23

## Requirements baseline
- 12V/24V automatic recognition target; operating windows remain preliminary pending vehicle-envelope evidence.
- Separate main-power and auxiliary-power product variants.
- BLE base; BLE + Wi-Fi/4G connectivity remains a product target, not an end-to-end implementation.
- PostgreSQL 15+ is the supported application database.
- Telemetry units: voltage V, current A, temperature integer 0.1°C.

## Implemented in repository
- PostgreSQL schema/migrations 001–009, explicit migration runner, backend service, OIDC user authentication, owner/member-scoped device APIs, Ed25519-signed device event/telemetry ingestion, Redis rate limiting and replay protection.
- Remote OIDC JWKS, PostgreSQL and Redis transports enforce HTTPS / verify-full / rediss with certificate verification; loopback development endpoints remain supported.
- GitHub Dependabot configuration and strict pip-audit CI gate.
- Partial unique indexes protect active device/user bindings and the single active owner invariant. Migration 009 does not delete duplicate legacy rows; it stops if duplicates require reconciliation.
- One-time device claim-code provisioning stores only a SHA-256 digest and uses the TLS-enforcing database factory. Device Ed25519 key generation, secure-element injection and public-key enrollment workflow remain unimplemented.
- Portable C controller core with monitor-only defaults, low-voltage qualification, recovery delay, engine interlock, fault lock and configuration validation.
- INA228 voltage/shunt conversion and TMP117 temperature conversion to 0.1°C. INA228 signed shunt ADC rail codes are rejected as saturated/invalid.
- 12V/24V classification helper: 10-second qualification, locked until restart; classification windows remain preliminary.
- ESP32-C6 ESP-IDF monitor-mode application: I2C sensor identity/configuration checks, read-only BLE telemetry and boot diagnostics. Physical actuator output is not implemented; protection remains OFF in engineering defaults.
- 4 MiB ESP32-C6-MINI-1-H4 partition map with two equal 1,856 KiB OTA slots.
- NVS dual-slot journal, generation ordering, CRC validation, commit read-back, legacy read-only fallback and host fault-injection regression tests for write/read/verification failures.
- Rev A BOM, connector pinout, functional schematic description, SVG concept and KiCad mechanical floorplan template.

## Branch / validation state
- main remains unchanged by the audit batches; no PR was merged.
- PR #8 is open/unmerged on audit/2026-11-20-safety-hardening. The current head SHA and CI state are reported in the daily audit, rather than hard-coded here.
- Main has no attached check runs/status contexts; PR checks do not imply main was validated.
- Branch protection and required checks remain absent on both visible branches.

## Audit batches
- Batch 27 added NVS size-query, data-read and post-commit readback failure injection. Host mocks are not physical flash power-cut evidence.
- Batch 28 added daily firmware, backend and host-safety schedules at 01:15, 01:20 and 01:25 UTC. Scheduled GitHub Actions runs only from the default branch; these schedules are not active until changes reach main.
- Batch 29 adds MQTT contract drift tests (topic, transport/ACL, command safety and unit assertions). It is contract testing only; MQTT runtime is absent.
- Batch 30 corrects BLE protocol documentation against actual short-key JSON/UUIDs and boot diagnostics; strengthens the schema/default validator and its workflow path triggers. BLE remains unsecured, read-only development telemetry.
- Batch 31 adds transactional audit rows to device-claim and member add/revoke operations, plus a unit test for audit metadata serialization. These audit rows commit with the corresponding mutation.


- Batch 32 expands host safety gate negative-case tests for invalid action enum, over-current and invalid actuator feedback (host-only evidence).
- Batch 33 expands sensor conversion boundary/invalid-input tests (host-only evidence).
- Batch 34 expands NVS mock regression coverage for identical-generation duplicates, truncated slots, corrupt legacy data and recovery behavior; physical flash tests remain unperformed.

- Batch 35 adds NVS mock post-commit CRC corruption injection and recovery tests; this remains host-model evidence only.

- Batch 36 adds controller low-voltage/recovery qualification timer rollover regression coverage across uint32 millisecond wrap (host-only).

- Batch 37 adds voltage-classifier stability timer wraparound regression coverage (host-only); classification windows remain preliminary.

## Current full-repository findings / remaining work
- Native KiCad electrical schematic, real footprints, routed copper, ERC/DRC, Gerbers and drill files are not released.
- Automotive input power supply, reverse-polarity and load-dump protection, exact regulator, shunt/rating, voltage-sense front end, isolation circuits and external actuator driver remain open.
- Secure Boot, Flash Encryption, NVS Encryption, signed OTA runtime, rollback, anti-rollback and eFuse provisioning remain disabled/not implemented. Partition table reservation and CI checks do not establish production OTA readiness.
- MQTT has a contract draft and contract tests only; no broker, ACL, TLS client, offline queue or cloud command implementation is present.
- Mobile, WeChat Mini Program and admin console directories contain scope/README documents only; application code is not implemented.
- BLE telemetry and boot diagnostics are currently unauthenticated and unencrypted; no BLE writes/commands exist. Commercial deployment requires an approved privacy/security design.
- Physical NVS power-loss/endurance, HIL, vehicle, environmental, EMC, thermal, certification and production tests have not been executed.

## Critical safety boundaries
- Current firmware is monitor-only; no physical actuator output is implemented.
- Main-power switching must never be requested while engine state is RUNNING or UNKNOWN.
- Engine and actuator validity inputs require isolated conditioning and external fail-low hardware.
- No starter-current or high-current power path is routed through the Rev A controller PCB.
- No current threshold is approved until the shunt and analog measurement chain are selected and calibrated.
- No prototype is approved for installation on a road vehicle.

## Release rule
Do not claim automotive suitability, current rating, safety certification, production readiness, OTA readiness or vehicle compatibility without objective design and verification evidence.
