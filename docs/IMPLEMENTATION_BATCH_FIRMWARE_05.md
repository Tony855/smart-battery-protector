# Firmware implementation batch 05 — ESP32-C6 4 MiB partition foundation

Date: 2026-11-17

## Delivered

- Confirmed the selected Rev A BOM controller module is ESP32-C6-MINI-1-H4 with 4 MiB flash.
- Added a custom 4 MiB partition map with NVS, OTA metadata, an encrypted-flag NVS key reservation, PHY data, two equal OTA application slots and a reserved storage partition.
- Selected two 1,856 KiB application slots. The map ends exactly at 4 MiB and contains no factory app partition.
- Configured ESP-IDF defaults to use the custom table and 4 MiB flash profile.
- Added a static partition validator for exact labels/types/subtypes/offsets/sizes, alignment, overlap, flash boundary, OTA slot symmetry, NVS key flag and factory-partition exclusion.
- Added a post-build check that the engineering application binary fits in one OTA slot.
- Added OTA HIL plan cases for interrupted inactive-slot writes, first-boot rollback and anti-rollback rejection.
- Added a 30-minute CI job timeout and made the partition validator run for push and pull-request builds.

## Verification

- Local execution of the partition validator passed against the committed CSV: two equal 1,900,544-byte OTA slots, no overlaps and 4 MiB boundary respected.
- ESP-IDF parsing/build of the custom partition table, generated sdkconfig checks and actual application image-size check are pending the latest GitHub Actions run. An earlier pre-partition firmware build succeeded but exposed the old 2 MiB flash default; the current sdkconfig now explicitly selects 4 MiB. A later run was cancelled during ESP-IDF build by a newer push. The safe-default gate exposed that ESP-IDF hides the anti-rollback Kconfig symbol unless its parent feature is enabled; the guard now treats an absent symbol as disabled but still rejects any explicit enabled value. Its regex was separately tested against both absent and explicitly enabled anti-rollback settings.
- No OTA runtime, image download, signature verification, boot-slot selection, rollback, Secure Boot, Flash Encryption, NVS Encryption or eFuse provisioning has been enabled.
- No hardware flashing, HIL or vehicle test has been performed.

## Safety boundary

The two OTA slots and NVS key partition are storage reservations only. The current firmware remains monitor-only; the encrypted partition flag does not enable encryption by itself. Never provision production eFuses using this engineering layout without validating the signed bootloader, signed image size, key recovery, power-loss behavior and exact flash hardware.

## Next engineering batch

1. Confirm ESP-IDF 5.4 accepts the custom partition table and the generated 4 MiB sdkconfig defaults.
2. Record actual engineering image size and remaining OTA slot headroom from CI.
3. Implement an OTA state machine only after defining signed manifest format, trust-anchor handling, transport authentication, inactive-slot writes and boot confirmation/rollback.
4. Add host-testable OTA policy logic before enabling any device update path.
