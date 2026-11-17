# ESP32-C6 secure provisioning and OTA lifecycle

Status: architecture proposal only. No security eFuse has been programmed, no production signing key has been generated, and no Secure Boot, Flash Encryption, NVS Encryption or OTA feature is enabled by this document.

Target software baseline: ESP-IDF 5.4.x, ESP32-C6.

## 1. Security goals

1. Only firmware signed by an authorized release key may boot or be installed.
2. Off-chip flash contents and device-specific NVS data are confidential at rest.
3. Every device receives a unique flash-encryption key; fleet-wide shared encryption keys are prohibited.
4. A device must recover from a failed OTA image without accepting an older vulnerable security version.
5. Production signing keys never enter the Git repository, developer workstation images, ordinary CI secrets or downloadable build artifacts.
6. A firmware update must never enable the battery disconnect output. The current product firmware remains monitor-only until the independent hardware safety chain is released.

## 2. Proposed production profile

| Area | Proposed policy | Not enabled yet |
|---|---|---|
| Boot authenticity | ESP32-C6 Secure Boot v2, RSA-PSS signing profile | Yes |
| Flash confidentiality | Flash Encryption, Release mode, unique per-device key | Yes |
| NVS confidentiality | NVS Encryption using the Flash-Encryption-based key-protection scheme and an NVS key partition | Yes |
| OTA authenticity | Secure-Boot-signed application image plus authenticated HTTPS transport | Yes |
| OTA recovery | Two OTA application slots, OTA metadata and first-boot health confirmation | Yes |
| Anti-rollback | ESP-IDF application anti-rollback with a controlled security-version policy | Yes |
| Signing key custody | Offline HSM or isolated signing service; separate key custody and audit | Yes |
| BLE diagnostics | Read-only, no secrets; no firmware update or control commands | Existing diagnostics only |

ESP32-C6 Secure Boot v2 supports RSA-PSS or ECDSA signatures and verifies the second-stage bootloader and application images. RSA is the proposed default because Espressif documents faster verification; final selection must be frozen with the production bootloader and signing infrastructure.

## 3. Partition layout requirements

The production partition table must be designed before enabling security features. The intended logical layout is:

- NVS data partition for configuration and device settings.
- NVS key partition with data type, NVS-keys subtype, encrypted flag and the ESP-IDF-required minimum size.
- OTA metadata partition.
- OTA application slot 0.
- OTA application slot 1.
- Optional encrypted manufacturing/service data only if a concrete requirement and access policy exist.

The exact offsets and sizes are deliberately not assigned here. They depend on the selected flash capacity, secure-boot image padding/signature overhead, bootloader growth, application growth, NVS wear budget and future OTA payload size. The final table must be checked against the actual signed image sizes.

If application anti-rollback is enabled, do not include factory or test application partitions; ESP-IDF documents that these partition subtypes are unsupported by its anti-rollback scheme. The OTA slot layout and recovery strategy must be tested together.

## 4. Key hierarchy and custody

### Firmware signing keys

- Generate production private keys on an isolated, high-entropy system or in an HSM.
- Keep private signing keys out of Git, normal CI, build artifacts and device flash.
- Store public-key digests in the supported ESP32-C6 eFuse slots during controlled manufacturing.
- Plan key rotation before provisioning. ESP32-C6 Secure Boot v2 supports up to three public-key digests; the factory bootloader must be signed with every key intended to remain usable over the device lifetime because the second-stage bootloader is not OTA-upgradeable.
- Keep at least one rotation/recovery key under separate custody. Never revoke the currently required key until the new-key-signed application and boot path have been validated on a representative device population.
- Record key ID, digest, signing event, firmware hash and provisioning station identity in manufacturing records. Never record private key material.

### Flash-encryption keys

- Generate a different flash-encryption key for every device.
- Provision and protect the key in the ESP32-C6 eFuse key block using the approved manufacturing station.
- Do not use one host-generated key for the whole fleet.
- Verify that the release-mode and download-mode policy is correct before irreversible eFuse changes.

### NVS encryption keys

- Prefer the ESP-IDF NVS Encryption scheme protected by Flash Encryption for this production profile.
- Add the required NVS key partition to the final partition table and protect that partition with Flash Encryption.
- Do not treat the current record CRC32 as authentication. CRC32 detects accidental corruption; NVS encryption is a separate protection layer.
- NVS encryption does not prevent an attacker from erasing flash. Recovery and re-provisioning must handle erased or missing NVS without automatically activating unsafe defaults.

## 5. OTA transaction and rollback policy

