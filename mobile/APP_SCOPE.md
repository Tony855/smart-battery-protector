# Mobile App Scope v0.1

Target: Flutter for Android and iOS.

## Navigation
1. Sign-in / account
2. Device scan and bind
3. Device overview
4. Live telemetry
5. Protection profile and settings
6. Event/fault history
7. Firmware update
8. Support and diagnostics

## UX safety
- Distinguish "request sent", "device accepted", and "physical state confirmed".
- Display last-seen time and offline status.
- Never present a queued cloud command as completed actuation.
- Explain why a request is rejected (engine state, sensor fault, temperature, fault lock).
- Destructive or power-state requests require confirmation and clear vehicle safety warning.
- Settings are read back from device after write; show config revision and sync state.

## Platform notes
BLE permissions, background scanning and reconnect behavior differ by OS version. Core protection must continue on the device without the phone app.
