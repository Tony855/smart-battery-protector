# Project Status — 2026-11-22

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

## Latest verified GitHub state (2026-11-22)
- Default branch main: `cc309fa69e49dab4ca53a8c71ee8c73524bcb95c`.
- Audit branch: `audit/2026-11-20-safety-hardening`.
- PR #8 remains OPEN and UNMERGED; latest verified head at this update: `bc7d5324d92aff86493274c99e534b6f9d7bc742`.
- Latest PR head workflow runs 44972401774 (backend), 44972401765 (host safety), and 44972401724 (firmware) completed successfully.
- Firmware run 44972401724 completed host configure/build/test, ESP32-C6 ESP-IDF application build, OTA slot capacity validation, safe commissioning-default validation and artifact upload.
- Artifact `sbp-esp32c6-firmware`: 419,667 bytes; SHA-256 `83920fa6a96e7aa5959da1598c8a8e824e5aeee9746bc986a98afa5d9a41456e`.
- Main head currently has no commit status contexts/check runs attached; do not infer that main has passed the PR checks.
- Both visible branches are unprotected. PR #8 is mergeable but has not been merged.

## Current audit findings / work in progress
- Batch 27 added NVS size-query, data-read and post-commit readback failure injection. These are host-mock tests, not physical flash power-cut evidence.
- Batch 28 adds daily schedules to the firmware, backend and host-safety workflows at 01:15, 01:20 and 01:25 UTC respectively. GitHub scheduled workflows execute from the repository default branch; therefore these schedules are configured on this audit branch but will NOT become active until the workflow changes reach main. No PR merge was performed.
- Native KiCad electrical schematic, real footprints, routed copper, ERC/DRC, Gerbers and drill files are not released.
- Automotive input power supply, reverse-polarity and load-dump protection, exact regulator, shunt/rating, voltage-sense front end, isolation circuits and external actuator driver remain open.
- Secure Boot, Flash Encryption, NVS Encryption, signed OTA runtime, rollback, anti-rollback and eFuse provisioning remain disabled/not implemented. Partition table reservation and CI checks do not establish production OTA readiness.
- MQTT has a contract draft only; no broker, ACL, TLS client, offline queue or cloud command implementation is present.
- Mobile, WeChat Mini Program and admin console directories contain scope/README documents only; application code is not implemented.
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
