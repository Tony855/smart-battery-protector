# ESP32-C6 protection commissioning

## Default build is safe monitor-only
The checked-in defaults and Kconfig defaults enforce:
- `CONFIG_SBP_PROTECTION_ENABLE` disabled
- `CONFIG_SBP_SHUNT_MICRO_OHM=0`
- 30-second low-voltage and recovery qualification windows

The ESP-IDF application initializes NVS and validates a versioned 56-byte configuration record when one exists. The record uses CRC32 for accidental-corruption detection and a monotonically increasing generation check on writes. A missing, unreadable or corrupt record is not silently erased or replaced. At this stage a valid NVS record is logged but **not applied to live protection settings**.

In this default state the device reports sensor readings and read-only BLE telemetry. It does not issue a physical disconnect.

## Engineering configuration
Only after battery type, vehicle voltage envelope, current shunt and sensor calibration are frozen, open:
```sh
cd firmware/esp-idf
idf.py menuconfig
```
Under **Smart Battery Protector**, configure:
- Product variant (main-power or auxiliary).
- Enable protection decision logic.
- 12V low-voltage threshold (mV) and recovery threshold (mV).
- 24V low-voltage threshold (mV) and recovery threshold (mV).
- Maximum absolute current (mA).
- Maximum temperature (0.1°C units).
- Low-voltage and recovery qualification times.
- External Kelvin shunt resistance (micro-ohms).

The firmware waits for a stable 10-second 12V/24V classification before enabling a matching threshold set. Preliminary classification windows are 9.0–16.5V for 12V and 18.0–33.0V for 24V; outside those windows remains UNKNOWN. These windows require validation against the final vehicle and battery envelope.

If any required threshold is absent or inconsistent, the firmware stays monitor-only. Even if a configuration record is present, this build does not apply it to the protection controller. The NVS save API is not exposed over BLE or MQTT. No physical actuator output driver exists in this build.

## Actuator release gate
Do not add or enable an actuator output driver on a prototype or vehicle until:
1. The power stage and DC breaking ratings are selected and validated.
2. Hardware default state is proven safe during power-up, reset, brownout and firmware crash.
3. Engine-running input is galvanically isolated and fail-safe.
4. Independent hardware interlocks and actuator feedback are tested.
5. HIL fault injection and engineering sign-off are complete.

A Kconfig build flag is not a substitute for a physical safety design or approval.
