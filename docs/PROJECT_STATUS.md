# Project Status — 2026-11-17

## Requirements confirmed
- 12V/24V automatic recognition target.
- Main-power and auxiliary-power variants.
- BLE base and BLE + Wi-Fi/4G connected variants.
- Automatic/manual recovery only through local safety checks.
- PostgreSQL 15+ is the only supported backend database.
- Telemetry units: voltage V, current A, temperature integer 0.1°C.

## Implemented in repository
- Backend API scaffold, PostgreSQL migrations 001–007, PostgreSQL CI integration and telemetry storage of the locked 12V/24V class.
- Portable C protection controller core with monitor-only defaults, low-voltage qualification, recovery hysteresis/delay, engine-off interlock, fault lock and config validation.
- INA228 voltage/shunt conversion and TMP117 temperature conversion to 0.1°C.
- Stable 12V/24V classification helper: 10-second qualification, locked until restart; current voltage windows are preliminary and remain subject to vehicle-envelope validation.
- ESP32-C6 ESP-IDF monitor-mode application: I2C sensor reads, INA228/TMP117 identity checks, INA228 ADCRANGE=0 configuration, isolated engine/feedback inputs, read-only BLE GATT telemetry and locked 12V/24V class reporting.
- Per-voltage thresholds and limits are configurable in Kconfig but protection decision logic defaults OFF; physical actuator output driver is not implemented.
- Host CMake tests include controller, sensor-unit, voltage-class and CRC-protected configuration-record coverage, including the standard CRC32 known vector, invalid configuration boundaries, TMP117 signed-temperature endpoints and out-of-range rejection. Workflow run 44065450047 passed host tests and ESP-IDF build, verified safe commissioning defaults, and uploaded the ESP32-C6 artifact. Later sensor-fault-handling and TMP117 portability changes are under CI validation in run 44066814201.
- ESP-IDF 5.4 CI builds the ESP32-C6 application and uploads bootloader, partition table and application binaries. Successful CI compilation is not a hardware flash or physical-device test.
- Sensor initialization failure no longer aborts the application at `init_i2c()`; the firmware continues advertising read-only BLE telemetry with sensor values invalid and protection disabled. Hardware absence/fault behavior still requires HIL verification.
- Portable configuration record v1 is implemented with explicit little-endian serialization, generation field, strict size/version/magic checks, CRC32, and range validation. ESP-IDF NVS load/save adapter is implemented. Startup validates an existing record but does not apply it to live protection settings. Save rejects stale generations and refuses to overwrite unreadable/corrupt records. No BLE/MQTT configuration write path or authenticated commissioning is enabled.
- Rev A controller PCB functional schematic/netlist definition, connector pinout, preliminary BOM, signal-level SVG, PCB floorplan SVG and KiCad mechanical floorplan template.

## In progress / not released
- Latest ESP-IDF build and firmware artifact workflow must complete successfully after the latest code changes.
- Native KiCad electrical schematic, actual footprints, routed copper PCB, ERC/DRC, Gerbers and drill files.
- Automotive 12/24V input power supply, reverse-polarity protection and transient/load-dump protection.
- Exact 3.3V regulator, shunt value/rating, voltage-sense protection, remote sensor cable protection, isolation circuits and external actuator driver.
- Authenticated commissioning/configuration, NVS encryption policy, secure boot/flash encryption, signed OTA and manufacturing provisioning.
- NVS adapter integration tests and physical power-loss / power-cycle verification.
- Hardware-in-loop plan is documented in `docs/HIL_TEST_PLAN.md`; none of those HIL or vehicle tests have been executed.
- Vehicle HIL, environmental, EMC, fault injection and thermal tests.

## Critical safety boundaries
- Firmware defaults to monitor-only; no physical actuator output is implemented.
- Main-power switching must never open when engine state is RUNNING or UNKNOWN.
- Engine and actuator validity inputs require external fail-low hardware pull-downs and isolated interfaces.
- No main starter current or high-current power path is routed through the Rev A controller PCB.
- No current threshold is enabled until the shunt and analog measurement chain are selected and calibrated.
- No prototype is approved for installation on a road vehicle.

## Release rule
Do not claim automotive suitability, current rating, safety certification, production readiness or vehicle compatibility until design review and documented verification are complete.
