# Project Status — 2026-11-17

## Requirements confirmed
- 12V/24V automatic recognition target.
- Main-power and auxiliary-power variants.
- BLE base and BLE + Wi-Fi/4G connected product variants.
- Automatic/manual recovery only through local safety checks.
- PostgreSQL 15+ is the only supported backend database.
- Telemetry units: voltage V, current A, temperature integer 0.1°C.

## Implemented in repository
- Backend API scaffold, PostgreSQL migrations and PostgreSQL CI integration.
- Portable C protection controller core: monitor-only default, low-voltage qualification, recovery hysteresis/delay, engine-off interlock and fault lock.
- INA228 voltage/shunt conversion and TMP117 temperature conversion helpers.
- Host CMake unit tests for state logic and sensor units.
- ESP32-C6 ESP-IDF monitor-mode application shell with I2C sensor access and isolated engine/feedback logic inputs.
- Rev A controller PCB functional netlist definition, connector pinout, preliminary BOM, SVG floorplan and KiCad mechanical floorplan template.

## In progress / not released
- ESP-IDF toolchain build CI is being added and must pass before firmware build is marked verified.
- Native KiCad electrical schematic, actual footprints, routed copper PCB, ERC/DRC, Gerbers and drill files.
- Automotive 12/24V input power supply, reverse-polarity protection and transient/load-dump protection.
- Exact 3.3V regulator, shunt value/rating, isolation circuits and external actuator driver.
- BLE GATT, NVS configuration/commissioning, secure OTA and manufacturing provisioning.
- Vehicle HIL, environmental, EMC, fault injection and thermal tests.

## Critical safety boundaries
- Firmware default is monitor-only; physical actuator output is not implemented.
- Main-power switching must never open when engine state is RUNNING or UNKNOWN.
- No main starter current or high-current power path is routed through the Rev A controller PCB.
- No current threshold is enabled until the shunt and analog measurement chain are selected and calibrated.
- No prototype is approved for installation on a road vehicle.

## Release rule
Do not claim automotive suitability, current rating, safety certification, production readiness or vehicle compatibility until design review and documented verification are complete.
