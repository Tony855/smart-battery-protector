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


## Batch 23 — telemetry time provenance contract (2026-11-21)
- Added `docs/IMPLEMENTATION_BATCH_23.md` defining separate device observation time, server receipt time and per-device sample sequence.
- The current API still accepts timezone-aware device `observed_at` without age/future-skew enforcement; this remains an explicit open gap, not a completed safeguard.
- Enforcement is deferred pending approval of trusted time source/uncertainty, offline retention, sequence persistence/reset/wrap behavior and handling of unsynchronized devices.
- No behavior-changing migration or API change was made. See Batch 23 for the test matrix and decision list.


## Batch 25 — NVS generation exhaustion and firmware CI closure (2026-11-21)
- Added a host regression test proving that a stored `UINT32_MAX` generation remains loadable and a wrapped generation-zero save is rejected; ordinary save does not silently reset or wrap the journal.
- Latest pre-batch PR head `a3363d4be122a03bda7e74fca95f5b3105d19712` passed Host safety gate run 44854864027, Backend service run 44854864140 and Firmware portable core run 44854864039. The latter completed ESP-IDF build, OTA-slot size validation, safe commissioning defaults and artifact upload.
- A second firmware run 44854854626 also completed all listed steps successfully.
- Artifact `sbp-esp32c6-firmware` from run 44854864039 was 419,663 bytes, SHA-256 `7cf7574bc6edecf720ba66bbe7ecd377e4f508882ac47cbdfed48f244acf074a`.
- These are CI-only results; physical flash, NVS power-cut/endurance, HIL, vehicle, EMC and certification remain untested. See `docs/IMPLEMENTATION_BATCH_25.md`.

## Batch 26 — NVS write fault injection and MQTT contract review (2026-11-21)
- Extended the NVS host mock with one-shot `nvs_set_blob` failure injection and added a regression test proving a failed alternate-slot write leaves the previous valid generation readable; retry succeeds.
- Reviewed `protocol/MQTT_CONTRACT.md`: TLS, per-device credentials/ACL, QoS 1 idempotency and retained-command prohibition are contract requirements only. Broker/client implementation, credential lifecycle, deny-by-default ACL tests, replay persistence, clock/expiry policy and outage behavior remain open.
- New head CI must complete before the NVS test change is marked validated. Mock tests are not physical flash power-cut/endurance evidence. See `docs/IMPLEMENTATION_BATCH_26.md`.


## Batch 27 — NVS read and verification fault coverage (2026-11-22)
- Added host mock fault injection for NVS blob size-query and data-read failures; load/save fail closed and tests assert the prior journal remains intact.
- Added post-commit verification-read failure test, documenting that an error can be returned after a durable commit; re-read is required to resolve the outcome before retrying.
- Latest pre-batch head `e35c529acd9b392fb9150aea8ddbbdae9d73bcb9` passed host safety, backend, and firmware/ESP-IDF CI. Firmware artifact from run 44855793708: 419,664 bytes, digest `58756ed4a874177cbe3d17a10d8dfedc18a9c1778331300b774cd16f48dec13e`.
- New Batch 27 commits must complete their own CI before these tests are considered validated. Physical flash power-cut/endurance and vehicle/HIL testing remain unverified.
- See `docs/IMPLEMENTATION_BATCH_27.md`.
