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
int main(void) {
    sbp_controller_t c;
    sbp_controller_init(&c);
    sbp_config_t cfg = config();
    sbp_measurements_t m = sample();

    sbp_output_t o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 0U);
    assert(o.state == SBP_STATE_MONITOR);

    /* Threshold must persist for the full qualification interval. */
    m.battery_voltage_v = 11.7f;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 100U);
    assert(!o.disconnect_request);
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 5099U);
    assert(!o.disconnect_request);
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 5100U);
    assert(o.disconnect_request && o.state == SBP_STATE_DISCONNECTED);

    /* Restore requires engine OFF, recovery voltage and its own delay. */
    m.battery_voltage_v = 12.8f;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_RESTORE, 5200U);
    assert(!o.restore_request && o.disconnect_request);
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_NONE, 10200U);
    assert(o.restore_request && !o.disconnect_request);

    /* Engine running or unknown blocks a disconnect request. */
    m = sample();
    m.engine = SBP_ENGINE_RUNNING;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_DISCONNECT, 11000U);
    assert(!o.disconnect_request && o.fault == SBP_FAULT_ENGINE_INTERLOCK);
    m.engine = SBP_ENGINE_UNKNOWN;
    o = sbp_controller_step(&c, &cfg, &m, SBP_REQUEST_DISCONNECT, 12000U);
    assert(!o.disconnect_request);

    /* Sensor/thermal/overcurrent faults lock automatic operation. */
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

    /* Uncommissioned defaults are monitor-only; invalid hysteresis rejected. */
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

    puts("SBP controller core tests passed");
    return 0;
}
