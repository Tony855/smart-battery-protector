#include "sbp_sensor_units.h"
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>

int main(void) {
    float volts = 0.0f;
    /* 12.000 V / 195.3125 uV = 61440 counts; register is left-aligned. */
    assert(sbp_ina228_bus_voltage_v(61440U << 4U, &volts));
    assert(fabsf(volts - 12.0f) < 0.001f);

    float amps = 0.0f;
    /* +10 mV across 1 mOhm = +10 A. */
    uint32_t positive_code = (uint32_t)(10000.0f / 0.0003125f);
    assert(sbp_ina228_shunt_current_a(positive_code << 4U, 0.001f, &amps));
    assert(fabsf(amps - 10.0f) < 0.02f);
    /* -10 mV signed two's-complement VSHUNT. */
    int32_t negative_code = -(int32_t)positive_code;
    uint32_t negative_register = ((uint32_t)negative_code & 0xFFFFFU) << 4U;
    assert(sbp_ina228_shunt_current_a(negative_register, 0.001f, &amps));
    assert(fabsf(amps + 10.0f) < 0.02f);

    int16_t temp = 0;
    /* TMP117 raw 0x0CA0 = 25.0°C -> 250 deci-degrees. */
    assert(sbp_tmp117_temperature_deci_c(0x0C80U, &temp));
    assert(temp == 250);
    /* -10.0°C */
    assert(sbp_tmp117_temperature_deci_c((uint16_t)(int16_t)-1280, &temp));
    assert(temp == -100);

    assert(!sbp_ina228_shunt_current_a(0U, 0.0f, &amps));
    assert(!sbp_tmp117_temperature_deci_c(0U, NULL));
    puts("SBP sensor unit conversion tests passed");
    return 0;
}
