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


static void test_generation_exhaustion_fails_closed(void) {
    nvs_mock_reset();
    sbp_config_record_t final_record = make_record(UINT32_MAX, 0U);
    seed_record("record_a", &final_record);

    sbp_config_record_t loaded;
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == UINT32_MAX);

    /* Generation is monotonic and must never wrap to zero. */
    sbp_config_record_t wrapped = make_record(0U, 1U);
    assert(sbp_config_store_save(&wrapped) == ESP_ERR_INVALID_STATE);
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == UINT32_MAX);
}


static void test_set_blob_failure_preserves_previous_record(void) {
    nvs_mock_reset();
    sbp_config_record_t first = make_record(50U, 0U);
    seed_record("record_a", &first);

    sbp_config_record_t proposed = make_record(51U, 1U);
    sbp_config_record_t loaded;
    nvs_mock_fail_next_set_blob();
    assert(sbp_config_store_save(&proposed) == ESP_FAIL);
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 50U);
    assert(!nvs_mock_has_key("record_b"));

    assert(sbp_config_store_save(&proposed) == ESP_OK);
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 51U);
}


static void test_read_failures_fail_closed(void) {
    nvs_mock_reset();
    sbp_config_record_t first = make_record(60U, 0U);
    seed_record("record_a", &first);
    sbp_config_record_t loaded;

    nvs_mock_fail_next_get_blob_query();
    assert(sbp_config_store_load(&loaded) == ESP_FAIL);
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 60U);

    nvs_mock_fail_next_get_blob_read();
    assert(sbp_config_store_load(&loaded) == ESP_FAIL);
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 60U);

    sbp_config_record_t proposed = make_record(61U, 1U);
    nvs_mock_fail_next_get_blob_query();
    assert(sbp_config_store_save(&proposed) == ESP_FAIL);
    assert(!nvs_mock_has_key("record_b"));
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 60U);

    nvs_mock_fail_next_get_blob_read();
    assert(sbp_config_store_save(&proposed) == ESP_FAIL);
    assert(!nvs_mock_has_key("record_b"));
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 60U);
}

static void test_post_commit_readback_failure_is_recoverable(void) {
    nvs_mock_reset();
    sbp_config_record_t first = make_record(70U, 0U);
    seed_record("record_a", &first);
    sbp_config_record_t proposed = make_record(71U, 1U);
    sbp_config_record_t loaded;

    nvs_mock_fail_next_readback_after_commit();
    assert(sbp_config_store_save(&proposed) == ESP_FAIL);
    /* Commit may be durable despite failed verification; re-read resolves it. */
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 71U);
    assert(sbp_config_store_save(&proposed) == ESP_ERR_INVALID_STATE);

    sbp_config_record_t next = make_record(72U, 0U);
    assert(sbp_config_store_save(&next) == ESP_OK);
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 72U);
}


static void test_identical_generation_duplicate_slots_rotate_deterministically(void) {
    nvs_mock_reset();
    sbp_config_record_t first = make_record(80U, 0U);
    seed_record("record_a", &first);
    seed_record("record_b", &first);

    sbp_config_record_t loaded;
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 80U);

    sbp_config_record_t next = make_record(81U, 1U);
    assert(sbp_config_store_save(&next) == ESP_OK);
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 81U);
    /* Deterministic tie rotation replaces B and leaves A intact. */
    assert(nvs_mock_has_key("record_a"));
    assert(nvs_mock_has_key("record_b"));
}

static void test_truncated_slot_is_corrupt_and_replaced_safely(void) {
    nvs_mock_reset();
    sbp_config_record_t first = make_record(90U, 0U);
    seed_record("record_a", &first);
    uint8_t truncated[8] = {0x53U, 0x42U, 0x50U};
    nvs_mock_seed("record_b", truncated, sizeof(truncated));

    sbp_config_record_t loaded;
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 90U);

    sbp_config_record_t next = make_record(91U, 1U);
    assert(sbp_config_store_save(&next) == ESP_OK);
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 91U);
}

static void test_corrupt_legacy_is_not_overwritten_without_valid_slot(void) {
    nvs_mock_reset();
    uint8_t corrupt[SBP_CONFIG_RECORD_SIZE] = {0};
    nvs_mock_seed("record_v1", corrupt, sizeof(corrupt));

    sbp_config_record_t loaded;
    sbp_config_record_t proposed = make_record(1U, 0U);
    assert(sbp_config_store_load(&loaded) == ESP_ERR_INVALID_RESPONSE);
    assert(sbp_config_store_save(&proposed) == ESP_ERR_INVALID_RESPONSE);
    assert(!nvs_mock_has_key("record_a"));
    assert(!nvs_mock_has_key("record_b"));
}

static void test_corrupt_legacy_is_ignored_when_slot_is_valid(void) {
    nvs_mock_reset();
    sbp_config_record_t first = make_record(100U, 0U);
    seed_record("record_a", &first);
    uint8_t corrupt[SBP_CONFIG_RECORD_SIZE] = {0};
    nvs_mock_seed("record_v1", corrupt, sizeof(corrupt));

    sbp_config_record_t loaded;
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 100U);
    sbp_config_record_t next = make_record(101U, 1U);
    assert(sbp_config_store_save(&next) == ESP_OK);
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 101U);
    assert(nvs_mock_has_key("record_v1"));
}


static void test_readback_crc_mismatch_preserves_previous_slot(void) {
    nvs_mock_reset();
    sbp_config_record_t first = make_record(110U, 0U);
    seed_record("record_a", &first);

    sbp_config_record_t proposed = make_record(111U, 1U);
    sbp_config_record_t loaded;
    nvs_mock_corrupt_next_commit();
    assert(sbp_config_store_save(&proposed) == ESP_ERR_INVALID_RESPONSE);
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 110U);

    /* The corrupt target is replaceable; the valid prior slot remains intact. */
    assert(sbp_config_store_save(&proposed) == ESP_OK);
    assert(sbp_config_store_load(&loaded) == ESP_OK);
    assert(loaded.generation == 111U);
}

int main(void) {
    assert(sbp_config_store_init() == ESP_OK);
    test_first_save_and_failed_commit();
    test_failed_rotation_keeps_newest_slot();
    test_corrupt_newest_slot_falls_back();
    test_legacy_migration_is_non_destructive();
    test_corrupt_only_storage_is_not_overwritten();
    test_equal_generation_conflict_fails_closed();
    test_generation_exhaustion_fails_closed();
    test_set_blob_failure_preserves_previous_record();
    test_read_failures_fail_closed();
    test_post_commit_readback_failure_is_recoverable();
    test_identical_generation_duplicate_slots_rotate_deterministically();
    test_truncated_slot_is_corrupt_and_replaced_safely();
    test_corrupt_legacy_is_not_overwritten_without_valid_slot();
    test_corrupt_legacy_is_ignored_when_slot_is_valid();
    test_readback_crc_mismatch_preserves_previous_slot();
    puts("SBP NVS config journal tests passed");
    return 0;
}
