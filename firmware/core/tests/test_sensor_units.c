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

    /* The protected battery-sense input and API accept at most 60.0 V. */
    assert(sbp_ina228_bus_voltage_v(307200U << 4U, &volts));
    assert(fabsf(volts - 60.0f) < 0.001f);
    volts = 123.0f;
    assert(!sbp_ina228_bus_voltage_v(307201U << 4U, &volts));
    assert(volts == 123.0f);
    assert(!sbp_ina228_bus_voltage_v(0xFFFFFFU, &volts));
    assert(volts == 123.0f);
    assert(!sbp_ina228_bus_voltage_v(0x1000000U, &volts));
    assert(volts == 123.0f);
    assert(!sbp_ina228_bus_voltage_v(61440U << 4U, NULL));

    float amps = 0.0f;
    /* +10 mV across 1 mOhm = +10 A. */
    uint32_t positive_code = (uint32_t)(0.010f / 0.0000003125f);
    assert(sbp_ina228_shunt_current_a(positive_code << 4U, 0.001f, &amps));
    assert(fabsf(amps - 10.0f) < 0.02f);
    /* -10 mV signed two's-complement VSHUNT. */
    int32_t negative_code = -(int32_t)positive_code;
    uint32_t negative_register = ((uint32_t)negative_code & 0xFFFFFU) << 4U;
    assert(sbp_ina228_shunt_current_a(negative_register, 0.001f, &amps));
    assert(fabsf(amps + 10.0f) < 0.02f);

    /* Both signed ADC rail codes are saturation, not valid measurements. */
    amps = 123.0f;
    assert(!sbp_ina228_shunt_current_a(0x7FFFF0U, 0.001f, &amps));
    assert(amps == 123.0f);
    assert(!sbp_ina228_shunt_current_a(0x800000U, 0.001f, &amps));
    assert(amps == 123.0f);
    assert(sbp_ina228_shunt_current_a(0x7FFFE0U, 0.001f, &amps));
    assert(sbp_ina228_shunt_current_a(0x800010U, 0.001f, &amps));

    /* Invalid shunt calibration and register values must not modify outputs. */
    amps = 321.0f;
    assert(!sbp_ina228_shunt_current_a(0U, 0.0f, &amps));
    assert(amps == 321.0f);
    assert(!sbp_ina228_shunt_current_a(0U, -0.001f, &amps));
    assert(amps == 321.0f);
    assert(!sbp_ina228_shunt_current_a(0U, 1.0001f, &amps));
    assert(amps == 321.0f);
    assert(!sbp_ina228_shunt_current_a(0U, NAN, &amps));
    assert(amps == 321.0f);
    assert(!sbp_ina228_shunt_current_a(0U, INFINITY, &amps));
    assert(amps == 321.0f);
    assert(!sbp_ina228_shunt_current_a(0x1000000U, 0.001f, &amps));
    assert(amps == 321.0f);
    assert(!sbp_ina228_shunt_current_a(0U, 0.001f, NULL));
    /* A positive subnormal shunt can overflow the derived current; reject it
       without replacing the caller's last known value with infinity. */
    assert(!sbp_ina228_shunt_current_a(
        0x7FFFE0U, nextafterf(0.0f, 1.0f), &amps));
    assert(amps == 321.0f);

    int16_t temp = 0;
    /* TMP117 raw 0x0C80 = 25.0°C -> 250 deci-degrees. */
    assert(sbp_tmp117_temperature_deci_c(0x0C80U, &temp));
    assert(temp == 250);
    /* -10.0°C */
    assert(sbp_tmp117_temperature_deci_c((uint16_t)(int16_t)-1280, &temp));
    assert(temp == -100);
    /* Signed conversion endpoints and out-of-range sensor values. */
    assert(sbp_tmp117_temperature_deci_c((uint16_t)(int16_t)-7040, &temp));
    assert(temp == -550);
    assert(sbp_tmp117_temperature_deci_c(19200U, &temp));
    assert(temp == 1500);
    temp = 1234;
    assert(!sbp_tmp117_temperature_deci_c((uint16_t)(int16_t)-7041, &temp));
    assert(temp == 1234);
    assert(!sbp_tmp117_temperature_deci_c(19201U, &temp));
    assert(temp == 1234);
    assert(!sbp_tmp117_temperature_deci_c(0x8000U, &temp));
    assert(temp == 1234);
    assert(!sbp_tmp117_temperature_deci_c(0U, NULL));

    puts("SBP sensor unit conversion tests passed");
    return 0;
}
