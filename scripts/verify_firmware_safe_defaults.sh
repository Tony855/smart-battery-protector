#!/usr/bin/env bash
set -euo pipefail

SDKCONFIG="${1:-firmware/esp-idf/sdkconfig}"
if [[ ! -f "$SDKCONFIG" ]]; then
  echo "ERROR: generated ESP-IDF sdkconfig not found: $SDKCONFIG" >&2
  exit 1
fi

require_config() {
  local key="$1"
  local expected="$2"
  local actual
  actual="$(grep -E "^${key}=" "$SDKCONFIG" | tail -n 1 || true)"
  if [[ "$actual" != "${key}=${expected}" ]]; then
    echo "ERROR: unsafe or missing commissioning setting" >&2
    echo "  expected: ${key}=${expected}" >&2
    echo "  actual:   ${actual:-<missing>}" >&2
    echo "Relevant generated settings:" >&2
    grep -E '^CONFIG_SBP_(LOW_VOLTAGE_QUALIFY_MS|RECOVERY_QUALIFY_MS|SHUNT_MICRO_OHM|PROTECTION_ENABLE)=' "$SDKCONFIG" >&2 || true
    exit 1
  fi
  echo "OK: ${actual}"
}

require_config CONFIG_SBP_LOW_VOLTAGE_QUALIFY_MS 30000
require_config CONFIG_SBP_RECOVERY_QUALIFY_MS 30000
require_config CONFIG_SBP_SHUNT_MICRO_OHM 0
require_disabled() {
  local key="$1"
  if ! grep -qx "# ${key} is not set" "$SDKCONFIG"; then
    echo "ERROR: ${key} must remain disabled in commissioning defaults" >&2
    grep -E "^(CONFIG_${key#CONFIG_}=|# ${key} is not set)" "$SDKCONFIG" >&2 || true
    exit 1
  fi
  echo "OK: # ${key} is not set"
}

require_disabled CONFIG_SBP_PROTECTION_ENABLE

# Security and OTA features are intentionally not provisioned in the engineering build.
# Enabling any of these requires an approved manufacturing/recovery lifecycle.
require_disabled CONFIG_SECURE_BOOT
require_disabled CONFIG_SECURE_FLASH_ENC_ENABLED
require_disabled CONFIG_NVS_ENCRYPTION
require_disabled CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE
require_disabled CONFIG_BOOTLOADER_APP_ANTI_ROLLBACK
