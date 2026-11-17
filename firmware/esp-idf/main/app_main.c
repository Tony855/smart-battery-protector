#include <math.h>
#include <stdbool.h>
#include <stdint.h>

#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "esp_err.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sbp_controller.h"
#include "ble_service.h"
#include "sbp_sensor_units.h"
#include "sbp_voltage_class.h"
#include "config_store.h"
#include "nvs.h"

#ifndef CONFIG_SBP_SHUNT_MICRO_OHM
#define CONFIG_SBP_SHUNT_MICRO_OHM 0
#endif
#ifndef CONFIG_SBP_LOW_VOLTAGE_QUALIFY_MS
#define CONFIG_SBP_LOW_VOLTAGE_QUALIFY_MS 30000
#endif
#ifndef CONFIG_SBP_RECOVERY_QUALIFY_MS
#define CONFIG_SBP_RECOVERY_QUALIFY_MS 30000
#endif
#ifndef CONFIG_SBP_PROTECTION_ENABLE
#define CONFIG_SBP_PROTECTION_ENABLE 0
#endif
#ifndef CONFIG_SBP_PRODUCT_MAIN_POWER
#define CONFIG_SBP_PRODUCT_MAIN_POWER 0
#endif

#define SBP_I2C_SDA GPIO_NUM_6
#define SBP_I2C_SCL GPIO_NUM_7
#define SBP_ENGINE_RUNNING_GPIO GPIO_NUM_20
#define SBP_ENGINE_VALID_GPIO GPIO_NUM_21
#define SBP_ACTUATOR_FEEDBACK_GPIO GPIO_NUM_18
#define SBP_ACTUATOR_FEEDBACK_VALID_GPIO GPIO_NUM_19
#define INA228_ADDRESS 0x40U
#define TMP117_ADDRESS 0x48U
#define INA228_CONFIG_REGISTER 0x00U
#define INA228_ADC_CONFIG_REGISTER 0x01U
#define INA228_MANUFACTURER_ID_REGISTER 0x3EU
#define INA228_DEVICE_ID_REGISTER 0x3FU
#define INA228_VSHUNT_REGISTER 0x04U
#define INA228_VBUS_REGISTER 0x05U
#define TMP117_TEMPERATURE_REGISTER 0x00U
#define TMP117_DEVICE_ID_REGISTER 0x0FU

static const char *TAG = "sbp";
static i2c_master_dev_handle_t ina228;
static i2c_master_dev_handle_t tmp117;

static esp_err_t read_register(i2c_master_dev_handle_t device, uint8_t reg,
                               uint8_t *data, size_t length) {
    return i2c_master_transmit_receive(device, &reg, 1U, data, length, 100U);
}

static esp_err_t read_u24(i2c_master_dev_handle_t device, uint8_t reg, uint32_t *value) {
    uint8_t b[3] = {0U, 0U, 0U};
    esp_err_t err = read_register(device, reg, b, sizeof(b));
    if (err == ESP_OK) *value = ((uint32_t)b[0] << 16U) | ((uint32_t)b[1] << 8U) | b[2];
    return err;
}

static esp_err_t read_u16(i2c_master_dev_handle_t device, uint8_t reg, uint16_t *value) {
    uint8_t b[2] = {0U, 0U};
    esp_err_t err = read_register(device, reg, b, sizeof(b));
    if (err == ESP_OK) *value = (uint16_t)(((uint16_t)b[0] << 8U) | b[1]);
    return err;
}

static esp_err_t write_u16(i2c_master_dev_handle_t device, uint8_t reg, uint16_t value) {
    uint8_t data[3] = {reg, (uint8_t)(value >> 8U), (uint8_t)value};
    return i2c_master_transmit(device, data, sizeof(data), 100U);
}

