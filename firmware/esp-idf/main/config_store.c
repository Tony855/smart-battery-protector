#include "config_store.h"

#include <string.h>

#include "nvs.h"
#include "nvs_flash.h"

#define SBP_NVS_NAMESPACE "sbp_cfg"
#define SBP_NVS_KEY "record_v1"

esp_err_t sbp_config_store_init(void) {
    /* Never erase NVS automatically: a version/partition issue must not silently
       destroy a previously commissioned configuration. */
    return nvs_flash_init();
}

esp_err_t sbp_config_store_load(sbp_config_record_t *record) {
    if (record == NULL) return ESP_ERR_INVALID_ARG;
    nvs_handle_t handle;
    esp_err_t err = nvs_open(SBP_NVS_NAMESPACE, NVS_READONLY, &handle);
    if (err != ESP_OK) return err;

    size_t size = 0U;
    err = nvs_get_blob(handle, SBP_NVS_KEY, NULL, &size);
    if (err == ESP_OK && size != SBP_CONFIG_RECORD_SIZE) err = ESP_ERR_INVALID_SIZE;

    uint8_t bytes[SBP_CONFIG_RECORD_SIZE];
    if (err == ESP_OK) err = nvs_get_blob(handle, SBP_NVS_KEY, bytes, &size);
    nvs_close(handle);
    if (err != ESP_OK) return err;
    if (!sbp_config_record_decode(bytes, size, record)) return ESP_ERR_INVALID_RESPONSE;
    return ESP_OK;
}

esp_err_t sbp_config_store_save(const sbp_config_record_t *record) {
    if (!sbp_config_record_is_valid(record)) return ESP_ERR_INVALID_ARG;
    uint8_t bytes[SBP_CONFIG_RECORD_SIZE];
    if (!sbp_config_record_encode(record, bytes)) return ESP_ERR_INVALID_ARG;

    nvs_handle_t handle;
    esp_err_t err = nvs_open(SBP_NVS_NAMESPACE, NVS_READWRITE, &handle);
    if (err != ESP_OK) return err;
    err = nvs_set_blob(handle, SBP_NVS_KEY, bytes, sizeof(bytes));
    if (err == ESP_OK) err = nvs_commit(handle);
    nvs_close(handle);
    return err;
}
