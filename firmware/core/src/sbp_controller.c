#include "sbp_controller.h"

#include <stddef.h>
#include <math.h>

#define SBP_MIN_VOLTAGE_V 5.0f
#define SBP_MAX_VOLTAGE_V 40.0f
#define SBP_MAX_CURRENT_A 2000.0f
#define SBP_MIN_TEMP_DECI_C (-400)
#define SBP_MAX_TEMP_DECI_C 1500

static bool engine_is_safely_off(const sbp_measurements_t *m) {
    return m->engine == SBP_ENGINE_OFF;
}

bool sbp_config_is_valid(const sbp_config_t *c) {
    if (c == NULL) return false;
    if (c->variant != SBP_VARIANT_AUXILIARY && c->variant != SBP_VARIANT_MAIN) return false;
    if (!c->protection_enabled) return true;
    if (!isfinite(c->low_voltage_v) || !isfinite(c->recovery_voltage_v) ||
        !isfinite(c->max_current_a)) return false;
    if (c->low_voltage_v < SBP_MIN_VOLTAGE_V || c->low_voltage_v > SBP_MAX_VOLTAGE_V) return false;
    if (c->recovery_voltage_v <= c->low_voltage_v || c->recovery_voltage_v > SBP_MAX_VOLTAGE_V) return false;
    if (c->max_current_a <= 0.0f || c->max_current_a > SBP_MAX_CURRENT_A) return false;
    if (c->max_temperature_deci_c < SBP_MIN_TEMP_DECI_C ||
        c->max_temperature_deci_c > SBP_MAX_TEMP_DECI_C) return false;
    if (c->low_voltage_qualify_ms < 1000U || c->recovery_qualify_ms < 1000U) return false;
    return true;
}

void sbp_controller_init(sbp_controller_t *c) {
    if (c == NULL) return;
    c->state = SBP_STATE_BOOT;
    c->fault = SBP_FAULT_NONE;
    c->low_voltage_since_ms = 0U;
    c->recovery_since_ms = 0U;
    c->timers_started = false;
}

static sbp_output_t make_output(const sbp_controller_t *c, bool disconnect, bool restore, bool active) {
    sbp_output_t out = {
        .state = c->state,
        .fault = c->fault,
        .disconnect_request = disconnect,
        .restore_request = restore,
        .protection_active = active
    };
    return out;
}

