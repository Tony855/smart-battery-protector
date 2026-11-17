# ESP32-C6 Firmware

## Current implementation
- Portable C protection decision core in core/; buildable with host CMake.
- Default commissioning policy is monitor-only. No thresholds are preloaded and no output pin is driven.
- Low-voltage qualification and recovery use independent delays and hysteresis.
- Main and auxiliary variants both conservatively require a positively known engine-OFF state before disconnect/restore requests.
- Sensor invalidity, actuator-feedback unknown, over-current and over-temperature enter a fault-locked state.
- BLE, sensor hardware drivers, NVS provisioning and the physical actuator driver are not yet integrated in this first firmware increment.

## Build and test the portable core
```sh
cmake -S firmware/core -B build/firmware-core
cmake --build build/firmware-core
ctest --test-dir build/firmware-core --output-on-failure
```

## ESP-IDF target
ESP32-C6-MINI-1 is the candidate module. The ESP-IDF application shell, sensor drivers and BLE GATT service are the next integration increment after PCB pinout and selected sensor parts are frozen. Do not flash this portable core directly to a vehicle controller.

## Safety
The C core only returns requested actions. It does not drive a MOSFET, relay or contactor. Production actuator enable remains disabled until the hardware power stage, engine-state input, feedback diagnostics and release tests are approved.
