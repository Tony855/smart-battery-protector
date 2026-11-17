#ifndef SBP_BOOT_DIAGNOSTICS_H
#define SBP_BOOT_DIAGNOSTICS_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define SBP_BOOT_DIAGNOSTICS_SCHEMA_VERSION 1U

typedef enum {
    SBP_BOOT_RESET_UNKNOWN = 0,
    SBP_BOOT_RESET_POWER_ON = 1,
    SBP_BOOT_RESET_EXTERNAL = 2,
    SBP_BOOT_RESET_SOFTWARE = 3,
    SBP_BOOT_RESET_PANIC = 4,
    SBP_BOOT_RESET_INTERRUPT_WDT = 5,
    SBP_BOOT_RESET_TASK_WDT = 6,
    SBP_BOOT_RESET_OTHER_WDT = 7,
    SBP_BOOT_RESET_DEEP_SLEEP = 8,
    SBP_BOOT_RESET_BROWNOUT = 9,
    SBP_BOOT_RESET_SDIO = 10,
    SBP_BOOT_RESET_OTHER = 11
} sbp_boot_reset_reason_t;

typedef enum {
    SBP_BOOT_NVS_UNKNOWN = 0,
    SBP_BOOT_NVS_MISSING = 1,
    SBP_BOOT_NVS_VALID_NOT_APPLIED = 2,
    SBP_BOOT_NVS_INVALID = 3,
    SBP_BOOT_NVS_ERROR = 4
} sbp_boot_nvs_state_t;

typedef enum {
    SBP_BOOT_SENSOR_UNKNOWN = 0,
    SBP_BOOT_SENSOR_READY = 1,
    SBP_BOOT_SENSOR_INIT_FAILED = 2,
    SBP_BOOT_SENSOR_BUS_FAILED = 3,
    SBP_BOOT_SENSOR_INA228_FAILED = 4,
    SBP_BOOT_SENSOR_TMP117_FAILED = 5,
    SBP_BOOT_SENSOR_INA228_CONFIG_FAILED = 6
} sbp_boot_sensor_state_t;

typedef enum {
    SBP_BOOT_MODE_MONITOR_ONLY = 0
} sbp_boot_mode_t;

#define SBP_BOOT_REASON_PROTECTION_FORCED_OFF (1UL << 0)
#define SBP_BOOT_REASON_CONFIG_NOT_APPLIED (1UL << 1)
#define SBP_BOOT_REASON_SENSOR_INIT_FAILED (1UL << 2)
#define SBP_BOOT_REASON_SHUNT_UNCONFIGURED (1UL << 3)
#define SBP_BOOT_REASON_ACTUATOR_NOT_IMPLEMENTED (1UL << 4)
#define SBP_BOOT_REASON_MASK (0x1FUL)

typedef struct {
    uint8_t reset_reason;
    uint8_t nvs_state;
    uint8_t sensor_state;
    uint8_t mode;
    uint32_t reason_flags;
    uint32_t config_generation;
} sbp_boot_diagnostics_t;

bool sbp_boot_diagnostics_is_valid(const sbp_boot_diagnostics_t *diagnostics);
bool sbp_boot_diagnostics_format_json(const sbp_boot_diagnostics_t *diagnostics,
                                      char *buffer, size_t capacity);

#endif
