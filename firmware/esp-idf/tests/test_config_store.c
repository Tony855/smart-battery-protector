#include "config_store.h"
#include "nvs_mock.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static sbp_config_record_t make_record(uint32_t generation, uint8_t variant) {
    return (sbp_config_record_t){
        .generation = generation,
        .variant = variant,
        .protection_enabled = false,
        .low_voltage_qualify_ms = 30000U,
        .recovery_qualify_ms = 30000U
    };
}

static void seed_record(const char *key, const sbp_config_record_t *record) {
    uint8_t bytes[SBP_CONFIG_RECORD_SIZE];
    assert(sbp_config_record_encode(record, bytes));
    nvs_mock_seed(key, bytes, sizeof(bytes));
}

static void test_first_save_and_failed_commit(void) {
    nvs_mock_reset();
    sbp_config_record_t loaded;
    assert(sbp_config_store_load(&loaded) == ESP_ERR_NVS_NOT_FOUND);

    sbp_config_record_t first = make_record(1U, 0U);
    assert(sbp_config_store_save(&first) == ESP_OK);
    assert(nvs_mock_has_key("record_a"));
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 1U);

    sbp_config_record_t second = make_record(2U, 1U);
    nvs_mock_fail_next_commit();
    assert(sbp_config_store_save(&second) == ESP_FAIL);
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 1U);

    assert(sbp_config_store_save(&second) == ESP_OK);
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 2U);
    assert(sbp_config_store_save(&second) == ESP_ERR_INVALID_STATE);
}

static void test_corrupt_newest_slot_falls_back(void) {
    nvs_mock_reset();
    sbp_config_record_t first = make_record(10U, 0U);
    sbp_config_record_t second = make_record(11U, 1U);
    seed_record("record_a", &first);
    seed_record("record_b", &second);

    uint8_t corrupt[SBP_CONFIG_RECORD_SIZE] = {0};
    nvs_mock_seed("record_b", corrupt, sizeof(corrupt));

    sbp_config_record_t loaded;
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 10U);

    sbp_config_record_t third = make_record(12U, 0U);
    assert(sbp_config_store_save(&third) == ESP_OK);
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 12U);
}

static void test_legacy_migration_is_non_destructive(void) {
    nvs_mock_reset();
    sbp_config_record_t legacy = make_record(20U, 0U);
    seed_record("record_v1", &legacy);

    sbp_config_record_t loaded;
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 20U);

    sbp_config_record_t migrated = make_record(21U, 1U);
    assert(sbp_config_store_save(&migrated) == ESP_OK);
    assert(nvs_mock_has_key("record_v1"));
    assert(nvs_mock_has_key("record_a"));
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 21U);
}

static void test_corrupt_only_storage_is_not_overwritten(void) {
    nvs_mock_reset();
    uint8_t corrupt[SBP_CONFIG_RECORD_SIZE] = {0};
    nvs_mock_seed("record_a", corrupt, sizeof(corrupt));

    sbp_config_record_t loaded;
    sbp_config_record_t proposed = make_record(1U, 0U);
    assert(sbp_config_store_load(&loaded) == ESP_ERR_INVALID_RESPONSE);
    assert(sbp_config_store_save(&proposed) == ESP_ERR_INVALID_RESPONSE);
    assert(!nvs_mock_has_key("record_b"));
}

static void test_equal_generation_conflict_fails_closed(void) {
    nvs_mock_reset();
    sbp_config_record_t first = make_record(30U, 0U);
    sbp_config_record_t conflict = make_record(30U, 1U);
    seed_record("record_a", &first);
    seed_record("record_b", &conflict);

    sbp_config_record_t loaded;
    sbp_config_record_t proposed = make_record(31U, 0U);
    assert(sbp_config_store_load(&loaded) == ESP_ERR_INVALID_RESPONSE);
    assert(sbp_config_store_save(&proposed) == ESP_ERR_INVALID_RESPONSE);
}


static void test_failed_rotation_keeps_newest_slot(void) {
    nvs_mock_reset();
    sbp_config_record_t first = make_record(40U, 0U);
    sbp_config_record_t second = make_record(41U, 1U);
    seed_record("record_a", &first);
    seed_record("record_b", &second);

    sbp_config_record_t proposed = make_record(42U, 0U);
    sbp_config_record_t loaded;
    nvs_mock_fail_next_commit();
    assert(sbp_config_store_save(&proposed) == ESP_FAIL);
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 41U);

    assert(sbp_config_store_save(&proposed) == ESP_OK);
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 42U);
}

int main(void) {
    assert(sbp_config_store_init() == ESP_OK);
    test_first_save_and_failed_commit();
    test_failed_rotation_keeps_newest_slot();
    test_corrupt_newest_slot_falls_back();
    test_legacy_migration_is_non_destructive();
    test_corrupt_only_storage_is_not_overwritten();
    test_equal_generation_conflict_fails_closed();
    puts("SBP NVS config journal tests passed");
    return 0;
}
