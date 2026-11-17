#ifndef SBP_BLE_SERVICE_H
#define SBP_BLE_SERVICE_H
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
#include "sbp_boot_diagnostics.h"
void sbp_ble_start(void);
void sbp_ble_publish_diagnostics(const sbp_boot_diagnostics_t *diagnostics);
void sbp_ble_publish(float voltage_v, bool voltage_valid,
                     float current_a, bool current_valid,
                     int16_t temperature_deci_c, bool temperature_valid,
                     int engine_state, int controller_state, int voltage_class);
#endif
