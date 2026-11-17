#ifndef SBP_SENSOR_UNITS_H
#define SBP_SENSOR_UNITS_H
#include <stdbool.h>
#include <stdint.h>

/* INA228 VBUS: 20-bit unsigned code, 195.3125 uV/LSB. */
bool sbp_ina228_bus_voltage_v(uint32_t register_value, float *volts);
/* INA228 VSHUNT: signed 20-bit code. ADCRANGE=0: 312.5 nV/LSB. */
bool sbp_ina228_shunt_current_a(uint32_t register_value, float shunt_ohms, float *amps);
/* TMP117 temperature register: signed 16-bit, 0.0078125 degC/LSB. */
bool sbp_tmp117_temperature_deci_c(uint16_t register_value, int16_t *deci_c);
#endif
