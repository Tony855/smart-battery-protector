# Implementation Batch 33 — Sensor conversion invalid-input coverage

Date: 2026-11-24

## Change
Extended portable unit conversion tests for INA228 bus voltage, INA228 signed shunt current and TMP117 temperature.

Coverage now explicitly checks:
- Null output pointers.
- 24-bit register overflow inputs.
- Invalid shunt values: zero, negative, >1 ohm, NaN and infinity.
- Rejection of signed VSHUNT saturation rails while accepting adjacent representable codes.
- TMP117 physical range boundaries at -55.0°C and +150.0°C and just outside them.
- Rejected invalid sensor input preserves the prior output value.

## Validation boundary
These tests validate conversion functions only. They do not validate sensor calibration, ADC analog front-end behavior, noise, wiring faults, EMI, thermal placement, sampling timing, or the physical accuracy of sensors in a vehicle. Host CI is required for this change; physical characterization remains open.