1. Device receives a signed release manifest over authenticated HTTPS. The manifest identifies product variant, hardware revision, firmware version, security version, image size, digest and release ID.
2. Device checks compatibility, available OTA slot capacity and anti-rollback eligibility before writing.
3. Firmware image is written only to the inactive OTA slot. The active slot is not erased during download.
4. Image signature is verified by the ESP-IDF Secure Boot chain; transport TLS is defense in depth, not a replacement for image signing.
5. Bootloader selects the new slot and marks it pending verification.
6. On first boot, firmware runs bounded health checks: boot diagnostics, NVS read, sensor identity/configuration, watchdog health and stable task startup. No actuator output is enabled.
7. Only after all required checks pass does the application mark the new image valid and cancel rollback.
8. If the new image crashes, resets unexpectedly or fails required checks before confirmation, leave it unconfirmed so the bootloader can roll back to the previous valid slot.
9. Increase the eFuse security version only as part of a deliberate vulnerability-removal release after the replacement image has passed field validation. Do not increment it for ordinary feature releases.
10. Verify that the fallback slot has a security version acceptable to the eFuse anti-rollback state before committing any security-version increase.

ESP-IDF anti-rollback uses a limited eFuse security-version field (documented as up to 16 bits in the selected ESP-IDF generation). The rollback plan must account for this finite budget and the rule that rollback cannot select an image below the programmed security version.

## 6. Manufacturing sequence and irreversible gates

Do not run a generic script that burns eFuses automatically. Each operation requires an approved device-specific work order and an operator confirmation.

1. Verify exact ESP32-C6 module/SoC revision, flash size, board revision and partition-table hash.
2. Program and verify the unsigned engineering image on an unprovisioned sample.
3. Validate the signed bootloader and application on a sacrificial engineering unit.
4. Validate the complete OTA update, first-boot confirmation and rollback sequence with power interruption.
5. Generate or retrieve the unique device flash-encryption key through the controlled station.
6. Provision NVS encryption material and verify encrypted NVS read/write/recovery.
7. Program the approved Secure Boot public-key digest set and verify signatures.
8. Enable Flash Encryption in Release mode and the approved secure download/debug restrictions.
9. Apply only the reviewed eFuse write/read protections; capture a post-provisioning eFuse summary.
10. Verify signed boot, encrypted flash, encrypted NVS, BLE read-only diagnostics, OTA success, OTA rollback and recovery behavior.
11. Seal the unit and record serial number, board revision, firmware hash, key IDs/digests, security-version state, provisioning operator and test evidence.

Any incorrect eFuse programming may permanently lock out recovery or prevent future firmware updates. Never perform first-time release provisioning on the only prototype or on a device connected to a vehicle.

## 7. CI and repository rules

- CI may build unsigned engineering binaries while security is not enabled.
- CI must never upload private signing keys, flash-encryption keys, NVS encryption keys or provisioning tokens.
- Production signing must occur in a separate protected signing system or HSM workflow after build artifact digest approval.
- Signed artifacts must be traceable to source commit, toolchain version, partition-table hash, build configuration and signer key ID.
- Security configuration changes require review of the bootloader, partition table, OTA code, NVS adapter, manufacturing instructions and recovery process as one change set.
- Do not enable a security Kconfig option in the current default build until the manufacturing and recovery gates above are approved.

## 8. Required verification before production

- Secure Boot rejects unsigned, incorrectly signed and modified bootloader/application images.
- Flash Encryption Release mode blocks the prohibited plaintext download paths while the approved recovery path still works.
- NVS encryption protects configuration and key material; erased/corrupt NVS remains a safe monitor-only boot.
- OTA rejects wrong product, wrong hardware revision, invalid signature, invalid digest, truncated image and lower security version.
- Power interruption during download, slot selection and first boot leaves at least one valid bootable image.
- Failed first-boot health checks trigger rollback; a successful update is confirmed only after all mandatory checks.
- Key rotation and key revocation are tested on representative devices before production use.
- Secure provisioning, service recovery and RMA procedures are reviewed by an independent security engineer.

## 9. Current project status

The current firmware does not implement OTA, Secure Boot provisioning, Flash Encryption provisioning or NVS Encryption. It uses CRC32-protected dual-slot NVS records and read-only BLE telemetry/diagnostics. The device remains monitor-only, and all production security settings remain disabled.

## 10. Espressif references (ESP-IDF 5.4)

- Secure Boot v2 for ESP32-C6: https://docs.espressif.com/projects/esp-idf/en/release-v5.4/esp32c6/security/secure-boot-v2.html
- Flash Encryption for ESP32-C6: https://docs.espressif.com/projects/esp-idf/en/release-v5.4/esp32c6/security/flash-encryption.html
- NVS Encryption: https://docs.espressif.com/projects/esp-idf/en/release-v5.4/esp32/api-reference/storage/nvs_encryption.html
- NVS library for ESP32-C6: https://docs.espressif.com/projects/esp-idf/en/release-v5.4/esp32c6/api-reference/storage/nvs_flash.html
- OTA and anti-rollback for ESP32-C6: https://docs.espressif.com/projects/esp-idf/en/release-v5.4/esp32c6/api-reference/system/ota.html
- Security feature enablement workflows for ESP32-C6: https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32c6/security/security-features-enablement-workflows.html
