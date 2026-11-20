#include "safety_gate.h"
#include <assert.h>
int main(void) {
    sbp_interlocks_t ok = {true, false, true, false, false, true, false};
    assert(sbp_request_allowed(SBP_ACTION_OPEN, &ok));
    assert(sbp_request_allowed(SBP_ACTION_CLOSE, &ok));
    assert(sbp_request_allowed(SBP_ACTION_RECOVER, &ok));
    sbp_interlocks_t running = {true, true, true, false, false, true, false};
    assert(!sbp_request_allowed(SBP_ACTION_OPEN, &running));
    assert(!sbp_request_allowed(SBP_ACTION_CLOSE, &running));
    assert(!sbp_request_allowed(SBP_ACTION_RECOVER, &running));
    sbp_interlocks_t unknown = {true, false, false, false, false, true, false};
    assert(!sbp_request_allowed(SBP_ACTION_OPEN, &unknown));
    assert(!sbp_request_allowed(SBP_ACTION_CLOSE, &unknown));
    assert(!sbp_request_allowed(SBP_ACTION_RECOVER, &unknown));
    sbp_interlocks_t sensor_bad = {false, false, true, false, false, true, false};
    assert(!sbp_request_allowed(SBP_ACTION_OPEN, &sensor_bad));
    sbp_interlocks_t hot = {true, false, true, true, false, true, false};
    assert(!sbp_request_allowed(SBP_ACTION_RECOVER, &hot));
    sbp_interlocks_t latched = {true, false, true, false, false, true, true};
    assert(!sbp_request_allowed(SBP_ACTION_CLOSE, &latched));
    assert(!sbp_request_allowed(SBP_ACTION_OPEN, 0));
    return 0;
}
