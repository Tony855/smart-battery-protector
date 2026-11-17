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
The backend database is PostgreSQL 15+. MariaDB is no longer the supported runtime database. See backend/service/README.md and docs/POSTGRESQL_MIGRATION.md.

## Repository layout
hardware/ schematics/PCB/BOM; firmware/ MCU firmware; mobile/ Flutter; wechat/ mini program; backend/ API/MQTT/PostgreSQL; admin/ Vue; protocol/ BLE/API; manufacturing/ production; docs/ engineering docs.

## Engineering implementation status
- PostgreSQL backend and telemetry API scaffold are in the repository.
- Portable C protection core and INA228/TMP117 unit conversion helpers are implemented with host tests.
- ESP32-C6 ESP-IDF monitor-mode application reads INA228/TMP117 and exposes read-only BLE GATT telemetry; physical switching is disabled by default.
- Rev A controller PCB engineering pack, connector pinout, BOM, functional netlist, SVG floorplan and KiCad mechanical floorplan template are present.
- The KiCad file is not yet an electrical/routed PCB. Native schematic, footprints, copper routing, ERC/DRC, Gerbers and drill files are not released.
- BLE command/configuration, NVS commissioning, production actuator driver, vehicle transient front-end, current shunt selection, calibration, HIL and road-vehicle validation remain open.
See docs/PROJECT_STATUS.md and docs/IMPLEMENTATION_BATCH_FIRMWARE_01.md.