static esp_err_t init_i2c(void) {
    i2c_master_bus_config_t bus_config = {
        .i2c_port = I2C_NUM_0,
        .sda_io_num = SBP_I2C_SDA,
        .scl_io_num = SBP_I2C_SCL,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7U,
        .flags.enable_internal_pullup = true
    };
    i2c_master_bus_handle_t bus = NULL;
    esp_err_t err = i2c_new_master_bus(&bus_config, &bus);
    if (err != ESP_OK) return err;

    const i2c_device_config_t ina_config = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = INA228_ADDRESS,
        .scl_speed_hz = 100000U
    };
    err = i2c_master_bus_add_device(bus, &ina_config, &ina228);
    if (err != ESP_OK) return err;

    const i2c_device_config_t tmp_config = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = TMP117_ADDRESS,
        .scl_speed_hz = 100000U
    };
    err = i2c_master_bus_add_device(bus, &tmp_config, &tmp117);
    if (err != ESP_OK) return err;

    uint16_t manufacturer_id = 0U;
    uint16_t ina_device_id = 0U;
    uint16_t tmp_device_id = 0U;
    if (read_u16(ina228, INA228_MANUFACTURER_ID_REGISTER, &manufacturer_id) != ESP_OK ||
        read_u16(ina228, INA228_DEVICE_ID_REGISTER, &ina_device_id) != ESP_OK ||
        read_u16(tmp117, TMP117_DEVICE_ID_REGISTER, &tmp_device_id) != ESP_OK) {
        return ESP_ERR_NOT_FOUND;
    }
    if (manufacturer_id != 0x5449U || (ina_device_id & 0xFFF0U) != 0x2280U ||
        (tmp_device_id & 0x0FFFU) != 0x0117U) {
        ESP_LOGE(TAG, "Sensor identity mismatch: INA mfr=0x%04x id=0x%04x TMP id=0x%04x",
                 manufacturer_id, ina_device_id, tmp_device_id);
        return ESP_ERR_NOT_FOUND;
    }

    /* Force INA228 ADCRANGE=0 and continuous VBUS/VSHUNT/TEMP conversions. */
    if (write_u16(ina228, INA228_CONFIG_REGISTER, 0x0000U) != ESP_OK ||
        write_u16(ina228, INA228_ADC_CONFIG_REGISTER, 0xFB68U) != ESP_OK) {
        return ESP_FAIL;
    }
    uint16_t adc_config = 0U;
    if (read_u16(ina228, INA228_ADC_CONFIG_REGISTER, &adc_config) != ESP_OK ||
        adc_config != 0xFB68U) {
        ESP_LOGE(TAG, "INA228 ADC configuration readback mismatch: 0x%04x", adc_config);
        return ESP_FAIL;
    }
    return ESP_OK;
}

