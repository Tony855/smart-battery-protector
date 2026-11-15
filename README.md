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

## Status
Requirements and architecture drafts plus an API scaffold. Schematics, PCB, production firmware, apps, cloud deployment, prototypes, validation and certification are not complete. See docs/PROJECT_STATUS.md.
