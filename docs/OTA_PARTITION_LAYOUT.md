# ESP32-C6 4 MiB partition layout

Status: committed engineering partition map; OTA runtime, encryption and eFuse provisioning remain disabled.

## Hardware basis

Rev A BOM selects Espressif ESP32-C6-MINI-1-H4. The H4 module variant has 4 MiB flash. This layout is specific to the current H4 selection; changing module or flash size requires a new reviewed map and CI validation.

## Partition map

Partition table offset: 0x8000 (ESP-IDF default). Flash capacity: 0x400000 bytes.

| Name | Type / subtype | Offset | Size | Purpose |
|---|---|---:|---:|---|
| nvs | data / nvs | 0x9000 | 24 KiB | Existing dual-slot configuration journal |
| otadata | data / ota | 0xF000 | 8 KiB | Reserved OTA selection metadata; OTA code is not enabled |
| nvs_keys | data / nvs_keys | 0x11000 | 4 KiB | Reserved NVS encryption key partition; encryption is not enabled |
| phy_init | data / phy | 0x12000 | 4 KiB | PHY calibration data partition |
| ota_0 | app / ota_0 | 0x20000 | 1,856 KiB | First application slot |
| ota_1 | app / ota_1 | 0x1F0000 | 1,856 KiB | Second application slot |
| storage | data / spiffs | 0x3C0000 | 256 KiB | Reserved; current firmware does not mount a filesystem |

The map ends at 0x400000 exactly. OTA slots are equal-sized and 64 KiB aligned. The nvs_keys entry is marked encrypted for a future Flash Encryption profile; this flag does not enable Flash Encryption by itself.

## Release constraints

- No factory app partition is included. The planned anti-rollback profile requires OTA app slots and must not rely on a factory app partition.
- OTA metadata and slots are layout reservations only. Current firmware does not download, authenticate, install, select or roll back images.
- Secure Boot, Flash Encryption, NVS Encryption and anti-rollback remain disabled.
- The application image must fit in one OTA slot, including signature/padding added by a production build. CI checks engineering image size against the slot.
- The storage partition is reserved and unused. Do not store secrets there.
- Bootloader, partition table, application and any future NVS key partition must be tested together on the exact module and flash chip before provisioning.

## CI checks

The scripts/verify_partition_layout.py script checks expected labels, types, subtypes, offsets, sizes, alignment, equal OTA slot sizes, no overlaps, 4 MiB boundary, encrypted NVS key reservation and absence of a factory partition. With --app-bin it checks that the built image fits in an OTA slot.

Run from repository root:

~~~sh
python3 scripts/verify_partition_layout.py
python3 scripts/verify_partition_layout.py --app-bin firmware/esp-idf/build/sbp_esp32c6_controller.bin
~~~

This is a static layout and image-size gate, not proof of OTA reliability or flash hardware compatibility.
