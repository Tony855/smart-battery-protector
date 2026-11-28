# Firmware implementation batch 05 — ESP32-C6 4 MiB partition foundation

Date: 2026-11-17

## Delivered
- Confirmed the selected Rev A BOM controller module is ESP32-C6-MINI-1-H4 with 4 MiB flash.
- Added a custom 4 MiB partition map with NVS, OTA metadata, an encrypted-flag NVS key reservation, PHY data, two equal OTA application slots and reserved storage.
- Selected two 1,856 KiB application slots. The map ends exactly at 4 MiB and contains no factory app partition.
- Configured ESP-IDF defaults to use the custom table and 4 MiB flash profile.
- Added a static partition validator for exact labels/types/subtypes/offsets/sizes, alignment, overlap, flash boundary, OTA slot symmetry, NVS key flag and factory-partition exclusion.
- Added a post-build check that the engineering application binary fits in one OTA slot.
- Added OTA HIL plan cases for interrupted inactive-slot writes, first-boot rollback and anti-rollback rejection.
- Added a 30-minute CI job timeout and made the partition validator run for push and pull-request builds.

## Verification
- Successful GitHub Actions run [44074491646](https://github.com/Tony855/smart-battery-protector/actions/runs/44074491646), commit `8cc7513d1c61af4972434fd5700cc45c3ae6021f`: host CMake tests, partition validation, ESP-IDF v5.4 build, app-slot size gate, safe commissioning defaults and firmware artifact upload all passed.
- Built application image: 666,800 bytes of 1,900,544 bytes (35.1%); 1,233,744 bytes of slot capacity remained at that build.
- Earlier run 44073280227 failed at the safe-default verifier because ESP-IDF omitted the hidden anti-rollback Kconfig symbol while the script expected a visible unset line. The guard was corrected to accept an absent hidden symbol but still reject explicit enablement; run 44074491646 then passed.
- Current main head advanced to cc309fa after the successful run, so that exact head did not have check-runs attached at the start of the 2026-11-20 audit. The current audit PR must be validated independently.
- No OTA runtime, image download, signature verification, boot-slot selection, rollback, Secure Boot, Flash Encryption, NVS Encryption or eFuse provisioning has been enabled.
- No hardware flashing, HIL or vehicle test has been performed.

## Safety boundary
The two OTA slots and NVS key partition are storage reservations only. The encrypted partition flag does not enable encryption by itself. Never provision production eFuses using this engineering layout without validating the signed bootloader, signed image size, key recovery, power-loss behavior and exact flash hardware.

## Next engineering batch
1. Complete audit PR CI for the current source head.
2. Continue host-testable safety and fault-injection coverage.
3. Implement OTA policy only after defining signed manifest format, trust-anchor handling, transport authentication, inactive-slot writes and boot confirmation/rollback.
