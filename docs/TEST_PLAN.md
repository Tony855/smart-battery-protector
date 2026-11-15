# Verification Plan Draft

Electrical: 12V/24V recognition boundaries, reverse polarity, over/undervoltage, ripple, crank dip and transient pulses.

Power: continuous current, specified-duration peak current, make/inrush, DC interruption, short-circuit coordination, contact resistance and temperature rise.

Environment: high/low temperature, thermal cycling, humidity, vibration, shock, ingress and corrosion as required by installation and market.

Firmware/security: sensor open/short, ADC out-of-range, watchdog, brownout, state-machine boundaries, BLE pairing/auth/replay/privilege tests, OTA interruption/signature rejection/rollback, MQTT TLS/ACL/expiry/offline queue.

Manufacturing: ICT/FCT, sensor calibration, power-path inspection, serial traceability, secure flashing, burn-in and sampling.

Acceptance limits must be defined after electrical ratings are frozen. No test is considered passed without recorded results.