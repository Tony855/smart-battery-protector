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
- Host CMake tests cover controller logic, sensor units, voltage classification, CRC-protected configuration records, NVS journal recovery and boot-diagnostics schema/JSON encoding. Workflow run 44071200302 passed host tests, ESP32-C6 ESP-IDF build, safe commissioning-default checks and firmware artifact upload.
- ESP-IDF 5.4 CI builds the ESP32-C6 application and uploads bootloader, partition table and application binaries. Successful CI compilation is not a hardware flash or physical-device test.
- Sensor initialization failure no longer aborts the application at `init_i2c()`; the firmware continues in monitor-only mode with invalid sensor telemetry. Boot diagnostics now classify reset reason, NVS state, sensor initialization, monitor-only reason flags and configuration generation in a structured serial log and a separate BLE READ-only characteristic. Hardware fault behavior and BLE interoperability still require HIL verification.
- Portable configuration record v1 is implemented with explicit little-endian serialization, generation field, strict size/version/magic checks, CRC32, and range validation. ESP-IDF NVS now uses alternating `record_a` / `record_b` slots and retains `record_v1` as a read-only migration fallback. Loads select the highest valid generation; saves write the older/inactive slot, commit and read back exact bytes, reject stale generations and fail closed on conflicting or corrupt-only storage. Host NVS mock tests cover interrupted commit, corruption fallback, legacy migration and generation conflicts. Startup validates a record but does not apply it to live protection settings. No BLE/MQTT configuration write path or authenticated commissioning is enabled.
- Rev A controller PCB functional schematic/netlist definition, connector pinout, preliminary BOM, signal-level SVG, PCB floorplan SVG and KiCad mechanical floorplan template.

## In progress / not released
- Dual-slot NVS code and the additional two-populated-slot power-loss regression test passed host tests, ESP32-C6 ESP-IDF build, safe-default verification and artifact upload in run 44071200302.
- Native KiCad electrical schematic, actual footprints, routed copper PCB, ERC/DRC, Gerbers and drill files.
- Automotive 12/24V input power supply, reverse-polarity protection and transient/load-dump protection.
- Exact 3.3V regulator, shunt value/rating, voltage-sense protection, remote sensor cable protection, isolation circuits and external actuator driver.
- Authenticated commissioning/configuration, NVS encryption policy, secure boot/flash encryption, signed OTA and manufacturing provisioning.
- Physical NVS power-loss / power-cycle and flash-endurance verification; host mock tests do not replace hardware tests.
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
