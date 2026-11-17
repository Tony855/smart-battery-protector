idf_component_register(
    SRCS "app_main.c" "ble_service.c" "config_store.c" "../../core/src/sbp_controller.c" "../../core/src/sbp_sensor_units.c" "../../core/src/sbp_voltage_class.c" "../../core/src/sbp_config_record.c" "../../core/src/sbp_boot_diagnostics.c"
    INCLUDE_DIRS "." "../../core/include"
    REQUIRES driver bt nvs_flash
)
