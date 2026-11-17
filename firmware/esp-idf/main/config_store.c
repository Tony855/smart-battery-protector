#include "config_store.h"

#include <string.h>

#include "nvs.h"
#include "nvs_flash.h"

#define SBP_NVS_NAMESPACE "sbp_cfg"
#define SBP_NVS_SLOT_A "record_a"
#define SBP_NVS_SLOT_B "record_b"
/* Read-only migration source from the original single-record implementation. */
#define SBP_NVS_LEGACY_KEY "record_v1"

typedef enum {
    RECORD_MISSING = 0,
    RECORD_VALID,
    RECORD_CORRUPT,
    RECORD_ERROR
} record_state_t;

typedef struct {
    record_state_t state;
    esp_err_t error;
    sbp_config_record_t record;
    uint8_t bytes[SBP_CONFIG_RECORD_SIZE];
} stored_record_t;

static stored_record_t read_record(nvs_handle_t handle, const char *key) {
    stored_record_t result;
    memset(&result, 0, sizeof(result));
    result.state = RECORD_MISSING;

    size_t size = 0U;
    esp_err_t err = nvs_get_blob(handle, key, NULL, &size);
    if (err == ESP_ERR_NVS_NOT_FOUND) return result;
    if (err != ESP_OK) {
        result.state = RECORD_ERROR;
        result.error = err;
        return result;
    }
    if (size != SBP_CONFIG_RECORD_SIZE) {
        result.state = RECORD_CORRUPT;
        return result;
    }

    size = sizeof(result.bytes);
    err = nvs_get_blob(handle, key, result.bytes, &size);
    if (err != ESP_OK) {
        result.state = RECORD_ERROR;
        result.error = err;
        return result;
    }
    if (size != SBP_CONFIG_RECORD_SIZE ||
        !sbp_config_record_decode(result.bytes, size, &result.record)) {
        result.state = RECORD_CORRUPT;
        return result;
    }

    result.state = RECORD_VALID;
    return result;
}

static esp_err_t read_all(nvs_handle_t handle,
                          stored_record_t *slot_a,
                          stored_record_t *slot_b,
                          stored_record_t *legacy) {
    *slot_a = read_record(handle, SBP_NVS_SLOT_A);
    *slot_b = read_record(handle, SBP_NVS_SLOT_B);
    *legacy = read_record(handle, SBP_NVS_LEGACY_KEY);

    const stored_record_t *records[] = {slot_a, slot_b, legacy};
    for (size_t i = 0U; i < sizeof(records) / sizeof(records[0]); ++i) {
        if (records[i]->state == RECORD_ERROR) return records[i]->error;
    }
    return ESP_OK;
}

static bool any_corrupt(const stored_record_t *a,
                        const stored_record_t *b,
                        const stored_record_t *legacy) {
    return a->state == RECORD_CORRUPT ||
           b->state == RECORD_CORRUPT ||
           legacy->state == RECORD_CORRUPT;
}

/* Returns false for equal generations carrying different encoded data. */
static bool latest_valid(const stored_record_t *a,
                         const stored_record_t *b,
                         const stored_record_t *legacy,
                         const stored_record_t **latest) {
    const stored_record_t *records[] = {a, b, legacy};
    *latest = NULL;
    for (size_t i = 0U; i < sizeof(records) / sizeof(records[0]); ++i) {
        const stored_record_t *candidate = records[i];
        if (candidate->state != RECORD_VALID) continue;
        if (*latest == NULL ||
            candidate->record.generation > (*latest)->record.generation) {
            *latest = candidate;
        } else if (candidate->record.generation ==
                       (*latest)->record.generation &&
                   memcmp(candidate->bytes, (*latest)->bytes,
                          SBP_CONFIG_RECORD_SIZE) != 0) {
            return false;
        }
    }
    return true;
}

esp_err_t sbp_config_store_init(void) {
    /* Never erase NVS automatically: a partition/version issue must not
       silently destroy a previously commissioned configuration. */
    return nvs_flash_init();
}

