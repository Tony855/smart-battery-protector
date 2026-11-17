# Protection State Machine Specification v0.1

Status: behavioral specification draft; not production safety approval.

## States
- POWER_ON: outputs held in hardware-defined safe condition; initialize watchdog and diagnostics.
- SELF_TEST: verify ADC plausibility, sensor presence, memory/config integrity and actuator feedback.
- CLASSIFY_SYSTEM: classify nominal 12V or 24V profile only inside validated voltage windows; ambiguous voltage enters FAULT_LOCKED.
- MONITOR_CONNECTED: collect voltage/current/temperature and vehicle-running evidence.
- LOW_VOLTAGE_QUALIFY: require threshold crossing for configured duration; reject transient cranking dips and require engine-off confidence.
- OPEN_REQUESTED: local safety gate evaluates request and all interlocks before actuation.
- OPEN: verify actuator feedback and record reason/event.
- RECOVERY_QUALIFY: require recovery threshold plus hysteresis, delay, acceptable temperature/current, and engine-state interlock.
- MANUAL_RECOVERY_REQUEST: manual command goes through the same local safety gate.
- FAULT_LOCKED: prevent automatic actuation until fault-specific recovery criteria are met.

## Invariants
1. Main-power output shall not open when engine-running is true or unknown.
2. BLE/Wi-Fi/LTE loss shall not change the power state.
3. MCU reset, watchdog, OTA and brownout shall not cause an unintended open transition.
4. All commands are authenticated, time-bounded and idempotent.
5. Sensor implausibility blocks automatic decisions.
6. Automatic and manual recovery both obey the same interlocks.
7. Actuator command and physical feedback must be compared; mismatch creates a fault.

## Required tests
State transition coverage, boundary values, sensor open/short, stuck actuator, feedback mismatch, reset injection, comms loss, OTA interruption and engine-state uncertainty.

## 12V/24V classification implementation note
The current firmware helper samples the INA228 bus voltage for 10 seconds and locks the detected class until controller restart:
- Preliminary 12V window: 9.0–16.5 V.
- Preliminary 24V window: 18.0–33.0 V.
- The 16.5–18.0 V gap and readings outside both windows remain UNKNOWN.
- Once 12V or 24V is locked, runtime voltage changes do not switch the class.

These are conservative bring-up windows, not approved vehicle operating limits. Validate against battery chemistry, charging systems, cold cranking, alternator regulation and transient profiles before production. Unknown classification must keep protection thresholds disabled.
