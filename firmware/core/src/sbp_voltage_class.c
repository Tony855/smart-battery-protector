#include "sbp_voltage_class.h"
#include <math.h>
#include <stddef.h>

static sbp_voltage_class_t candidate_for_voltage(float voltage_v) {
    if (!isfinite(voltage_v)) return SBP_VOLTAGE_UNKNOWN;
    if (voltage_v >= 9.0f && voltage_v <= 16.5f) return SBP_VOLTAGE_12V;
    if (voltage_v >= 18.0f && voltage_v <= 33.0f) return SBP_VOLTAGE_24V;
    return SBP_VOLTAGE_UNKNOWN;
}

void sbp_voltage_classifier_init(sbp_voltage_classifier_t *c) {
    if (c == NULL) return;
    c->locked_class = SBP_VOLTAGE_UNKNOWN;
    c->candidate_class = SBP_VOLTAGE_UNKNOWN;
    c->candidate_since_ms = 0U;
    c->candidate_active = false;
}

sbp_voltage_class_t sbp_voltage_classifier_update(
    sbp_voltage_classifier_t *c, float voltage_v,
    uint32_t now_ms, uint32_t stable_time_ms) {
    if (c == NULL) return SBP_VOLTAGE_UNKNOWN;
    if (c->locked_class != SBP_VOLTAGE_UNKNOWN &&
        c->locked_class != SBP_VOLTAGE_12V &&
        c->locked_class != SBP_VOLTAGE_24V) {
        /* Corrupt retained state must not leak an invalid voltage class to policy/telemetry. */
        sbp_voltage_classifier_init(c);
        return SBP_VOLTAGE_UNKNOWN;
    }
    if (c->locked_class != SBP_VOLTAGE_UNKNOWN) return c->locked_class;

    /* Keep elapsed-time arithmetic bounded and aligned with persisted controller settings. */
    if (stable_time_ms < 1000U || stable_time_ms > 600000U) {
        c->candidate_class = SBP_VOLTAGE_UNKNOWN;
        c->candidate_active = false;
        c->candidate_since_ms = 0U;
        return SBP_VOLTAGE_UNKNOWN;
    }

    const sbp_voltage_class_t observed = candidate_for_voltage(voltage_v);
    if (observed == SBP_VOLTAGE_UNKNOWN) {
        c->candidate_class = SBP_VOLTAGE_UNKNOWN;
        c->candidate_active = false;
        c->candidate_since_ms = 0U;
        return SBP_VOLTAGE_UNKNOWN;
    }

    if (!c->candidate_active || c->candidate_class != observed) {
        c->candidate_class = observed;
        c->candidate_since_ms = now_ms;
        c->candidate_active = true;
        return SBP_VOLTAGE_UNKNOWN;
    }

    if ((uint32_t)(now_ms - c->candidate_since_ms) >= stable_time_ms) {
        c->locked_class = observed;
    }
    return c->locked_class;
}