static void init_inputs(void) {
    const gpio_config_t inputs = {
        .pin_bit_mask = (1ULL << SBP_ENGINE_RUNNING_GPIO) |
                        (1ULL << SBP_ENGINE_VALID_GPIO) |
                        (1ULL << SBP_ACTUATOR_FEEDBACK_GPIO) |
                        (1ULL << SBP_ACTUATOR_FEEDBACK_VALID_GPIO),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    ESP_ERROR_CHECK(gpio_config(&inputs));
    ESP_LOGW(TAG, "Actuator output GPIO14 is reserved and not driven in this firmware build");

}

static sbp_engine_state_t read_engine_state(void) {
    if (gpio_get_level(SBP_ENGINE_VALID_GPIO) == 0) return SBP_ENGINE_UNKNOWN;
    return gpio_get_level(SBP_ENGINE_RUNNING_GPIO) != 0 ?
        SBP_ENGINE_RUNNING : SBP_ENGINE_OFF;
}

static sbp_actuator_state_t read_actuator_feedback(void) {
    if (gpio_get_level(SBP_ACTUATOR_FEEDBACK_VALID_GPIO) == 0) {
        return SBP_ACTUATOR_UNKNOWN;
    }
    return gpio_get_level(SBP_ACTUATOR_FEEDBACK_GPIO) != 0 ?
        SBP_ACTUATOR_CLOSED : SBP_ACTUATOR_OPEN;
}

void app_main(void) {
    ESP_LOGI(TAG, "SBP ESP32-C6 controller starting; firmware build is monitor-only by default");
    init_inputs();
    sbp_config_record_t persisted_config;
    esp_err_t store_err = sbp_config_store_init();
    if (store_err == ESP_OK) {
        store_err = sbp_config_store_load(&persisted_config);
        if (store_err == ESP_OK) {
            ESP_LOGW(TAG, "Stored config generation %lu validated; not applied in monitor-only firmware",
                     (unsigned long)persisted_config.generation);
        } else if (store_err == ESP_ERR_NVS_NOT_FOUND) {
            ESP_LOGI(TAG, "No commissioned NVS config found; using safe monitor-only defaults");
        } else {
            ESP_LOGE(TAG, "NVS config unavailable or invalid (%s); protection remains disabled",
                     esp_err_to_name(store_err));
        }
    } else {
        ESP_LOGE(TAG, "NVS initialization failed (%s); protection remains disabled",
                 esp_err_to_name(store_err));
    }
    const esp_err_t sensor_init_err = init_i2c();
    const bool sensors_initialized = sensor_init_err == ESP_OK;
    if (!sensors_initialized) {
        ESP_LOGE(TAG, "Sensor initialization failed (%s); continuing in safe monitor-only mode",
                 esp_err_to_name(sensor_init_err));
    }
    sbp_ble_start();

    sbp_controller_t controller;
    sbp_controller_init(&controller);
    sbp_voltage_classifier_t voltage_classifier;
    sbp_voltage_classifier_init(&voltage_classifier);
    sbp_config_t config = {
        .variant = CONFIG_SBP_PRODUCT_MAIN_POWER ? SBP_VARIANT_MAIN : SBP_VARIANT_AUXILIARY,
        .protection_enabled = false,
        .low_voltage_v = 0.0f,
        .recovery_voltage_v = 0.0f,
        .max_current_a = 0.0f,
        .max_temperature_deci_c = 0,
        .low_voltage_qualify_ms = (uint32_t)CONFIG_SBP_LOW_VOLTAGE_QUALIFY_MS,
        .recovery_qualify_ms = (uint32_t)CONFIG_SBP_RECOVERY_QUALIFY_MS
    };

    const float shunt_ohms = (float)CONFIG_SBP_SHUNT_MICRO_OHM / 1000000.0f;
    while (true) {
        uint32_t vbus_raw = 0U;
        uint32_t vshunt_raw = 0U;
        uint16_t temp_raw = 0U;
        float voltage_v = 0.0f;
        float current_a = 0.0f;
        int16_t temperature_deci_c = 0;
        const bool voltage_ok = sensors_initialized &&
                                read_u24(ina228, INA228_VBUS_REGISTER, &vbus_raw) == ESP_OK &&
                                sbp_ina228_bus_voltage_v(vbus_raw, &voltage_v);
        const bool current_ok = sensors_initialized && shunt_ohms > 0.0f &&
                                read_u24(ina228, INA228_VSHUNT_REGISTER, &vshunt_raw) == ESP_OK &&
                                sbp_ina228_shunt_current_a(vshunt_raw, shunt_ohms, &current_a);
        const bool temp_ok = sensors_initialized &&
                             read_u16(tmp117, TMP117_TEMPERATURE_REGISTER, &temp_raw) == ESP_OK &&
                             sbp_tmp117_temperature_deci_c(temp_raw, &temperature_deci_c);

        const uint32_t now_ms = (uint32_t)(xTaskGetTickCount() * portTICK_PERIOD_MS);
        const sbp_voltage_class_t voltage_class =
            sbp_voltage_classifier_update(&voltage_classifier,
                voltage_ok ? voltage_v : NAN, now_ms, 10000U);

        config.protection_enabled = false;
#if CONFIG_SBP_PROTECTION_ENABLE
        if (voltage_class == SBP_VOLTAGE_12V) {
            config.low_voltage_v = (float)CONFIG_SBP_LOW_VOLTAGE_12V_MV / 1000.0f;
            config.recovery_voltage_v = (float)CONFIG_SBP_RECOVERY_VOLTAGE_12V_MV / 1000.0f;
        } else if (voltage_class == SBP_VOLTAGE_24V) {
            config.low_voltage_v = (float)CONFIG_SBP_LOW_VOLTAGE_24V_MV / 1000.0f;
            config.recovery_voltage_v = (float)CONFIG_SBP_RECOVERY_VOLTAGE_24V_MV / 1000.0f;
        }
        config.max_current_a = (float)CONFIG_SBP_MAX_CURRENT_MA / 1000.0f;
        config.max_temperature_deci_c = (int16_t)CONFIG_SBP_MAX_TEMPERATURE_DECI_C;
        config.protection_enabled = voltage_class != SBP_VOLTAGE_UNKNOWN &&
                                    CONFIG_SBP_MAX_TEMPERATURE_DECI_C > 0 &&
                                    shunt_ohms > 0.0f &&
                                    sbp_config_is_valid(&config);
#endif

        sbp_measurements_t measurements = {
            .sensors_valid = voltage_ok && current_ok && temp_ok,
            .battery_voltage_v = voltage_v,
            .battery_current_a = current_a,
            .temperature_deci_c = temperature_deci_c,
            .engine = read_engine_state(),
            .actuator = read_actuator_feedback()
        };
        sbp_output_t output = sbp_controller_step(
            &controller, &config, &measurements, SBP_REQUEST_NONE, now_ms);

        sbp_ble_publish(voltage_v, voltage_ok, current_a, current_ok,
                        temperature_deci_c, temp_ok, (int)measurements.engine, (int)output.state, (int)voltage_class);

        if (voltage_ok && temp_ok) {
            if (current_ok) {
                ESP_LOGI(TAG, "VBAT=%.3f V I=%.3f A TEMP=%.1f C engine=%d state=%d voltage_class=%d",
                         (double)voltage_v, (double)current_a,
                         (double)temperature_deci_c / 10.0,
                         (int)measurements.engine, (int)output.state, (int)voltage_class);
            } else {
                ESP_LOGW(TAG, "VBAT=%.3f V current=UNCONFIGURED TEMP=%.1f C; monitor only",
                         (double)voltage_v, (double)temperature_deci_c / 10.0);
            }
        } else {
            ESP_LOGE(TAG, "Sensor read failed: INA228 voltage/current or TMP117 temperature");
        }

        /* No physical switching is performed in this firmware increment. */
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
