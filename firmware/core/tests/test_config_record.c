#include "sbp_config_record.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static sbp_config_record_t sample(void) {
    return (sbp_config_record_t){
        .generation = 42U,
        .variant = 1U,
        .protection_enabled = true,
        .low_voltage_12v_mv = 11800U,
        .recovery_voltage_12v_mv = 12600U,
        .low_voltage_24v_mv = 23600U,
        .recovery_voltage_24v_mv = 25200U,
        .max_current_ma = 150000U,
        .max_temperature_deci_c = 800,
        .low_voltage_qualify_ms = 30000U,
        .recovery_voltage_qualify_ms = 30000U,
        .shunt_micro_ohm = 500U
    };
}

int main(void) {
    uint8_t bytes[SBP_CONFIG_RECORD_SIZE];
    sbp_config_record_t original = sample();
    sbp_config_record_t decoded = {0};
    assert(sbp_config_record_encode(&original, bytes));
    assert(sbp_config_record_decode(bytes, sizeof(bytes), &decoded));
    assert(decoded.generation == original.generation);
    assert(decoded.variant == original.variant);
    assert(decoded.protection_enabled == original.protection_enabled);
    assert(decoded.low_voltage_12v_mv == original.low_voltage_12v_mv);
    assert(decoded.recovery_voltage_24v_mv == original.recovery_voltage_24v_mv);
    assert(decoded.max_current_ma == original.max_current_ma);
    assert(decoded.max_temperature_deci_c == original.max_temperature_deci_c);
    assert(decoded.shunt_micro_ohm == original.shunt_micro_ohm);

    bytes[20] ^= 0x01U;
    assert(!sbp_config_record_decode(bytes, sizeof(bytes), &decoded));
    assert(!sbp_config_record_decode(bytes, sizeof(bytes) - 1U, &decoded));

    original = sample();
    original.recovery_voltage_12v_mv = original.low_voltage_12v_mv;
    assert(!sbp_config_record_encode(&original, bytes));

    original = sample();
    original.protection_enabled = false;
    original.low_voltage_12v_mv = 0U;
    original.recovery_voltage_12v_mv = 0U;
    original.low_voltage_24v_mv = 0U;
    original.recovery_voltage_24v_mv = 0U;
    original.max_current_ma = 0U;
    original.shunt_micro_ohm = 0U;
    assert(sbp_config_record_encode(&original, bytes));
    assert(sbp_config_record_decode(bytes, sizeof(bytes), &decoded));
    assert(!decoded.protection_enabled);

    puts("SBP config record tests passed");
    return 0;
}
