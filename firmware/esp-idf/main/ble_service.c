#include "ble_service.h"

#include <stdio.h>
#include <string.h>

#include "esp_log.h"
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "host/ble_hs.h"
#include "host/ble_att.h"
#include "host/ble_uuid.h"
#include "host/util/util.h"
#include "services/gap/ble_svc_gap.h"
#include "services/gatt/ble_svc_gatt.h"
#include "freertos/FreeRTOS.h"
#include "freertos/portmacro.h"

static const char *TAG = "sbp_ble";
static uint8_t own_addr_type;
static uint16_t telemetry_value_handle;
static uint16_t diagnostics_value_handle;
static char diagnostics_json[128] = "{\"v\":1,\"rr\":0,\"nv\":0,\"sn\":0,\"mo\":0,\"rf\":19,\"cg\":0}";
static char telemetry_json[320] = "{\"v\":1,\"n\":0,\"bv\":null,\"vv\":false,\"ba\":null,\"av\":false,\"tc\":null,\"tv\":false,\"e\":0,\"s\":0,\"vc\":0,\"pe\":false}";
static portMUX_TYPE telemetry_mux = portMUX_INITIALIZER_UNLOCKED;

static const ble_uuid128_t service_uuid =
    BLE_UUID128_INIT(0x9a, 0x70, 0x10, 0x01, 0x62, 0x9b, 0x4d, 0x83,
                     0x9a, 0x2c, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66);
static const ble_uuid128_t telemetry_uuid =
    BLE_UUID128_INIT(0x9a, 0x70, 0x10, 0x02, 0x62, 0x9b, 0x4d, 0x83,
                     0x9a, 0x2c, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66);
static const ble_uuid128_t diagnostics_uuid =
    BLE_UUID128_INIT(0x9a, 0x70, 0x10, 0x03, 0x62, 0x9b, 0x4d, 0x83,
                     0x9a, 0x2c, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66);

static int telemetry_access(uint16_t conn_handle, uint16_t attr_handle,
                            struct ble_gatt_access_ctxt *ctxt, void *arg) {
    (void)conn_handle;
    (void)arg;
    if (ctxt->op != BLE_GATT_ACCESS_OP_READ_CHR ||
        attr_handle != telemetry_value_handle) {
        return BLE_ATT_ERR_READ_NOT_PERMITTED;
    }

    char snapshot[sizeof(telemetry_json)];
    portENTER_CRITICAL(&telemetry_mux);
    memcpy(snapshot, telemetry_json, sizeof(snapshot));
    portEXIT_CRITICAL(&telemetry_mux);
    snapshot[sizeof(snapshot) - 1U] = '\0';
    int rc = os_mbuf_append(ctxt->om, snapshot, strlen(snapshot));
    return rc == 0 ? 0 : BLE_ATT_ERR_INSUFFICIENT_RES;
}

static int diagnostics_access(uint16_t conn_handle, uint16_t attr_handle,
                             struct ble_gatt_access_ctxt *ctxt, void *arg) {
    (void)conn_handle;
    (void)arg;
    if (ctxt->op != BLE_GATT_ACCESS_OP_READ_CHR ||
        attr_handle != diagnostics_value_handle) {
        return BLE_ATT_ERR_READ_NOT_PERMITTED;
    }

    char snapshot[sizeof(diagnostics_json)];
    portENTER_CRITICAL(&telemetry_mux);
    memcpy(snapshot, diagnostics_json, sizeof(snapshot));
    portEXIT_CRITICAL(&telemetry_mux);
    snapshot[sizeof(snapshot) - 1U] = '\0';
    const int rc = os_mbuf_append(ctxt->om, snapshot, strlen(snapshot));
    return rc == 0 ? 0 : BLE_ATT_ERR_INSUFFICIENT_RES;
}

static const struct ble_gatt_svc_def services[] = {
    {
        .type = BLE_GATT_SVC_TYPE_PRIMARY,
        .uuid = &service_uuid.u,
        .characteristics = (struct ble_gatt_chr_def[]) {
            {
                .uuid = &telemetry_uuid.u,
                .access_cb = telemetry_access,
                .flags = BLE_GATT_CHR_F_READ | BLE_GATT_CHR_F_NOTIFY,
                .val_handle = &telemetry_value_handle
            },
            {
                .uuid = &diagnostics_uuid.u,
                .access_cb = diagnostics_access,
                .flags = BLE_GATT_CHR_F_READ,
                .val_handle = &diagnostics_value_handle
            },
            { 0 }
        }
    },
    { 0 }
};

static int gap_event(struct ble_gap_event *event, void *arg);

static void start_advertising(void) {
    struct ble_hs_adv_fields fields;
    memset(&fields, 0, sizeof(fields));
    fields.flags = BLE_HS_ADV_F_DISC_GEN | BLE_HS_ADV_F_BREDR_UNSUP;
    const char *name = ble_svc_gap_device_name();
    fields.name = (uint8_t *)name;
    fields.name_len = (uint8_t)strlen(name);
    fields.name_is_complete = 1;
    int rc = ble_gap_adv_set_fields(&fields);
    if (rc != 0) {
        ESP_LOGE(TAG, "BLE advertisement data failed: %d", rc);
        return;
    }

    struct ble_gap_adv_params params;
    memset(&params, 0, sizeof(params));
    params.conn_mode = BLE_GAP_CONN_MODE_UND;
    params.disc_mode = BLE_GAP_DISC_MODE_GEN;
    rc = ble_gap_adv_start(own_addr_type, NULL, BLE_HS_FOREVER,
                           &params, gap_event, NULL);
    if (rc != 0) ESP_LOGE(TAG, "BLE advertising failed: %d", rc);
    else ESP_LOGI(TAG, "BLE advertising as %s", name);
}

