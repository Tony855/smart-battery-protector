# Firmware & hardware implementation batch 01

## Delivered
- Portable C protection core: boot/self-test, monitor-only, low-voltage qualification, disconnect request, disconnected, recovery qualification and fault lock.
- Configuration validation and safe monitor-only behavior when not commissioned.
- Engine-OFF-only disconnect/restore policy; RUNNING and UNKNOWN inhibit requests.
- Fault handling for invalid sensor, unknown actuator feedback, over-current and over-temperature.
- INA228 bus voltage and shunt-current conversion helpers.
- TMP117 conversion helper to 0.1°C integer units.
- ESP-IDF ESP32-C6 application reading INA228/TMP117 over I2C and isolated engine/feedback logic inputs.
- Read-only NimBLE GATT telemetry service with JSON LiveTelemetry; no remote command/write characteristic.
- No physical actuator output driver is implemented; GPIO14 remains unused.
- Host CMake tests and GitHub Actions workflow.

## Hardware design artifacts
- Rev A controller-board functional schematic/netlist definition.
- Connector pinout CSV and preliminary BOM.
- PCB floorplan SVG.
- Rev A is a low-voltage controller/sensor PCB; it has no starter-current or main battery current path.
- Power front-end, 3.3V regulator, external shunt, isolation circuits and external actuator stage are not yet frozen.
- Native KiCad schematic, routed board, ERC/DRC, Gerbers and drill files are not released.

## Verification boundary
- Host C tests cover logic and unit conversions only.
- ESP-IDF application has not yet been built on ESP-IDF toolchain or flashed to an ESP32-C6 module.
- No real INA228/TMP117 hardware, shunt calibration, isolation circuit, contactor/MOSFET or vehicle bench validation has been run.
- Do not connect to a road vehicle.
