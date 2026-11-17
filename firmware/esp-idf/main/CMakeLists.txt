idf_component_register(
    SRCS "app_main.c" "ble_service.c" "../../core/src/sbp_controller.c" "../../core/src/sbp_sensor_units.c" "../../core/src/sbp_voltage_class.c" "../../core/src/sbp_config_record.c"
    INCLUDE_DIRS "." "../../core/include"
    REQUIRES driver bt
)