static int gap_event(struct ble_gap_event *event, void *arg) {
    (void)arg;
    switch (event->type) {
    case BLE_GAP_EVENT_CONNECT:
        if (event->connect.status == 0) {
            ESP_LOGI(TAG, "BLE client connected");
        } else {
            ESP_LOGW(TAG, "BLE connection failed: %d", event->connect.status);
            start_advertising();
        }
        return 0;
    case BLE_GAP_EVENT_DISCONNECT:
        ESP_LOGI(TAG, "BLE client disconnected; resume advertising");
        start_advertising();
        return 0;
    case BLE_GAP_EVENT_ADV_COMPLETE:
        start_advertising();
        return 0;
    case BLE_GAP_EVENT_SUBSCRIBE:
        ESP_LOGI(TAG, "BLE telemetry notify subscription changed");
        return 0;
    default:
        return 0;
    }
}

static void on_sync(void) {
    int rc = ble_hs_util_ensure_addr(0);
    if (rc != 0) {
        ESP_LOGE(TAG, "BLE identity address unavailable: %d", rc);
        return;
    }
    rc = ble_hs_id_infer_auto(0, &own_addr_type);
    if (rc != 0) {
        ESP_LOGE(TAG, "BLE address type inference failed: %d", rc);
        return;
    }
    start_advertising();
}

static void on_reset(int reason) {
    ESP_LOGE(TAG, "NimBLE host reset: %d", reason);
}

static void host_task(void *param) {
    (void)param;
    nimble_port_run();
    nimble_port_freertos_deinit();
}

void sbp_ble_start(void) {
    ble_att_set_preferred_mtu(128);
    ESP_ERROR_CHECK(nimble_port_init());
    ble_hs_cfg.reset_cb = on_reset;
    ble_hs_cfg.sync_cb = on_sync;

    ESP_ERROR_CHECK(ble_svc_gap_device_name_set("SBP-CTRL"));
    ble_svc_gap_init();
    ble_svc_gatt_init();
    int rc = ble_gatts_count_cfg(services);
    if (rc != 0) ESP_LOGE(TAG, "GATT count configuration failed: %d", rc);
    ESP_ERROR_CHECK(rc);
    rc = ble_gatts_add_svcs(services);
    if (rc != 0) ESP_LOGE(TAG, "GATT service registration failed: %d", rc);
    ESP_ERROR_CHECK(rc);
    nimble_port_freertos_init(host_task);
}

void sbp_ble_publish_diagnostics(const sbp_boot_diagnostics_t *diagnostics) {
    char json[sizeof(diagnostics_json)];
    if (!sbp_boot_diagnostics_format_json(diagnostics, json, sizeof(json))) {
        ESP_LOGE(TAG, "Invalid boot diagnostics; keeping not_ready diagnostic value");
        return;
    }
    portENTER_CRITICAL(&telemetry_mux);
    memcpy(diagnostics_json, json, strlen(json) + 1U);
    portEXIT_CRITICAL(&telemetry_mux);
}

void sbp_ble_publish(float voltage_v, bool voltage_valid,
                     float current_a, bool current_valid,
                     int16_t temperature_deci_c, bool temperature_valid,
                     int engine_state, int controller_state, int voltage_class) {
    char json[sizeof(telemetry_json)];
    char voltage_text[24];
    char current_text[24];
    char temperature_text[16];
    if (voltage_valid) (void)snprintf(voltage_text, sizeof(voltage_text), "%.3f", (double)voltage_v);
    else (void)snprintf(voltage_text, sizeof(voltage_text), "null");
    if (current_valid) (void)snprintf(current_text, sizeof(current_text), "%.3f", (double)current_a);
    else (void)snprintf(current_text, sizeof(current_text), "null");
    if (temperature_valid) (void)snprintf(temperature_text, sizeof(temperature_text), "%d", (int)temperature_deci_c);
    else (void)snprintf(temperature_text, sizeof(temperature_text), "null");
    static uint32_t telemetry_sequence;
    const uint32_t sequence = ++telemetry_sequence;
    int length = snprintf(json, sizeof(json),
        "{\"v\":1,\"n\":%lu,\"bv\":%s,\"vv\":%s,"
        "\"ba\":%s,\"av\":%s,\"tc\":%s,\"tv\":%s,"
        "\"e\":%d,\"s\":%d,\"vc\":%d,\"pe\":false}",
        (unsigned long)sequence, voltage_text, voltage_valid ? "true" : "false",
        current_text, current_valid ? "true" : "false",
        temperature_text, temperature_valid ? "true" : "false",
        engine_state, controller_state, voltage_class);
    if (length < 0 || (size_t)length >= sizeof(json)) return;
    portENTER_CRITICAL(&telemetry_mux);
    memcpy(telemetry_json, json, (size_t)length + 1U);
    portEXIT_CRITICAL(&telemetry_mux);
    if (telemetry_value_handle != 0U) {
        ble_gatts_chr_updated(telemetry_value_handle);
    }
}
