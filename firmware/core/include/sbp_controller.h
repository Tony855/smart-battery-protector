#ifndef SBP_CONTROLLER_H
#define SBP_CONTROLLER_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    SBP_VARIANT_AUXILIARY = 0,
    SBP_VARIANT_MAIN = 1
} sbp_variant_t;

typedef enum {
    SBP_ENGINE_UNKNOWN = 0,
    SBP_ENGINE_OFF = 1,
    SBP_ENGINE_RUNNING = 2
} sbp_engine_state_t;

typedef enum {
    SBP_ACTUATOR_UNKNOWN = 0,
    SBP_ACTUATOR_CLOSED = 1,
    SBP_ACTUATOR_OPEN = 2
} sbp_actuator_state_t;

typedef enum {
    SBP_STATE_BOOT = 0,
    SBP_STATE_SELF_TEST,
    SBP_STATE_MONITOR_ONLY,
    SBP_STATE_MONITOR,
    SBP_STATE_LOW_VOLTAGE_QUALIFY,
    SBP_STATE_DISCONNECTED,
    SBP_STATE_RECOVERY_QUALIFY,
    SBP_STATE_FAULT_LOCKED
} sbp_state_t;

typedef enum {
    SBP_FAULT_NONE = 0,
    SBP_FAULT_CONFIG,
    SBP_FAULT_SENSOR,
    SBP_FAULT_OVERCURRENT,
    SBP_FAULT_OVERTEMPERATURE,
    SBP_FAULT_ACTUATOR_FEEDBACK,
    SBP_FAULT_ENGINE_INTERLOCK
} sbp_fault_t;

typedef enum {
    SBP_REQUEST_NONE = 0,
    SBP_REQUEST_DISCONNECT,
    SBP_REQUEST_RESTORE,
    SBP_REQUEST_CLEAR_FAULT
} sbp_request_t;

typedef struct {
    sbp_variant_t variant;
    bool protection_enabled;
    float low_voltage_v;
    float recovery_voltage_v;
    float max_current_a;
    int16_t max_temperature_deci_c;
    uint32_t low_voltage_qualify_ms;
    uint32_t recovery_qualify_ms;
} sbp_config_t;

typedef struct {
    bool sensors_valid;
    float battery_voltage_v;
    float battery_current_a;
    int16_t temperature_deci_c;
    sbp_engine_state_t engine;
    sbp_actuator_state_t actuator;
} sbp_measurements_t;

typedef struct {
    sbp_state_t state;
    sbp_fault_t fault;
    bool disconnect_request;
    bool restore_request;
    bool protection_active;
} sbp_output_t;

typedef struct {
    sbp_state_t state;
    sbp_fault_t fault;
    uint32_t low_voltage_since_ms;
    uint32_t recovery_since_ms;
    bool timers_started;
} sbp_controller_t;

void sbp_controller_init(sbp_controller_t *controller);
bool sbp_config_is_valid(const sbp_config_t *config);
sbp_output_t sbp_controller_step(
    sbp_controller_t *controller,
    const sbp_config_t *config,
    const sbp_measurements_t *measurements,
    sbp_request_t request,
    uint32_t now_ms);

#endif
