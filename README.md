# Smart Battery Protector

Automotive smart battery disconnect/protection platform. Product scope: 12V/24V automatic recognition; main-power and auxiliary-power variants; BLE base and BLE + Wi-Fi/LTE connected variants; WeChat Mini Program, Android, iOS, PostgreSQL-backed cloud API and admin console.

> Safety notice: This repository is an engineering starter, not a vehicle-ready design. Do not connect prototypes to road vehicles. Main power switching, DC interruption ratings, fuse coordination, thresholds and thermal design require qualified engineering review and bench/lab validation.

## SKUs
- SP-AUX-BLE — auxiliary power, BLE
- SP-AUX-PRO — auxiliary power, BLE + Wi-Fi/LTE
- SP-MAIN-BLE — main power, BLE
- SP-MAIN-PRO — main power, BLE + Wi-Fi/LTE

Different power grades require separately validated power modules. Peak cranking current is not a substitute for continuous current or DC breaking capacity.

## Telemetry engineering units
- Battery voltage: V (volts)
- Battery current: A (amperes)
- Temperature: °C in 0.1°C increments (one decimal place)

## Database
The backend database is PostgreSQL 15+. MariaDB is no longer the supported runtime database. See `backend/service/README.md` and `docs/POSTGRESQL_MIGRATION.md`.

## Repository layout
- `hardware/`: Rev A controller-board concept, BOM, connector pinout and mechanical PCB template; not a production electrical design.
- `firmware/`: portable C protection core, ESP32-C6 ESP-IDF monitor-mode application and host tests.
- `backend/`: FastAPI service, PostgreSQL migrations and device/user APIs; MQTT broker/client integration is not implemented.
- `protocol/`: BLE, HTTP API and MQTT contract documents.
- `mobile/`, `wechat/`, `admin/`: product scope and planning documents only; no released Flutter, Mini Program or Vue application code yet.
- `manufacturing/`: planning material only; no released production programming or test package.
- `docs/`: engineering decisions, safety, HIL plans and implementation status.

## Engineering implementation status
- PostgreSQL backend includes OIDC user authentication, owner/member-scoped device APIs, Ed25519-signed event/telemetry ingestion, Redis rate limiting and replay protection. Remote identity/database/cache transports now enforce TLS verification.
- Portable C protection core includes low-voltage qualification, recovery delay, engine-state interlock, fault lock and defensive input validation. INA228/TMP117 conversion helpers include sensor-validity checks and host tests.
- ESP32-C6 ESP-IDF application reads INA228/TMP117 and exposes read-only BLE GATT telemetry plus structured boot diagnostics. It remains monitor-only; physical switching is disabled and no actuator driver is implemented.
- NVS dual-slot configuration journaling is implemented and host-tested, but persisted settings are not yet part of a production commissioning flow.
- Rev A BOM, connector pinout, functional schematic description, SVG concept and KiCad mechanical floorplan template are present.
- The KiCad file is not yet an electrical/routed PCB. Native schematic, footprints, copper routing, ERC/DRC, Gerbers and drill files are not released.
- BLE command/configuration, production actuator driver, vehicle transient front-end, current shunt selection, calibration, device-key manufacturing/enrollment, HIL and road-vehicle validation remain open.
- Secure Boot, Flash/NVS Encryption, production signed OTA and eFuse provisioning remain disabled. OTA partition slots are reservations, not an implemented update system.

See `docs/PROJECT_STATUS.md`, the [ESP32-C6 partition layout](docs/OTA_PARTITION_LAYOUT.md), the [secure provisioning lifecycle](docs/SECURE_PROVISIONING_LIFECYCLE.md), and the firmware implementation records in `docs/`, including `docs/IMPLEMENTATION_BATCH_FIRMWARE_05.md`.
