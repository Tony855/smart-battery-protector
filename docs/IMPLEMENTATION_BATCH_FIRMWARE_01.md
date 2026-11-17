# Firmware & hardware implementation batch 01

## Delivered
- Portable C protection decision core: monitor-only, low-voltage qualification, disconnect request, disconnected, recovery qualification and fault lock.
- Configuration validation rejects non-finite thresholds and invalid hysteresis.
- Main and auxiliary variants conservatively require a positively known engine-OFF state before disconnect/restore requests.
- Over-current and over-temperature request a disconnect only when engine state is positively OFF and actuator feedback says CLOSED; invalid sensors or unknown feedback lock operation.
- INA228 VBUS/VSHUNT conversion and TMP117 conversion to integer 0.1°C.
- Stable 12V/24V classifier: preliminary 9.0–16.5V / 18.0–33.0V windows, 10-second qualification, class locked until restart, ambiguous values UNKNOWN.\n- Backend telemetry schema migration 007 stores the locked class as 12, 24 or NULL.
- ESP-IDF ESP32-C6 application reads INA228/TMP117 over I2C, verifies sensor IDs, configures INA228 continuous conversion with ADCRANGE=0 and reads isolated engine/actuator feedback.
- Per-12V/24V low/recovery thresholds, current limit, temperature limit and qualification times are Kconfig settings. Protection decision logic is disabled by default and only enables when voltage class, shunt and all thresholds are commissioned.
- Read-only NimBLE GATT telemetry service publishes JSON LiveTelemetry in V, A and 0.1°C units. No BLE write/control characteristic exists.
- No physical actuator output driver is implemented; GPIO14 is reserved and never driven.
- Host CMake tests and GitHub Actions host + ESP-IDF build workflow.

## Hardware design artifacts
- Rev A controller-board functional schematic/netlist definition and signal-level SVG diagram.
- Connector pinout CSV, preliminary BOM and remote TMP117 probe / battery sense connector definitions.
- SVG PCB floorplan and KiCad 9 mechanical floorplan template.
- Rev A is a low-voltage controller/sensor PCB; it has no starter-current or main battery current path.
- Power front-end, 3.3V regulator, external shunt, voltage-sense transient protection, isolation circuits and external actuator stage are not yet frozen.
- Native KiCad electrical schematic, actual footprints, routed copper, ERC/DRC, Gerbers and drill files are not released.

## Verification boundary
- Host C tests validate portable state logic, voltage classification and sensor unit conversion only.
- ESP-IDF build is verified only when the latest ESP32-C6 build workflow completes successfully; a successful compile does not validate physical hardware.
- No real INA228/TMP117 board, shunt calibration, isolation circuit, contactor/MOSFET or vehicle bench validation has been run.
- Do not connect to a road vehicle.