sbp_output_t sbp_controller_step(
    sbp_controller_t *c,
    const sbp_config_t *config,
    const sbp_measurements_t *m,
    sbp_request_t request,
    uint32_t now_ms) {

    if (c == NULL || config == NULL || m == NULL) {
        sbp_controller_t invalid = { .state = SBP_STATE_FAULT_LOCKED, .fault = SBP_FAULT_CONFIG };
        return make_output(&invalid, false, false, false);
    }

    if (c->state == SBP_STATE_BOOT) c->state = SBP_STATE_SELF_TEST;

    if (!sbp_config_is_valid(config)) {
        c->state = SBP_STATE_FAULT_LOCKED;
        c->fault = SBP_FAULT_CONFIG;
        return make_output(c, false, false, false);
    }

    /* A disabled/uncommissioned device is a monitor-only product. */
    if (!config->protection_enabled) {
        c->state = SBP_STATE_MONITOR_ONLY;
        c->fault = SBP_FAULT_NONE;
        c->timers_started = false;
        return make_output(c, false, false, false);
    }

    if (!m->sensors_valid || !isfinite(m->battery_voltage_v) ||
        !isfinite(m->battery_current_a) || m->battery_voltage_v <= 0.0f ||
        m->battery_voltage_v > 40.0f || m->temperature_deci_c < -550 ||
        m->temperature_deci_c > 1500) {
        c->state = SBP_STATE_FAULT_LOCKED;
        c->fault = SBP_FAULT_SENSOR;
        c->timers_started = false;
        return make_output(c, false, false, false);
    }

    if (m->actuator == SBP_ACTUATOR_UNKNOWN) {
        c->state = SBP_STATE_FAULT_LOCKED;
        c->fault = SBP_FAULT_ACTUATOR_FEEDBACK;
        c->timers_started = false;
        return make_output(c, false, false, false);
    }

    if (m->temperature_deci_c > config->max_temperature_deci_c) {
        c->state = SBP_STATE_FAULT_LOCKED;
        c->fault = SBP_FAULT_OVERTEMPERATURE;
        c->timers_started = false;
        return make_output(c, engine_is_safely_off(m) && m->actuator == SBP_ACTUATOR_CLOSED,
                           false, true);
    }

    if (m->battery_current_a > config->max_current_a ||
        m->battery_current_a < -config->max_current_a) {
        c->state = SBP_STATE_FAULT_LOCKED;
        c->fault = SBP_FAULT_OVERCURRENT;
        c->timers_started = false;
        return make_output(c, engine_is_safely_off(m) && m->actuator == SBP_ACTUATOR_CLOSED,
                           false, true);
    }

    if (c->fault == SBP_FAULT_ENGINE_INTERLOCK && engine_is_safely_off(m)) {
        c->fault = SBP_FAULT_NONE;
    }

    if (c->state == SBP_STATE_FAULT_LOCKED) {
        if (request == SBP_REQUEST_CLEAR_FAULT &&
            m->actuator == SBP_ACTUATOR_CLOSED &&
            engine_is_safely_off(m)) {
            c->state = SBP_STATE_MONITOR;
            c->fault = SBP_FAULT_NONE;
        } else {
            return make_output(c, false, false, false);
        }
    }

    if (request == SBP_REQUEST_DISCONNECT) {
        if (!engine_is_safely_off(m)) {
            c->fault = SBP_FAULT_ENGINE_INTERLOCK;
            return make_output(c, false, false, false);
        }
        c->state = SBP_STATE_DISCONNECTED;
        c->fault = SBP_FAULT_NONE;
        c->timers_started = false;
        return make_output(c, true, false, true);
    }

    if (c->state == SBP_STATE_DISCONNECTED &&
        request == SBP_REQUEST_RESTORE && engine_is_safely_off(m) &&
        m->battery_voltage_v >= config->recovery_voltage_v) {
        c->state = SBP_STATE_RECOVERY_QUALIFY;
        c->recovery_since_ms = now_ms;
        c->timers_started = true;
    }

    if (c->state == SBP_STATE_RECOVERY_QUALIFY) {
        if (!engine_is_safely_off(m) || m->battery_voltage_v < config->recovery_voltage_v) {
            c->state = SBP_STATE_DISCONNECTED;
            c->timers_started = false;
        } else if ((uint32_t)(now_ms - c->recovery_since_ms) >= config->recovery_qualify_ms) {
            c->state = SBP_STATE_MONITOR;
            c->timers_started = false;
            return make_output(c, false, true, false);
        }
        return make_output(c, true, false, true);
    }

    if (c->state == SBP_STATE_DISCONNECTED) {
        return make_output(c, true, false, true);
    }

    /* Main and auxiliary variants share the conservative engine-off interlock. */
    if (!engine_is_safely_off(m)) {
        c->state = SBP_STATE_MONITOR;
        c->timers_started = false;
        if (request == SBP_REQUEST_DISCONNECT) c->fault = SBP_FAULT_ENGINE_INTERLOCK;
        return make_output(c, false, false, false);
    }

    if (request == SBP_REQUEST_RESTORE) {
        c->state = SBP_STATE_MONITOR;
        c->timers_started = false;
        return make_output(c, false, false, false);
    }

    if (m->battery_voltage_v <= config->low_voltage_v) {
        if (c->state != SBP_STATE_LOW_VOLTAGE_QUALIFY || !c->timers_started) {
            c->state = SBP_STATE_LOW_VOLTAGE_QUALIFY;
            c->low_voltage_since_ms = now_ms;
            c->timers_started = true;
        } else if ((uint32_t)(now_ms - c->low_voltage_since_ms) >= config->low_voltage_qualify_ms) {
            c->state = SBP_STATE_DISCONNECTED;
            c->timers_started = false;
            return make_output(c, true, false, true);
        }
    } else {
        c->state = SBP_STATE_MONITOR;
        c->timers_started = false;
    }

    return make_output(c, false, false, false);
}
