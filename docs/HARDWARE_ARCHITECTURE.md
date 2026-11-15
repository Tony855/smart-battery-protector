# Hardware Architecture Draft

## Blocks
1. Controller: ESP32-C6 candidate for BLE/Wi-Fi, state machine, sampling, logging and OTA; validate module, RF, thermal and power suitability.
2. Connectivity: LTE Cat-1 module for connected SKU; bands/operator and antenna design TBD.
3. Input power: DC/DC, reverse-polarity protection, fuse coordination, surge/transient suppression.
4. Sensing: precision voltage measurement, Hall current sensor, power device/contactor temperature.
5. Actuation: automotive-grade MOSFET evaluation for auxiliary version; automotive DC contactor or dedicated power module evaluation for main version.
6. Safety chain: independent hardware protection where required, watchdog, safe driver defaults and fault lockout.
7. Mechanics: terminals, busbars, harness, enclosure, sealing, vibration and thermal path.

## Design gates
Define continuous current, cranking peak and duration, make/inrush, DC breaking capacity, short-circuit withstand, temperature rise, contact resistance and fuse coordination independently. Never infer DC breaking rating from AC rating.

## Prohibited shortcuts
- No main-power contactor selection before fault current and DC interruption requirements are defined.
- No ordinary PCB traces as an assumed hundreds-of-amps path.
- No phone/cloud/BLE dependency for safety protection.
- No unconditional battery disconnect while engine is running.

Evaluate applicable ISO 16750-2, ISO 7637-2, EMC and environmental requirements for target market and vehicle integration.