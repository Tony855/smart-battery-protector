#include "sbp_boot_diagnostics.h"

#include <stdio.h>

bool sbp_boot_diagnostics_is_valid(const sbp_boot_diagnostics_t *diagnostics) {
    if (diagnostics == NULL) return false;
    if (diagnostics->reset_reason > SBP_BOOT_RESET_OTHER) return false;
    if (diagnostics->nvs_state > SBP_BOOT_NVS_ERROR) return false;
    if (diagnostics->sensor_state > SBP_BOOT_SENSOR_INIT_FAILED) return false;
    if (diagnostics->mode != SBP_BOOT_MODE_MONITOR_ONLY) return false;
    if ((diagnostics->reason_flags & ~SBP_BOOT_REASON_MASK) != 0U) return false;
    return true;
}

bool sbp_boot_diagnostics_format_json(const sbp_boot_diagnostics_t *diagnostics,
                                      char *buffer, size_t capacity) {
    if (buffer == NULL || capacity == 0U) return false;
    buffer[0] = '\0';
    if (!sbp_boot_diagnostics_is_valid(diagnostics)) return false;

    const int length = snprintf(buffer, capacity,
        "{\"v\":%u,\"rr\":%u,\"nv\":%u,\"sn\":%u,"
        "\"mo\":%u,\"rf\":%lu,\"cg\":%lu}",
        (unsigned int)SBP_BOOT_DIAGNOSTICS_SCHEMA_VERSION,
        (unsigned int)diagnostics->reset_reason,
        (unsigned int)diagnostics->nvs_state,
        (unsigned int)diagnostics->sensor_state,
        (unsigned int)diagnostics->mode,
        (unsigned long)diagnostics->reason_flags,
        (unsigned long)diagnostics->config_generation);
    if (length < 0 || (size_t)length >= capacity) {
        buffer[0] = '\0';
        return false;
    }
    return true;
}
