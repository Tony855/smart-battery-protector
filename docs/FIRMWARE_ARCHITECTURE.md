# Firmware Architecture Draft

Candidate: ESP-IDF + ESP32-C6, subject to hardware validation.

Modules: `board_support` (GPIO/ADC/I2C/SPI/UART); `sensor_manager` (voltage/current/temperature and calibration); `protection_fsm`; `ble_gatt`; `connectivity` (Wi-Fi/LTE, MQTT TLS, offline queue); `security` (device identity, keys, anti-replay, signed image); `ota` (rollback/power-loss recovery); `diagnostics` (fault codes, event logs, factory test).

Logical states: BOOT_SELF_TEST -> VOLTAGE_CLASSIFY -> CONNECTED_MONITOR -> LOW_VOLTAGE_PENDING -> OPEN -> RECOVERY_PENDING -> CONNECTED_MONITOR. Critical sensor/driver/overtemperature/overcurrent faults enter FAULT_LOCKED.

Phone/cloud commands are requests only; local safety policy decides whether execution is allowed. Do not implement a production power-control output until the safety concept and hardware interface are reviewed.