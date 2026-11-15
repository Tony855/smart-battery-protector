# Preliminary Safety Concept

## Hazard to control
Unintended opening of the vehicle main battery circuit while the engine is running can cause loss of vehicle electrical supply, damage or unsafe vehicle behavior.

## Mandatory constraints
- Main-power switching shall be inhibited while engine-running status is active or uncertain.
- Engine-running detection shall not rely solely on a single battery-voltage threshold. Evaluate dedicated IGN/D+ or vehicle-approved signal and define fail-safe behavior.
- Communication loss, MCU reset, watchdog reset, OTA, low-voltage detection or cloud command shall not cause an unintended main-power opening.
- Sensor plausibility and actuator feedback shall be checked.
- Fault state and manual service recovery shall be defined per hazard analysis.
- The power path must have a validated DC interruption rating and upstream protection coordination.

## Required engineering artifacts
System hazard analysis, DFMEA, fault tree, safety requirements traceability, verification evidence and installation restrictions. This draft is not a functional-safety certification or completed safety case.
