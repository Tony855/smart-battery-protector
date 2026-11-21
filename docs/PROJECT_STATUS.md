# Project Status — 2026-11-20

## Requirements baseline
- 12V/24V automatic recognition target; current voltage windows remain preliminary.
- Separate main-power and auxiliary-power product variants.
- BLE base; BLE + Wi-Fi/4G connectivity is a product target, not yet implemented end-to-end.
- PostgreSQL 15+ is the only supported application database.
- Telemetry units: voltage V, current A, temperature integer 0.1°C.

## Implemented in repository
- PostgreSQL schema/migrations 001–009, explicit migration runner, backend service, OIDC user authentication, owner/member-scoped device APIs, Ed25519-signed device event/telemetry ingestion, Redis rate limiting and replay protection.
- Remote OIDC JWKS, PostgreSQL and Redis transports enforce HTTPS / verify-full / rediss with certificate verification; loopback development endpoints remain supported.
- GitHub Dependabot configuration and a pip-audit CI gate monitor GitHub Actions, Docker images and Python dependencies.
- Partial unique indexes protect active device/user bindings and the single active owner invariant. Migration 009 does not delete duplicate legacy rows; it will stop if duplicates need reconciliation.
- One-time device claim-code provisioning stores only a SHA-256 digest and uses the same TLS-enforcing database factory as the API. Device Ed25519 key generation, secure-element injection and public-key enrollment workflow remain unimplemented.
- Portable C controller core with monitor-only defaults, low-voltage qualification, recovery delay, engine interlock, fault lock and configuration validation.
- INA228 voltage/shunt conversion and TMP117 temperature conversion to 0.1°C. INA228 signed shunt ADC rail codes are rejected as saturated/invalid rather than exposed as plausible clipped current.
- 12V/24V classification helper: 10-second qualification, locked until restart; classification windows still require vehicle-envelope validation.
- ESP32-C6 ESP-IDF monitor-mode application: I2C sensor identity/configuration checks, read-only BLE telemetry and boot diagnostics. Physical actuator output remains unimplemented and protection remains OFF in engineering defaults.
- 4 MiB ESP32-C6-MINI-1-H4 partition map with two equal 1,856 KiB OTA slots. Latest successful firmware workflow run before this audit was 44074491646 on commit 8cc7513d1c61af4972434fd5700cc45c3ae6021f: host tests, ESP-IDF build, 4 MiB partition validation, 666,800-byte app image (35.1% of the 1,900,544-byte OTA slot), safe-default checks and artifact upload all passed.
- NVS dual-slot journal, generation ordering, CRC validation, commit read-back, legacy read-only fallback and host power-loss/corruption regression tests.
- Rev A BOM, connector pinout, functional schematic description, SVG concept and KiCad mechanical floorplan template.

## Current audit findings / work in progress
- The 2026-11-20 full-repository audit batch is being maintained in PR #8 on branch `audit/2026-11-20-safety-hardening`; the PR is intentionally not merged automatically.
- Current main head at audit start was cc309fa69e49dab4ca53a8c71ee8c73524bcb95c. It had no check-runs or commit statuses attached; latest successful firmware CI run was on the preceding commit above.
- Main branch protection is not enabled. There were no open PRs and only main branch existed at audit start.
- Audit PR #8 adds engine-state rechecks for already-disconnected/recovery states, fail-closed enum validation, INA228 saturation rejection, bounded request-body streaming, canonical device-signature checks, explicit Ed25519 credential algorithm checks, remote TLS enforcement, unique active-membership indexes, TMP117 temperature-range alignment, OpenAPI/runtime parity tests and BOM corrections.
- Migration 008 adds a NOT VALID temperature check: new telemetry writes are constrained immediately, but existing rows are not rewritten or scanned. Review legacy out-of-range rows before manually validating it.
- Migration 009 adds partial unique indexes without deleting data. Check for duplicate active (device,user) bindings and duplicate active owners before applying it to any existing database; reconcile duplicates manually under an approved data-change procedure.
- Native KiCad electrical schematic, real footprints, routed copper, ERC/DRC, Gerbers and drill files are not released.
- Automotive input power supply, reverse-polarity and load-dump protection, exact regulator, shunt/rating, voltage-sense front end, isolation circuits and external actuator driver remain open.
- Secure Boot, Flash Encryption, NVS Encryption, signed OTA runtime, rollback, anti-rollback and eFuse provisioning remain disabled/not implemented. Partition table is a reservation only.
- MQTT has a contract draft only; no broker, ACL, TLS client, offline queue or cloud command implementation is present.
- Mobile, WeChat Mini Program and admin console directories contain scope/README documents only; application code is not implemented.
- Physical NVS power-loss/endurance, HIL, vehicle, environmental, EMC, fault-injection, thermal and certification tests have not been executed.

## Critical safety boundaries
- Current firmware is monitor-only; no physical actuator output is implemented.
- Main-power switching must never be requested while engine state is RUNNING or UNKNOWN.
- Engine and actuator validity inputs require isolated conditioning and external fail-low hardware.
- No starter-current or high-current power path is routed through the Rev A controller PCB.
- No current threshold is approved until the shunt and analog measurement chain are selected and calibrated.
- No prototype is approved for installation on a road vehicle.

## Release rule
Do not claim automotive suitability, current rating, safety certification, production readiness, OTA readiness or vehicle compatibility without objective design and verification evidence.


## Batch 21 — CI closure (2026-11-21)
- Latest PR head `3942febc48b50e836254835e890fb7a6394e0765` passed Host safety gate run 44851079744, Backend service run 44851079852 and Firmware run 44851079685.
- Latest firmware run completed ESP-IDF build, OTA slot-size check, safe commissioning defaults and artifact upload. Artifact `sbp-esp32c6-firmware` size 419,667 bytes; GitHub reported SHA-256 `5332088ce589eb62e1b19debe512271db343df4939c4b4a5c4bc3744e93aa4f5`.
- This evidence is CI-only; it does not establish hardware, HIL, vehicle or production validation.
- See `docs/IMPLEMENTATION_BATCH_21.md` for detail.


## Batch 22 — latest-head review (2026-11-21)
- Latest PR head reviewed: `99aec71b3bedbaef174daee1c9fa45a120cecfbf`.
- Host safety and backend workflows succeeded (runs 44854427466 and 44854427543). Firmware run 44854427559 had completed host tests, partition/BLE validation and native C build/test; ESP-IDF build was still in progress at review time. OTA-slot, safe-default and artifact-upload steps had not yet run; no artifact was listed for this run.
- Additional finding: telemetry `observed_at` is timezone-aware but has no explicit age/future-skew policy tied to authenticated request/server receive time. Do not enforce arbitrary limits until device clock trust, offline buffering and synchronization contract are specified. See `docs/IMPLEMENTATION_BATCH_22.md`.
- PR #8 remains open and unmerged. No hardware/HIL/vehicle/EMC/certification, production OTA, eFuse or production encryption validation is claimed.
