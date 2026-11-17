# Rev A — Low-voltage controller / sensor PCB

**Design status: engineering layout proposal; not released for fabrication.**

This first board is a low-voltage controller and sensor interface only. It does not carry starter-motor or vehicle main-battery load current. Main-power switching must use a separately engineered automotive DC contactor/power module and protected driver. The auxiliary power stage is also external for Rev A so its current rating can be selected and validated independently.

## Architecture
- Controller: Espressif ESP32-C6-MINI-1-H4 (105°C module option preferred for automotive ambient evaluation; temperature rating does not make the board automotive-qualified).
- Bus/current monitor: TI INA228; external four-wire Kelvin shunt connects to J3. The shunt value is a commissioning parameter and remains unset in firmware by default.
- Temperature sensor: remote TI TMP117 probe on J8; install it at the battery case or the selected power-stage thermal point. The measured physical point must be recorded per SKU.
- Logic supply: externally regulated/protected 5 V at J1 for Rev A bring-up; 3.3 V regulator selection and vehicle front-end are a separate design gate.
- Engine state: two isolated logic signals, ENGINE_VALID and ENGINE_RUNNING. Open wire / missing validity is interpreted as UNKNOWN.
- Actuator: request and feedback are low-voltage logic only. The actual contactor/MOSFET driver is external and remains disabled in firmware.

## Pin allocation
See connector_pinout.csv. I2C is GPIO6/7. GPIO20/21 are engine-running/valid inputs. GPIO18/19 are actuator feedback state/validity. GPIO14 is a reserved actuator request signal and is not driven by current firmware.

## Design exclusions
- No high-current copper, busbar or starter-current path on this PCB.
- No direct 12/24 V signal is allowed on ESP32 GPIO. J7 battery sense must pass through a protected, high-impedance analog front-end before reaching INA228. IGN and feedback must be isolated/conditioned externally.
- Do not populate a TVS, regulator or shunt based on nominal voltage alone; complete load-dump, reverse-polarity, transient, thermal and fault-current analysis first.
- No Gerbers, drill files or assembly outputs are released in this revision.

## Fabrication release gates
1. Freeze power input, regulator, transient suppression and creepage/clearance.
2. Select INA228 package and shunt; validate Kelvin routing and ADC range.
3. Validate TMP117 package, thermal placement and sensor mounting.
4. Verify ESP32-C6-MINI-1 land pattern against Espressif's current land-pattern source and antenna keepout.
5. Complete schematic capture, ERC, PCB DRC, RF review and thermal analysis.
6. Bench test sensor accuracy, brownout, reverse polarity, EFT/surge, ESD, conducted/radiated emissions and actuator fault behavior.
7. Review with a qualified automotive hardware engineer before vehicle connection.
