#include "sbp_boot_diagnostics.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static void test_valid_payload(void) {
    const sbp_boot_diagnostics_t diagnostics = {
        .reset_reason = SBP_BOOT_RESET_BROWNOUT,
        .nvs_state = SBP_BOOT_NVS_VALID_NOT_APPLIED,
        .sensor_state = SBP_BOOT_SENSOR_READY,
        .mode = SBP_BOOT_MODE_MONITOR_ONLY,
        .reason_flags = SBP_BOOT_REASON_PROTECTION_FORCED_OFF |
                        SBP_BOOT_REASON_CONFIG_NOT_APPLIED |
                        SBP_BOOT_REASON_SHUNT_UNCONFIGURED |
                        SBP_BOOT_REASON_ACTUATOR_NOT_IMPLEMENTED,
        .config_generation = 42U
    };
    char json[128];
    assert(sbp_boot_diagnostics_is_valid(&diagnostics));
    assert(sbp_boot_diagnostics_format_json(&diagnostics, json, sizeof(json)));
    assert(strcmp(json,
        "{\"v\":1,\"rr\":9,\"nv\":2,\"sn\":1,\"mo\":0,\"rf\":27,\"cg\":42}") == 0);
}

static void test_invalid_enums_and_flags(void) {
    sbp_boot_diagnostics_t diagnostics = {
        .reset_reason = 255U,
        .nvs_state = SBP_BOOT_NVS_MISSING,
        .sensor_state = SBP_BOOT_SENSOR_READY,
        .mode = SBP_BOOT_MODE_MONITOR_ONLY,
        .reason_flags = 0U,
        .config_generation = 0U
    };
    char json[128];
    assert(!sbp_boot_diagnostics_is_valid(&diagnostics));
    assert(!sbp_boot_diagnostics_format_json(&diagnostics, json, sizeof(json)));
    assert(json[0] == '\0');

    diagnostics.reset_reason = SBP_BOOT_RESET_POWER_ON;
    diagnostics.reason_flags = 1UL << 12;
    assert(!sbp_boot_diagnostics_is_valid(&diagnostics));

    diagnostics.reason_flags = 0U;
    diagnostics.mode = 1U;
    assert(!sbp_boot_diagnostics_is_valid(&diagnostics));
}

static void test_buffer_bounds_and_nulls(void) {
    const sbp_boot_diagnostics_t diagnostics = {
        .reset_reason = SBP_BOOT_RESET_OTHER,
        .nvs_state = SBP_BOOT_NVS_ERROR,
        .sensor_state = SBP_BOOT_SENSOR_INIT_FAILED,
        .mode = SBP_BOOT_MODE_MONITOR_ONLY,
        .reason_flags = SBP_BOOT_REASON_MASK,
        .config_generation = UINT32_MAX
    };
    char tiny[8];
    char json[128];
    assert(!sbp_boot_diagnostics_format_json(&diagnostics, tiny, sizeof(tiny)));
    assert(tiny[0] == '\0');
    assert(!sbp_boot_diagnostics_format_json(&diagnostics, NULL, sizeof(json)));
    assert(!sbp_boot_diagnostics_format_json(&diagnostics, json, 0U));
}

int main(void) {
    test_valid_payload();
    test_invalid_enums_and_flags();
    test_buffer_bounds_and_nulls();
    puts("SBP boot diagnostics tests passed");
    return 0;
}
