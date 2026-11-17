#ifndef SBP_CONFIG_STORE_H
#define SBP_CONFIG_STORE_H

#include "esp_err.h"
#include "sbp_config_record.h"

esp_err_t sbp_config_store_init(void);
esp_err_t sbp_config_store_load(sbp_config_record_t *record);
esp_err_t sbp_config_store_save(const sbp_config_record_t *record);

#endif
