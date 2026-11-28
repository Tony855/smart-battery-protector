#include "sbp_sensor_units.h"
#include <math.h>
#include <stddef.h>

bool sbp_ina228_bus_voltage_v(uint32_t raw, float *volts) {
    if (volts == NULL || raw > 0xFFFFFFU) return false;
    const uint32_t code = (raw >> 4U) & 0xFFFFFU;
    const float measured_v = (float)code * 0.0001953125f;
    /* Rev A protected battery-sense input and API contract are limited to 0-60 V. */
    if (!isfinite(measured_v) || measured_v > 60.0f) return false;
    *volts = measured_v;
    return true;
}

bool sbp_ina228_shunt_current_a(uint32_t raw, float shunt_ohms, float *amps) {
    if (amps == NULL || raw > 0xFFFFFFU || !isfinite(shunt_ohms) ||
        shunt_ohms <= 0.0f || shunt_ohms > 1.0f) return false;
    const uint32_t code = (raw >> 4U) & 0xFFFFFU;
    /* Rail codes indicate a saturated converter; never report clipped current as valid. */
    if (code == 0x7FFFFU || code == 0x80000U) return false;
    int32_t signed_code = (int32_t)code;
    if ((code & 0x80000U) != 0U) signed_code -= 0x100000;
    const float shunt_volts = (float)signed_code * 0.0000003125f;
    const float measured_a = shunt_volts / shunt_ohms;
    /* Preserve the caller's previous value when a valid-looking calibration overflows. */
    if (!isfinite(measured_a)) return false;
    *amps = measured_a;
    return true;
}

bool sbp_tmp117_temperature_deci_c(uint16_t raw, int16_t *deci_c) {
    if (deci_c == NULL) return false;
    int32_t signed_raw = (int32_t)raw;
    if (signed_raw >= 0x8000) signed_raw -= 0x10000;
    float temp_deci = (float)signed_raw * 0.078125f;
    if (!isfinite(temp_deci) || temp_deci < -550.0f || temp_deci > 1500.0f) return false;
    *deci_c = (int16_t)lroundf(temp_deci);
    return true;
}
