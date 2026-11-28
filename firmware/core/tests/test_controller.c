#include "sbp_controller.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>

static sbp_config_t config(void) {
    return (sbp_config_t){
        .variant = SBP_VARIANT_MAIN,
        .protection_enabled = true,
        .low_voltage_v = 11.8f,
        .recovery_voltage_v = 12.6f,
        .max_current_a = 150.0f,
        .max_temperature_deci_c = 800,
        .low_voltage_qualify_ms = 5000U,
        .recovery_qualify_ms = 5000U
    };
}
static sbp_measurements_t sample(void) {
    return (sbp_measurements_t){
        .sensors_valid = true, .battery_voltage_v = 12.4f,
        .battery_current_a = 4.0f, .temperature_deci_c = 250,
        .engine = SBP_ENGINE_OFF, .actuator = SBP_ACTUATOR_CLOSED
    };
}

static void test_engine_interlock_after_disconnect_and_during_recovery(void) {
    sbp_controller_t c;
    sbp_controller_init(&c);
    sbp_config_t cfg = config();
    sbp_measurements_t m = sample();
    m.battery_voltage_v = 11.7f;

    (void)sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 0U);
    sbp_output_t o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 5000U);
    assert(o.state == SBP_STATE_DISCONNECTED && o.disconnect_request);

    m.engine = SBP_ENGINE_RUNNING;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 6000U);
    assert(o.state == SBP_STATE_DISCONNECTED);
    assert(!o.disconnect_request && o.fault == SBP_FAULT_ENGINE_INTERLOCK);

    m.engine = SBP_ENGINE_UNKNOWN;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 7000U);
    assert(!o.disconnect_request);

    m.engine = SBP_ENGINE_OFF;
    m.battery_voltage_v = 12.8f;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_RESTORE, 8000U);
    assert(o.state == SBP_STATE_RECOVERY_QUALIFY && o.disconnect_request);

    m.engine = SBP_ENGINE_RUNNING;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 9000U);
    assert(o.state == SBP_STATE_DISCONNECTED);
    assert(!o.disconnect_request && o.fault == SBP_FAULT_ENGINE_INTERLOCK);
}

static void test_invalid_enum_values_fail_closed(void) {
    sbp_controller_t c;
    sbp_config_t cfg = config();
    sbp_measurements_t m = sample();
    sbp_output_t o;

    sbp_controller_init(&c);
    m.engine = (sbp_engine_state_t)99;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 0U);
    assert(o.state == SBP_STATE_FAULT_LOCKED);
    assert(o.fault == SBP_FAULT_ENGINE_INTERLOCK && !o.disconnect_request);

    sbp_controller_init(&c);
    m = sample();
    m.actuator = (sbp_actuator_state_t)99;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 0U);
    assert(o.state == SBP_STATE_FAULT_LOCKED);
    assert(o.fault == SBP_FAULT_ACTUATOR_FEEDBACK && !o.disconnect_request);

    sbp_controller_init(&c);
    m = sample();
    c.state = (sbp_state_t)99;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 0U);
    assert(o.state == SBP_STATE_FAULT_LOCKED);
    assert(o.fault == SBP_FAULT_CONFIG && !o.disconnect_request);

    sbp_controller_init(&c);
    m = sample();
    o = sbp_controller_step(&c, &cfg, &m, (sbp_request_t)99, 0U);
    assert(o.state == SBP_STATE_FAULT_LOCKED);
    assert(o.fault == SBP_FAULT_CONFIG && !o.disconnect_request);
}


static void test_qualification_duration_bounds(void) {
    sbp_controller_t c;
    sbp_config_t cfg = config();
    sbp_measurements_t m = sample();

    cfg.low_voltage_qualify_ms = 600001U;
    assert(!sbp_config_is_valid(&cfg));
    sbp_controller_init(&c);
    sbp_output_t o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 0U);
    assert(o.state == SBP_STATE_FAULT_LOCKED && !o.disconnect_request);

    cfg = config();
    cfg.recovery_qualify_ms = UINT32_MAX;
    assert(!sbp_config_is_valid(&cfg));
    sbp_controller_init(&c);
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 0U);
    assert(o.state == SBP_STATE_FAULT_LOCKED && !o.disconnect_request);

    cfg = config();
    cfg.low_voltage_qualify_ms = 1000U;
    cfg.recovery_qualify_ms = 600000U;
    assert(sbp_config_is_valid(&cfg));
}

