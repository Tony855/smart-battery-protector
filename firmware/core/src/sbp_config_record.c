#include "sbp_config_record.h"

#include <string.h>

#define SBP_RECORD_MAGIC 0x43504253UL /* "SBPC" in little-endian bytes */

static void put_u16(uint8_t *p, uint16_t value) {
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8U);
}

static void put_u32(uint8_t *p, uint32_t value) {
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8U);
    p[2] = (uint8_t)(value >> 16U);
    p[3] = (uint8_t)(value >> 24U);
}

static uint16_t get_u16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8U));
}

static uint32_t get_u32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8U) |
           ((uint32_t)p[2] << 16U) | ((uint32_t)p[3] << 24U);
}

uint32_t sbp_config_record_crc32(const uint8_t *data, size_t length) {
    if (data == NULL) return 0U;
    uint32_t crc = 0xFFFFFFFFUL;
    for (size_t i = 0U; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t bit = 0U; bit < 8U; ++bit) {
            const uint32_t mask = (uint32_t)(0U - (crc & 1U));
            crc = (crc >> 1U) ^ (0xEDB88320UL & mask);
        }
    }
    return ~crc;
}

bool sbp_config_record_is_valid(const sbp_config_record_t *r) {
    if (r == NULL || r->variant > 1U) return false;
    if (r->low_voltage_qualify_ms < 1000U ||
        r->low_voltage_qualify_ms > 600000U ||
        r->recovery_qualify_ms < 1000U ||
        r->recovery_qualify_ms > 600000U) return false;
    if (!r->protection_enabled) return true;
    if (r->low_voltage_12v_mv < 9000U || r->low_voltage_12v_mv > 16500U ||
        r->recovery_voltage_12v_mv <= r->low_voltage_12v_mv ||
        r->recovery_voltage_12v_mv > 16500U) return false;
    if (r->low_voltage_24v_mv < 18000U || r->low_voltage_24v_mv > 33000U ||
        r->recovery_voltage_24v_mv <= r->low_voltage_24v_mv ||
        r->recovery_voltage_24v_mv > 33000U) return false;
    if (r->max_current_ma == 0U || r->max_current_ma > 2000000U ||
        r->shunt_micro_ohm == 0U || r->shunt_micro_ohm > 1000000U) return false;
    if (r->max_temperature_deci_c < -400 || r->max_temperature_deci_c > 1500) return false;
    return true;
}

bool sbp_config_record_encode(const sbp_config_record_t *r,
                              uint8_t output[SBP_CONFIG_RECORD_SIZE]) {
    if (output == NULL || !sbp_config_record_is_valid(r)) return false;
    memset(output, 0, SBP_CONFIG_RECORD_SIZE);
    put_u32(&output[0], SBP_RECORD_MAGIC);
    put_u16(&output[4], SBP_CONFIG_RECORD_VERSION);
    put_u16(&output[6], SBP_CONFIG_RECORD_SIZE);
    put_u32(&output[8], r->generation);
    output[12] = r->variant;
    output[13] = r->protection_enabled ? 1U : 0U;
    put_u32(&output[16], r->low_voltage_12v_mv);
    put_u32(&output[20], r->recovery_voltage_12v_mv);
    put_u32(&output[24], r->low_voltage_24v_mv);
    put_u32(&output[28], r->recovery_voltage_24v_mv);
    put_u32(&output[32], r->max_current_ma);
    put_u16(&output[36], (uint16_t)r->max_temperature_deci_c);
    put_u32(&output[40], r->low_voltage_qualify_ms);
    put_u32(&output[44], r->recovery_qualify_ms);
    put_u32(&output[48], r->shunt_micro_ohm);
    put_u32(&output[52], sbp_config_record_crc32(output, 52U));
    return true;
}

bool sbp_config_record_decode(const uint8_t *input, size_t input_size,
                              sbp_config_record_t *r) {
    if (input == NULL || r == NULL || input_size != SBP_CONFIG_RECORD_SIZE) return false;
    if (get_u32(&input[0]) != SBP_RECORD_MAGIC ||
        get_u16(&input[4]) != SBP_CONFIG_RECORD_VERSION ||
        get_u16(&input[6]) != SBP_CONFIG_RECORD_SIZE ||
        input[13] > 1U || input[14] != 0U || input[15] != 0U ||
        get_u16(&input[38]) != 0U ||
        get_u32(&input[52]) != sbp_config_record_crc32(input, 52U)) return false;

    sbp_config_record_t decoded = {
        .generation = get_u32(&input[8]),
        .variant = input[12],
        .protection_enabled = input[13] == 1U,
        .low_voltage_12v_mv = get_u32(&input[16]),
        .recovery_voltage_12v_mv = get_u32(&input[20]),
        .low_voltage_24v_mv = get_u32(&input[24]),
        .recovery_voltage_24v_mv = get_u32(&input[28]),
        .max_current_ma = get_u32(&input[32]),
        .max_temperature_deci_c = (int16_t)get_u16(&input[36]),
        .low_voltage_qualify_ms = get_u32(&input[40]),
        .recovery_qualify_ms = get_u32(&input[44]),
        .shunt_micro_ohm = get_u32(&input[48])
    };
    if (!sbp_config_record_is_valid(&decoded)) return false;
    *r = decoded;
    return true;
}
