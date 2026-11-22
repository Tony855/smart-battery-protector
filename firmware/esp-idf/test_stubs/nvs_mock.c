#include "nvs.h"
#include "nvs_flash.h"
#include "nvs_mock.h"

#include <string.h>

#define MOCK_KEY_COUNT 3
#define MOCK_VALUE_MAX 64

typedef struct {
    char key[16];
    bool present;
    size_t size;
    uint8_t bytes[MOCK_VALUE_MAX];
} mock_entry_t;

static mock_entry_t durable[MOCK_KEY_COUNT];
static mock_entry_t pending[MOCK_KEY_COUNT];
static bool namespace_present;
static bool fail_commit;
static bool fail_set_blob;
static bool fail_get_blob_query;
static bool fail_get_blob_read;
static bool fail_readback_after_commit;

static const char *const known_keys[MOCK_KEY_COUNT] = {
    "record_a", "record_b", "record_v1"
};

static int find_key(const char *key) {
    for (int i = 0; i < MOCK_KEY_COUNT; ++i) {
        if (strcmp(key, known_keys[i]) == 0) return i;
    }
    return -1;
}

void nvs_mock_reset(void) {
    memset(durable, 0, sizeof(durable));
    memset(pending, 0, sizeof(pending));
    namespace_present = false;
    fail_commit = false;
    fail_set_blob = false;
    fail_get_blob_query = false;
    fail_get_blob_read = false;
    fail_readback_after_commit = false;
}

void nvs_mock_seed(const char *key, const uint8_t *data, size_t size) {
    int index = find_key(key);
    if (index < 0 || size > MOCK_VALUE_MAX || (size > 0U && data == NULL)) return;
    (void)strncpy(durable[index].key, key, sizeof(durable[index].key) - 1U);
    durable[index].present = true;
    durable[index].size = size;
    if (size > 0U) memcpy(durable[index].bytes, data, size);
    namespace_present = true;
}

bool nvs_mock_has_key(const char *key) {
    int index = find_key(key);
    return index >= 0 && durable[index].present;
}

void nvs_mock_fail_next_commit(void) {
    fail_commit = true;
}

void nvs_mock_fail_next_set_blob(void) {
    fail_set_blob = true;
}

void nvs_mock_fail_next_get_blob_query(void) {
    fail_get_blob_query = true;
}

void nvs_mock_fail_next_get_blob_read(void) {
    fail_get_blob_read = true;
}

void nvs_mock_fail_next_readback_after_commit(void) {
    fail_readback_after_commit = true;
}

esp_err_t nvs_flash_init(void) {
    return ESP_OK;
}

esp_err_t nvs_open(const char *name, int open_mode, nvs_handle_t *out_handle) {
    if (name == NULL || out_handle == NULL) return ESP_ERR_INVALID_ARG;
    if (strcmp(name, "sbp_cfg") != 0) return ESP_ERR_INVALID_ARG;
    if (open_mode == NVS_READONLY && !namespace_present) return ESP_ERR_NVS_NOT_FOUND;
    if (open_mode == NVS_READWRITE) namespace_present = true;
    *out_handle = 1;
    return ESP_OK;
}

void nvs_close(nvs_handle_t handle) {
    (void)handle;
}

esp_err_t nvs_get_blob(nvs_handle_t handle, const char *key, void *out_value,
                       size_t *length) {
    if (handle != 1 || key == NULL || length == NULL) return ESP_ERR_INVALID_ARG;
    int index = find_key(key);
    if (index < 0 || !durable[index].present) return ESP_ERR_NVS_NOT_FOUND;
    if (out_value == NULL) {
        if (fail_get_blob_query) {
            fail_get_blob_query = false;
            return ESP_FAIL;
        }
        *length = durable[index].size;
        return ESP_OK;
    }
    if (fail_get_blob_read) {
        fail_get_blob_read = false;
        return ESP_FAIL;
    }
    if (*length < durable[index].size) return ESP_ERR_INVALID_SIZE;
    memcpy(out_value, durable[index].bytes, durable[index].size);
    *length = durable[index].size;
    return ESP_OK;
}

esp_err_t nvs_set_blob(nvs_handle_t handle, const char *key,
                       const void *value, size_t length) {
    if (handle != 1 || key == NULL || value == NULL || length > MOCK_VALUE_MAX) {
        return ESP_ERR_INVALID_ARG;
    }
    if (fail_set_blob) {
        fail_set_blob = false;
        return ESP_FAIL;
    }
    int index = find_key(key);
    if (index < 0) return ESP_ERR_INVALID_ARG;
    (void)strncpy(pending[index].key, key, sizeof(pending[index].key) - 1U);
    pending[index].present = true;
    pending[index].size = length;
    memcpy(pending[index].bytes, value, length);
    return ESP_OK;
}

esp_err_t nvs_commit(nvs_handle_t handle) {
    if (handle != 1) return ESP_ERR_INVALID_ARG;
    if (fail_commit) {
        fail_commit = false;
        memset(pending, 0, sizeof(pending));
        return ESP_FAIL;
    }
    for (int i = 0; i < MOCK_KEY_COUNT; ++i) {
        if (pending[i].present) durable[i] = pending[i];
    }
    memset(pending, 0, sizeof(pending));
    if (fail_readback_after_commit) {
        fail_readback_after_commit = false;
        fail_get_blob_read = true;
    }
    return ESP_OK;
}
