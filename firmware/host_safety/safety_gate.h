#ifndef SBP_SAFETY_GATE_H
#define SBP_SAFETY_GATE_H
#include <stdbool.h>
typedef enum {
    SBP_ACTION_OPEN = 0,
    SBP_ACTION_CLOSE = 1,
    SBP_ACTION_RECOVER = 2
} sbp_action_t;
typedef struct {
    bool sensors_valid;
    bool engine_running;
    bool engine_state_known;
    bool over_temperature;
    bool over_current;
    bool actuator_feedback_valid;
    bool fault_latched;
} sbp_interlocks_t;
/* Pure decision helper for host-side tests. Not a complete safety controller.
 * Hardware design, diagnostics and independent protection remain mandatory. */
bool sbp_request_allowed(sbp_action_t action, const sbp_interlocks_t *i);
#endif
