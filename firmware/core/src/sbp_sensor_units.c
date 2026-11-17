#include "sbp_sensor_units.h"
#include <math.h>
#include <stddef.h>

bool sbp_ina228_bus_voltage_v(uint32_t raw, float *volts) {
    if (volts == NULL || raw > 0xFFFFFFU) return false;
    uint32_t code = (raw >> 4U) & 0xFFFFFU;
    *volts = (float)code * 0.0001953125f;
    return isfinite(*volts);
}

bool sbp_ina228_shunt_current_a(uint32_t raw, float shunt_ohms, float *amps) {
    if (amps == NULL || raw > 0xFFFFFFU || !isfinite(shunt_ohms) ||
        shunt_ohms <= 0.0f || shunt_ohms > 1.0f) return false;
    int32_t code = (int32_t)((raw >> 4U) & 0xFFFFFU);
    if ((code & 0x80000) != 0) code -= 0x100000;
    const float shunt_volts = (float)code * 0.0000003125f;
    *amps = shunt_volts / shunt_ohms;
    return isfinite(*amps);
}

bool sbp_tmp117_temperature_deci_c(uint16_t raw, int16_t *deci_c) {
    if (deci_c == NULL) return false;
    int16_t signed_raw = (int16_t)raw;
    float temp_deci = (float)signed_raw * 0.078125f;
    if (!isfinite(temp_deci) || temp_deci < -550.0f || temp_deci > 1500.0f) return false;
    *deci_c = (int16_t)(temp_deci >= 0.0f ? temp_deci + 0.5f : temp_deci - 0.5f);
    return true;
}
