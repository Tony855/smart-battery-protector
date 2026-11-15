# Engineering Decision Records

## EDR-001: Separate main-power and auxiliary-power product families
Status: Proposed
Decision: Use separate power execution modules and ratings; share control/software platform only where electrical and safety isolation requirements permit.
Reason: Main starter/battery paths and auxiliary loads have materially different current, interruption, thermal and fault requirements.

## EDR-002: Local protection authority
Status: Accepted
Decision: The device firmware/hardware owns safety decisions. Mobile and cloud systems submit requests only.
Reason: BLE, phone OS, internet and cloud availability cannot be safety dependencies.

## EDR-003: Wireless controller candidate
Status: Proposed
Decision: Evaluate ESP32-C6 for BLE/Wi-Fi control plane; evaluate separate LTE Cat-1 module for cellular SKU.
Reason: Keep cellular certification/antenna and high-current power path separate. Final selection requires supply, RF, thermal, security and lifecycle review.

## EDR-004: Main-power switching technology
Status: Open
Decision: Compare automotive DC contactor and solid-state approaches after current waveform, DC interruption, failure mode and thermal requirements are measured.
Reason: Do not select a device based only on nominal cranking peak current.
