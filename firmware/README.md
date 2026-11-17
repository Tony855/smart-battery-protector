# ESP32-C6 Firmware

## Current implementation
- Portable C protection decision core in `core/`, buildable with host CMake.
- Default configuration is monitor-only. Protection thresholds default to zero/disabled and no actuator GPIO is driven.
- Stable 12V/24V classification uses a 10-second sample window and locks the class until restart; ambiguous voltage stays UNKNOWN. The current windows (9.0–16.5V and 18.0–33.0V) are preliminary and require vehicle-envelope validation.
- Per-12V and per-24V low/recovery thresholds, current limit, temperature limit and qualification times are configurable through ESP-IDF Kconfig. Protection decision logic enables only after voltage class is locked and the shunt and all thresholds are commissioned.
- Low-voltage qualification and recovery use independent delays and hysteresis.
- Main and auxiliary variants conservatively require a positively known engine-OFF state before disconnect/restore requests.
- Sensor invalidity, actuator-feedback unknown, over-current and over-temperature enter a fault-locked state.
- ESP-IDF application reads INA228/TMP117, verifies sensor IDs, configures INA228 continuous conversion with ADCRANGE=0, and publishes read-only BLE GATT telemetry.
- No physical actuator output driver is implemented. GPIO14 is reserved and not driven.

## Build and test the portable core
```sh
cmake -S firmware/core -B build/firmware-core
cmake --build build/firmware-core
ctest --test-dir build/firmware-core --output-on-failure
```

## Build ESP32-C6 firmware
```sh
cd firmware/esp-idf
idf.py set-target esp32c6
idf.py build
```

## Safety and release boundary
The C core returns requested actions; it does not drive a MOSFET, relay or contactor. The ESP-IDF application currently reports measurements and read-only BLE telemetry only. It has not been flashed or tested on a physical controller board. Do not connect to a vehicle.
