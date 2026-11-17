# ESP-IDF application — ESP32-C6

This is the ESP-IDF application shell for the SBP controller. Target: ESP32-C6. Tested build environment is intended to be ESP-IDF v5.4.x; hardware bring-up is not yet complete.

## Build
```sh
cd firmware/esp-idf
idf.py set-target esp32c6
idf.py build
```

## Current behavior
- I2C master on GPIO6 (SDA) and GPIO7 (SCL).
- INA228 at 0x40 for bus voltage and external shunt voltage.
- TMP117 at 0x48 for temperature.
- Engine-state interface uses two isolated logic inputs: ENGINE_VALID (GPIO21) and ENGINE_RUNNING (GPIO20). If VALID is low, engine state is UNKNOWN.
- Actuator feedback is read on GPIO18.
- Actuator output GPIO14 is compiled out unless the explicit Kconfig option is enabled; the default build is monitor-only.
- Telemetry log and BLE GATT LiveTelemetry use V, A, and integer 0.1°C units.\n- BLE advertises as SBP-CTRL and exposes a read/notify-only JSON telemetry characteristic; no remote command/write characteristic exists.

## Critical commissioning requirements
1. Select and characterize the external Kelvin shunt; leave CONFIG_SBP_SHUNT_MICRO_OHM=0 until the exact part and layout are approved. Current is considered invalid while this is zero.
2. Implement and validate the automotive protected power supply and isolated IGN/feedback input circuits before connecting vehicle signals.
3. Configure calibrated protection thresholds only after battery chemistry, capacity, vehicle envelope and thermal testing are known.
4. Keep actuator output disabled. No contactor/MOSFET gate driver or high-current path is implemented by this board.
5. Confirm the INA228 ADC range and register configuration against the selected shunt before current measurements are used for protection.

This app is an engineering bring-up shell, not road-vehicle firmware.