static void test_qualification_timers_survive_uint32_wraparound(void) {
    sbp_controller_t c;
    sbp_controller_init(&c);
    sbp_config_t cfg = config();
    sbp_measurements_t m = sample();
    m.battery_voltage_v = 11.7f;

    const uint32_t low_start = UINT32_MAX - 3000U;
    sbp_output_t o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, low_start);
    assert(o.state == SBP_STATE_LOW_VOLTAGE_QUALIFY && !o.disconnect_request);
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 999U);
    assert(o.state == SBP_STATE_LOW_VOLTAGE_QUALIFY && !o.disconnect_request);
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 1999U);
    assert(o.state == SBP_STATE_DISCONNECTED && o.disconnect_request);

    m.battery_voltage_v = 12.8f;
    const uint32_t recovery_start = UINT32_MAX - 3000U;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_RESTORE, recovery_start);
    assert(o.state == SBP_STATE_RECOVERY_QUALIFY && o.disconnect_request);
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 999U);
    assert(o.state == SBP_STATE_RECOVERY_QUALIFY && o.disconnect_request);
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 1999U);
    assert(o.state == SBP_STATE_MONITOR && o.restore_request);
}

int main(void) {
    sbp_controller_t c;
    sbp_controller_init(&c);
    sbp_config_t cfg = config();
    sbp_measurements_t m = sample();

    sbp_output_t o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 0U);
    assert(o.state == SBP_STATE_MONITOR);

    m.battery_voltage_v = 11.7f;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 100U);
    assert(!o.disconnect_request);
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 5099U);
    assert(!o.disconnect_request);
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 5100U);
    assert(o.disconnect_request && o.state == SBP_STATE_DISCONNECTED);

    m.battery_voltage_v = 12.8f;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_RESTORE, 5200U);
    assert(!o.restore_request && o.disconnect_request);
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 10200U);
    assert(o.restore_request && !o.disconnect_request);

    m = sample();
    m.engine = SBP_ENGINE_RUNNING;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_DISCONNECT, 11000U);
    assert(!o.disconnect_request && o.fault == SBP_FAULT_ENGINE_INTERLOCK);
    m.engine = SBP_ENGINE_UNKNOWN;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_DISCONNECT, 12000U);
    assert(!o.disconnect_request);

    m = sample(); m.sensors_valid = false;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 13000U);
    assert(o.state == SBP_STATE_FAULT_LOCKED && !o.disconnect_request);
    sbp_controller_init(&c);
    m = sample(); m.temperature_deci_c = 810;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 14000U);
    assert(o.fault == SBP_FAULT_OVERTEMPERATURE);
    sbp_controller_init(&c);
    m = sample(); m.battery_current_a = 151.0f;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 15000U);
    assert(o.fault == SBP_FAULT_OVERCURRENT);

    sbp_controller_init(&c);
    cfg.protection_enabled = false;
    m = sample();
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_DISCONNECT, 16000U);
    assert(o.state == SBP_STATE_MONITOR_ONLY && !o.disconnect_request);
    cfg.protection_enabled = true;
    cfg.recovery_voltage_v = cfg.low_voltage_v;
    assert(!sbp_config_is_valid(&cfg));
    cfg = config();
    cfg.low_voltage_v = NAN;
    assert(!sbp_config_is_valid(&cfg));

    test_engine_interlock_after_disconnect_and_during_recovery();
    test_invalid_enum_values_fail_closed();
    test_qualification_duration_bounds();
    test_qualification_timers_survive_uint32_wraparound();
    puts("SBP controller core tests passed");
    return 0;
}
