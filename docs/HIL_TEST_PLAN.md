# Smart Battery Protector — HIL verification plan

Status: engineering test plan only. No hardware-in-loop or vehicle test has been executed.

## 1. Test boundary

This plan validates the controller logic and low-voltage interface before any starter/battery power path is connected. The present Rev A PCB is a controller/sensor concept and does not contain a rated high-current disconnect stage. Use a current-limited bench supply and isolated signal simulators; do not connect a vehicle starter cable.

## 2. Required bench equipment

- Programmable DC source covering the proposed 12V and 24V test envelopes, current limited for the controller.
- Independent calibrated DMM and current measurement reference.
- INA228 bus/shunt simulator or precision voltage/current injection fixture.
- TMP117 temperature register simulator or calibrated temperature chamber/probe fixture.
- Isolated engine RUN/STOP signal simulator with open-wire fault insertion.
- Actuator feedback simulator with open/short fault insertion; no real actuator attached.
- Programmable power interrupter for brownout, reset and rapid power-cycle tests.
- Logic analyzer / oscilloscope for reset, GPIO default state, I2C and BLE observation.
- Test log with firmware SHA, board revision, fixture calibration IDs and captured results.

## 3. Mandatory test cases

| ID | Scenario | Stimulus | Required result |
|---|---|---|---|
| HIL-001 | Safe startup | Power-on with factory defaults | Protection disabled; no actuator drive; BLE telemetry only |
| HIL-002 | 12V classification | Stable voltage in 12V window for less than 10 s, then 10 s | UNKNOWN before qualification; 12V locked only after full qualification |
| HIL-003 | 24V classification | Stable voltage in 24V window for less than 10 s, then 10 s | UNKNOWN before qualification; 24V locked only after full qualification |
| HIL-004 | Ambiguous voltage | Mid-band, below-range and above-range samples | UNKNOWN; no protection activation |
| HIL-005 | Invalid sample | Inject failed/NaN voltage sample during qualification | Qualification timer resets; no premature class lock |
| HIL-006 | No class switching | Lock 12V, then apply 24V-range voltage without reset | Classification remains latched; no runtime profile switch |
| HIL-007 | Engine RUN interlock | Engine RUNNING while low-voltage condition persists | Controller never requests disconnect |
| HIL-008 | Engine UNKNOWN interlock | Open engine-valid wire during low-voltage condition | Controller never requests disconnect |
| HIL-009 | Engine STOP | Valid engine OFF and qualified low voltage | Only a logical request may be produced when all prerequisites are valid; no physical output in current build |
| HIL-010 | Feedback unknown | Actuator feedback validity absent | Fault-safe state; no disconnect request |
| HIL-011 | Sensor fault | Disconnect INA228 or TMP117 / inject invalid IDs | Protection disabled or fault-locked; no disconnect request |
| HIL-012 | Current calibration missing | Shunt value remains zero | Current invalid; protection cannot be commissioned |
| HIL-013 | Overcurrent | Inject calibrated current above configured limit | Fault behavior follows engine/feedback interlocks; output remains logical only |
| HIL-014 | Overtemperature | Inject calibrated temperature above configured limit | Fault behavior follows engine/feedback interlocks; output remains logical only |
| HIL-015 | MCU reset | Reset during each controller state | Hardware output must remain in externally defined safe state; firmware must not create a pulse |
| HIL-016 | Brownout / power loss | Sweep supply through brownout and remove power | No unintended actuator transition; persisted config must not be silently erased |
| HIL-017 | NVS absent | Blank NVS namespace | Startup logs missing configuration; monitor-only defaults remain |
| HIL-018 | NVS corruption | Modify payload byte / CRC / version / reserved byte | Record rejected; firmware must not auto-erase or apply it |
| HIL-019 | NVS stale generation | Attempt save with same or lower generation | Save rejected; current valid record preserved |
| HIL-020 | NVS power interruption | Interrupt supply during NVS commit, then reboot | Record is either old valid or new valid; never a partially accepted record |
| HIL-021 | BLE permissions | Connect from an unpaired client and inspect GATT | Telemetry read/notify only; no control or configuration write characteristic |
| HIL-022 | BLE disconnect | Drop BLE connection during telemetry | Local logic is unaffected; no protection-state change caused by radio loss |
| HIL-023 | Dual-slot rotation power loss | Seed two valid generations; interrupt power while replacing the older slot | The previously newest committed slot remains valid and is selected after reboot |
| HIL-024 | Newest-slot corruption | Corrupt the newest slot after two successful saves | The older valid slot is selected; corrupt data is never applied |
| HIL-025 | Legacy NVS migration | Boot with only a valid `record_v1`; save a newer generation | Legacy record loads; first journal write uses a new slot and leaves `record_v1` unchanged |
| HIL-026 | Generation conflict | Place different valid payloads with the same generation in both slots | Load and save fail closed; no arbitrary record is selected |
| HIL-027 | Reset reason diagnostics | Power-cycle, issue software reset and inject brownout reset using approved fixture | Boot diagnostics report the matching reset category; unknown values remain unknown |
| HIL-028 | NVS boot diagnostics | Test blank NVS, valid-but-not-applied record, corrupt slots and NVS init error | Read-only diagnostics report the correct NVS state and generation; protection remains disabled |
| HIL-029 | Sensor boot diagnostics | Boot with both sensors present, then with INA228/TMP117 missing or wrong device ID | Diagnostics distinguish READY from INIT_FAILED; telemetry validity flags remain authoritative for live samples |
| HIL-030 | Diagnostics GATT permissions | Read boot diagnostics and inspect characteristic properties | Diagnostics characteristic is READ only; no WRITE or NOTIFY; telemetry characteristic remains READ/NOTIFY only |

## 4. Pass/fail rules

- Every test must record expected result, actual result, firmware SHA, board revision, fixture calibration, test date and operator.
- Any unintended actuator request while engine state is RUNNING or UNKNOWN is an immediate safety failure.
- Any unexpected actuator GPIO pulse during reset, brownout or firmware crash is an immediate safety failure.
- Any corrupted or unsupported NVS record accepted as valid is an immediate failure.
- Do not waive failures by changing thresholds without recording a new configuration revision and rerunning affected tests.
- A test is not passed by source inspection or host unit tests; it requires captured HIL evidence.

## 5. Release gates before a real power stage

1. Native electrical schematic and PCB complete; ERC/DRC clean.
2. Input protection and power supply validated against applicable automotive transient requirements.
3. High-current switch topology, DC interrupt rating, thermal design and fault protection frozen for each vehicle class.
4. Hardware default-off behavior and independent engine interlock demonstrated.
5. HIL-001 through HIL-030 passed on production-intent hardware.
6. Independent design review and documented risk assessment completed.
7. Only then plan supervised vehicle testing with appropriate fusing, isolation and emergency disconnect.

## 6. Current execution status

- Host portable-core tests: automated CI evidence only.
- ESP-IDF build: see the latest GitHub Actions run.
- NVS persistence: dual-slot adapter and host mock tests implemented; physical power-loss behavior and flash wear behavior not yet tested.
- HIL tests: not run.
- Vehicle tests: not run.
- Safety certification: not obtained.
