cmake_minimum_required(VERSION 3.16)
project(sbp_controller_core C)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
add_library(sbp_controller src/sbp_controller.c src/sbp_sensor_units.c src/sbp_voltage_class.c src/sbp_config_record.c)
target_include_directories(sbp_controller PUBLIC include)
target_link_libraries(sbp_controller PUBLIC m)
target_compile_options(sbp_controller PRIVATE -Wall -Wextra -Werror -Wconversion)
add_executable(sbp_controller_test tests/test_controller.c)
target_link_libraries(sbp_controller_test PRIVATE sbp_controller)
target_compile_options(sbp_controller_test PRIVATE -Wall -Wextra -Werror)
enable_testing()
add_test(NAME sbp_controller_test COMMAND sbp_controller_test)
add_executable(sbp_sensor_units_test tests/test_sensor_units.c)
target_link_libraries(sbp_sensor_units_test PRIVATE sbp_controller)
target_compile_options(sbp_sensor_units_test PRIVATE -Wall -Wextra -Werror)
add_test(NAME sbp_sensor_units_test COMMAND sbp_sensor_units_test)

add_executable(sbp_voltage_class_test tests/test_voltage_class.c)
target_link_libraries(sbp_voltage_class_test PRIVATE sbp_controller)
target_compile_options(sbp_voltage_class_test PRIVATE -Wall -Wextra -Werror)
add_test(NAME sbp_voltage_class_test COMMAND sbp_voltage_class_test)

add_executable(sbp_config_record_test tests/test_config_record.c)
target_link_libraries(sbp_config_record_test PRIVATE sbp_controller)
target_compile_options(sbp_config_record_test PRIVATE -Wall -Wextra -Werror -Wconversion)
add_test(NAME sbp_config_record_test COMMAND sbp_config_record_test)

# Host-side NVS adapter model: commit failures emulate power loss before durability.
add_executable(sbp_config_store_test
    ../esp-idf/tests/test_config_store.c
    ../esp-idf/main/config_store.c
    ../esp-idf/test_stubs/nvs_mock.c
)
target_include_directories(sbp_config_store_test PRIVATE
    ../esp-idf/test_stubs
    ../esp-idf/main
)
target_link_libraries(sbp_config_store_test PRIVATE sbp_controller)
target_compile_options(sbp_config_store_test PRIVATE -Wall -Wextra -Werror -Wconversion)
add_test(NAME sbp_config_store_test COMMAND sbp_config_store_test)
