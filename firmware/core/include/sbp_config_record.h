#ifndef SBP_CONFIG_RECORD_H
#define SBP_CONFIG_RECORD_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define SBP_CONFIG_RECORD_SIZE 56U
#define SBP_CONFIG_RECORD_VERSION 1U

typedef struct {
    uint32_t generation;
    uint8_t variant;
    bool protection_enabled;
    uint32_t low_voltage_12v_mv;
    uint32_t recovery_voltage_12v_mv;
    uint32_t low_voltage_24v_mv;
    uint32_t recovery_voltage_24v_mv;
    uint32_t max_current_ma;
    int16_t max_temperature_deci_c;
    uint32_t low_voltage_qualify_ms;
    uint32_t recovery_qualify_ms;
    uint32_t shunt_micro_ohm;
} sbp_config_record_t;

/* Explicit little-endian wire encoding; never persist compiler struct padding. */
bool sbp_config_record_is_valid(const sbp_config_record_t *record);
bool sbp_config_record_encode(const sbp_config_record_t *record,
                              uint8_t output[SBP_CONFIG_RECORD_SIZE]);
bool sbp_config_record_decode(const uint8_t *input, size_t input_size,
                              sbp_config_record_t *record);
uint32_t sbp_config_record_crc32(const uint8_t *data, size_t length);

#endif
