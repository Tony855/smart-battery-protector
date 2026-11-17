#ifndef SBP_VOLTAGE_CLASS_H
#define SBP_VOLTAGE_CLASS_H
#include <stdbool.h>
#include <stdint.h>

typedef enum {
    SBP_VOLTAGE_UNKNOWN = 0,
    SBP_VOLTAGE_12V = 12,
    SBP_VOLTAGE_24V = 24
} sbp_voltage_class_t;

typedef struct {
    sbp_voltage_class_t locked_class;
    sbp_voltage_class_t candidate_class;
    uint32_t candidate_since_ms;
    bool candidate_active;
} sbp_voltage_classifier_t;

void sbp_voltage_classifier_init(sbp_voltage_classifier_t *classifier);
/* Preliminary conservative windows; classification locks until explicit re-init/power cycle. */
sbp_voltage_class_t sbp_voltage_classifier_update(
    sbp_voltage_classifier_t *classifier, float measured_voltage_v,
    uint32_t now_ms, uint32_t stable_time_ms);
#endif
