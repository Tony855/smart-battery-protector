#include "sbp_voltage_class.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>


static void test_classification_stability_timer_wraparound(void) {
    sbp_voltage_classifier_t c;
    sbp_voltage_classifier_init(&c);
    const uint32_t start = UINT32_MAX - 3000U;
    assert(sbp_voltage_classifier_update(&c, 12.4f, start, 5000U) == SBP_VOLTAGE_UNKNOWN);
    assert(sbp_voltage_classifier_update(&c, 12.5f, 999U, 5000U) == SBP_VOLTAGE_UNKNOWN);
    assert(sbp_voltage_classifier_update(&c, 12.5f, 1999U, 5000U) == SBP_VOLTAGE_12V);
}

int main(void) {
    sbp_voltage_classifier_t c;
    sbp_voltage_classifier_init(&c);

    assert(sbp_voltage_classifier_update(&c, 12.4f, 0U, 5000U) == SBP_VOLTAGE_UNKNOWN);
    assert(sbp_voltage_classifier_update(&c, 12.5f, 4999U, 5000U) == SBP_VOLTAGE_UNKNOWN);
    assert(sbp_voltage_classifier_update(&c, 12.5f, 5000U, 5000U) == SBP_VOLTAGE_12V);
    /* Once classified, charging voltage changes cannot cause a live 12/24V switch. */
    assert(sbp_voltage_classifier_update(&c, 28.0f, 10000U, 5000U) == SBP_VOLTAGE_12V);

    sbp_voltage_classifier_init(&c);
    assert(sbp_voltage_classifier_update(&c, 17.0f, 0U, 5000U) == SBP_VOLTAGE_UNKNOWN);
    assert(sbp_voltage_classifier_update(&c, 17.0f, 6000U, 5000U) == SBP_VOLTAGE_UNKNOWN);
    assert(sbp_voltage_classifier_update(&c, 24.8f, 7000U, 5000U) == SBP_VOLTAGE_UNKNOWN);
    assert(sbp_voltage_classifier_update(&c, 25.0f, 12000U, 5000U) == SBP_VOLTAGE_24V);

    sbp_voltage_classifier_init(&c);
    assert(sbp_voltage_classifier_update(&c, 12.4f, 0U, 5000U) == SBP_VOLTAGE_UNKNOWN);
    assert(sbp_voltage_classifier_update(&c, NAN, 4000U, 5000U) == SBP_VOLTAGE_UNKNOWN);
    assert(sbp_voltage_classifier_update(&c, 12.4f, 5000U, 5000U) == SBP_VOLTAGE_UNKNOWN);
    assert(sbp_voltage_classifier_update(&c, 12.4f, 10000U, 5000U) == SBP_VOLTAGE_12V);

    sbp_voltage_classifier_init(&c);
    c.locked_class = (sbp_voltage_class_t)18;
    assert(sbp_voltage_classifier_update(&c, 12.4f, 0U, 5000U) == SBP_VOLTAGE_UNKNOWN);
    assert(sbp_voltage_classifier_update(&c, 12.4f, 5000U, 5000U) == SBP_VOLTAGE_UNKNOWN);
    assert(sbp_voltage_classifier_update(&c, 12.4f, 10000U, 5000U) == SBP_VOLTAGE_12V);

    sbp_voltage_classifier_init(&c);
    assert(sbp_voltage_classifier_update(&c, NAN, 0U, 1000U) == SBP_VOLTAGE_UNKNOWN);
    assert(sbp_voltage_classifier_update(&c, 8.0f, 1000U, 1000U) == SBP_VOLTAGE_UNKNOWN);
    test_classification_stability_timer_wraparound();
    puts("SBP voltage classification tests passed");
    return 0;
}
