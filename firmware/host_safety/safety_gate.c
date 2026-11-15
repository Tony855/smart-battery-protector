#include "safety_gate.h"
bool sbp_request_allowed(sbp_action_t action, const sbp_interlocks_t *i) {
    if (i == 0) return false;
    if (!i->sensors_valid || !i->actuator_feedback_valid) return false;
    if (i->over_temperature || i->over_current || i->fault_latched) return false;
    /* Main-power open is prohibited whenever engine-running is true OR uncertain. */
    if (action == SBP_ACTION_OPEN &&
        (i->engine_running || !i->engine_state_known)) return false;
    /* Recovery/close also requires known engine state; do not energize blindly. */
    if ((action == SBP_ACTION_CLOSE || action == SBP_ACTION_RECOVER) &&
        !i->engine_state_known) return false;
    if (action != SBP_ACTION_OPEN &&
        action != SBP_ACTION_CLOSE &&
        action != SBP_ACTION_RECOVER) return false;
    return true;
}
