# Rev A controller PCB — functional schematic / netlist

This is the functional schematic definition for the Rev A low-voltage control board. It is not yet a native KiCad schematic or a fabrication netlist.

## Power and ground
- J1.1: +5V_PROTECTED input from a separately validated automotive DC/DC front-end or bench supply.
- J1.2: GND.
- U1 ESP32-C6-MINI-1 3V3 supplied by a 3.3 V regulator (U4; exact part and thermal design not frozen).
- U2 INA228 and U3 TMP117 powered from 3V3; decoupling capacitors placed at each IC.
- All low-voltage logic grounds join at the controller ground plane. High-current shunt power terminals do not route through this PCB.

## Controller U1 — ESP32-C6-MINI-1-H4
- Pin 3 (3V3) -> 3V3.
- Pins 1, 2, 11, 14, 36–53 (GND) -> GND according to module land pattern.
- Pin 8 (EN) -> reset network; 10 kΩ pull-up and 1 µF timing capacitor as a starting reference, then validate power sequencing.
- GPIO6 (module pin 15) -> I2C_SDA.
- GPIO7 (module pin 16) -> I2C_SCL.
- GPIO20 (module pin 26) -> ENGINE_RUNNING_LOGIC (isolated external interface).
- GPIO21 (module pin 27) -> ENGINE_VALID_LOGIC (isolated external interface).
- GPIO18 (module pin 24) -> ACTUATOR_FEEDBACK_LOGIC.\n- GPIO19 -> ACTUATOR_FEEDBACK_VALID_LOGIC; low/open-wire means UNKNOWN.
- GPIO14 (module pin 19) -> ACTUATOR_REQUEST_LOGIC; external pull-down; firmware output disabled by default.
- GPIO12/GPIO13 (module pins 17/18) reserved for USB D-/D+ only if USB connector ESD and routing are designed.
- GPIO4/5 (MTMS/MTDI), GPIO8/9 and GPIO15 are strapping/JTAG-related pins; do not attach safety inputs or drivers to them. Engine status uses GPIO20/21 instead.

## Bus monitor U2 — INA228
- I2C address: 0x40 (A0/A1 strap configuration must be checked against selected package).
- VBUS measures J7 protected battery sense through a properly rated high-impedance filter/clamp front-end, not directly through a GPIO. The 0–60V connector range is a design target only; transient protection must be engineered before connection.
- IN+ / IN- connect to external Kelvin sense wires from the selected shunt. Do not route load current through PCB.
- ALERT is optional and may be routed to a diagnostic GPIO after polarity/open-wire review.
- Select shunt and ADCRANGE together. Firmware current conversion is invalid until shunt resistance is commissioned.

## Temperature sensor U3 — TMP117
- I2C address: 0x48 with address pin strap as specified in the selected package.
- Place sensor near the external MOSFET/contactor thermal interface via a dedicated thermal coupling point.
- Keep away from regulator, ESP32 RF section and other self-heating components.
- Use 3V3, GND, I2C_SDA, I2C_SCL and local decoupling.

## Connectors
- J1: protected 5 V logic input, 2 pins.
- J2: external Kelvin shunt sense, 4 pins (SHUNT_IN+, SHUNT_IN-, optional remote sense return pair per final sensor topology).\n- J7: protected battery voltage sense input, 2 pins.\n- J8: remote TMP117 temperature probe, 4 pins.
- J3: isolated engine status, 4 pins (3V3, ENGINE_VALID, ENGINE_RUNNING, GND).
- J4: isolated actuator feedback, 4 pins (3V3, FEEDBACK_VALID, FEEDBACK, GND).
- J5: actuator request interface, 3V3/GND/REQUEST. Output remains disabled by default and is not a gate/coil drive.
- J6: UART debug / manufacturing test.
- SW1: reset; SW2: boot/download.

## Safety net rules
- ENGINE_VALID low or open wire means engine state UNKNOWN.
- Actuator feedback validity low/open wire means UNKNOWN and FAULT_LOCKED.
- No direct vehicle battery voltage reaches ESP32 GPIO.
- A request pin is not a power switch. External driver must enforce safe default and independent interlocks.