esp_err_t sbp_config_store_load(sbp_config_record_t *record) {
    if (record == NULL) return ESP_ERR_INVALID_ARG;

    nvs_handle_t handle;
    esp_err_t err = nvs_open(SBP_NVS_NAMESPACE, NVS_READONLY, &handle);
    if (err != ESP_OK) return err;

    stored_record_t slot_a, slot_b, legacy;
    err = read_all(handle, &slot_a, &slot_b, &legacy);
    nvs_close(handle);
    if (err != ESP_OK) return err;

    const stored_record_t *latest = NULL;
    if (!latest_valid(&slot_a, &slot_b, &legacy, &latest)) {
        return ESP_ERR_INVALID_RESPONSE;
    }
    if (latest != NULL) {
        *record = latest->record;
        return ESP_OK;
    }
    return any_corrupt(&slot_a, &slot_b, &legacy)
               ? ESP_ERR_INVALID_RESPONSE
               : ESP_ERR_NVS_NOT_FOUND;
}

static const char *choose_write_slot(const stored_record_t *slot_a,
                                     const stored_record_t *slot_b,
                                     const stored_record_t *legacy) {
    if (slot_a->state == RECORD_VALID &&
        slot_b->state == RECORD_VALID) {
        /* Equal generations were already checked for byte-identical data.
           Keep A as the tie-break winner and write the other slot. */
        return slot_a->record.generation <= slot_b->record.generation
                   ? SBP_NVS_SLOT_A
                   : SBP_NVS_SLOT_B;
    }
    if (slot_a->state == RECORD_VALID) return SBP_NVS_SLOT_B;
    if (slot_b->state == RECORD_VALID) return SBP_NVS_SLOT_A;

    /* Prefer an absent slot so a corrupt record remains available for
       diagnosis. The valid legacy record, if any, is never modified. */
    if (slot_a->state == RECORD_MISSING) return SBP_NVS_SLOT_A;
    if (slot_b->state == RECORD_MISSING) return SBP_NVS_SLOT_B;
    if (legacy->state == RECORD_VALID) return SBP_NVS_SLOT_A;
    return NULL;
}

esp_err_t sbp_config_store_save(const sbp_config_record_t *record) {
    if (!sbp_config_record_is_valid(record)) return ESP_ERR_INVALID_ARG;

    uint8_t encoded[SBP_CONFIG_RECORD_SIZE];
    if (!sbp_config_record_encode(record, encoded)) return ESP_ERR_INVALID_ARG;

    nvs_handle_t handle;
    esp_err_t err = nvs_open(SBP_NVS_NAMESPACE, NVS_READWRITE, &handle);
    if (err != ESP_OK) return err;

    stored_record_t slot_a, slot_b, legacy;
    err = read_all(handle, &slot_a, &slot_b, &legacy);
    if (err != ESP_OK) {
        nvs_close(handle);
        return err;
    }

    const stored_record_t *latest = NULL;
    if (!latest_valid(&slot_a, &slot_b, &legacy, &latest)) {
        nvs_close(handle);
        return ESP_ERR_INVALID_RESPONSE;
    }
    if (latest != NULL && record->generation <= latest->record.generation) {
        nvs_close(handle);
        return ESP_ERR_INVALID_STATE;
    }
    /* If no valid generation survives, never guess around an unreadable
       record: its generation may be newer than the proposed record. */
    if (latest == NULL && any_corrupt(&slot_a, &slot_b, &legacy)) {
        nvs_close(handle);
        return ESP_ERR_INVALID_RESPONSE;
    }

    const char *target = choose_write_slot(&slot_a, &slot_b, &legacy);
    if (target == NULL) {
        nvs_close(handle);
        return ESP_ERR_INVALID_RESPONSE;
    }

    err = nvs_set_blob(handle, target, encoded, sizeof(encoded));
    if (err == ESP_OK) err = nvs_commit(handle);
    if (err == ESP_OK) {
        stored_record_t verify = read_record(handle, target);
        if (verify.state != RECORD_VALID ||
            memcmp(verify.bytes, encoded, sizeof(encoded)) != 0) {
            err = verify.state == RECORD_ERROR
                      ? verify.error
                      : ESP_ERR_INVALID_RESPONSE;
        }
    }
    nvs_close(handle);
    return err;
}
