#ifndef SBP_TEST_NVS_MOCK_H
#define SBP_TEST_NVS_MOCK_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

void nvs_mock_reset(void);
void nvs_mock_seed(const char *key, const uint8_t *data, size_t size);
bool nvs_mock_has_key(const char *key);
void nvs_mock_fail_next_commit(void);
void nvs_mock_fail_next_set_blob(void);
void nvs_mock_fail_next_get_blob_query(void);
void nvs_mock_fail_next_get_blob_read(void);
void nvs_mock_fail_next_readback_after_commit(void);
void nvs_mock_corrupt_next_commit(void);

#endif
