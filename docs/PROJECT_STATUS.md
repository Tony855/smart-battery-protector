# Project Status — 2026-11-15

## Done
- Confirmed 12V/24V auto compatibility requirement.
- Confirmed main-power and auxiliary-power variants.
- Confirmed BLE base and BLE + Wi-Fi/4G connected variants.
- Confirmed automatic and manual recovery, subject to local safety checks.
- Initial SKU matrix, architecture, safety constraints and protocol drafts.
- Backend scaffold switched to PostgreSQL 15+; canonical PostgreSQL migrations and explicit migration runner added.
- Telemetry contract uses V, A and integer 0.1°C units.

## Not done
- Electrical ratings and safety concept freeze.
- Power calculations, component selection, schematic, PCB, BOM and Gerbers.
- Firmware implementation, mobile apps, mini program and production cloud deployment.
- Live PostgreSQL/Redis production integration, OIDC provider integration, MQTT broker deployment and HIL testing.
- EVT/DVT/PVT, lab tests, production documents and certification.

## Release rule
No unvalidated electrical rating, vehicle compatibility, safety function or certification may be represented as complete.
