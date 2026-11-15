-- Smart Battery Protector initial logical schema (MariaDB 10.11+ candidate)
-- Apply only in a development database. Review indexes, retention and privacy before production.
CREATE DATABASE IF NOT EXISTS smart_battery_protector
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_battery_protector;

CREATE TABLE IF NOT EXISTS users (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  auth_subject VARCHAR(191) NOT NULL UNIQUE,
  status ENUM('active','locked','deleted') NOT NULL DEFAULT 'active',
  created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS product_models (
  model_id VARCHAR(48) NOT NULL PRIMARY KEY,
  family ENUM('main','aux') NOT NULL,
  connectivity SET('ble','wifi','lte') NOT NULL,
  voltage_capability SET('12v','24v') NOT NULL,
  config_schema_version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS devices (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  serial_number VARCHAR(64) NOT NULL UNIQUE,
  model_id VARCHAR(48) NOT NULL,
  hw_revision VARCHAR(32) NULL,
  fw_version VARCHAR(64) NULL,
  lifecycle_status ENUM('provisioning','active','suspended','retired') NOT NULL DEFAULT 'provisioning',
  created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT fk_devices_model FOREIGN KEY (model_id) REFERENCES product_models(model_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS device_bindings (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  device_id BIGINT UNSIGNED NOT NULL,
  user_id BIGINT UNSIGNED NOT NULL,
  role ENUM('owner','admin','viewer') NOT NULL,
  bound_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  revoked_at TIMESTAMP(3) NULL,
  INDEX idx_binding_device_active (device_id, revoked_at),
  INDEX idx_binding_user_active (user_id, revoked_at),
  CONSTRAINT fk_binding_device FOREIGN KEY (device_id) REFERENCES devices(id),
  CONSTRAINT fk_binding_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS device_configurations (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  device_id BIGINT UNSIGNED NOT NULL,
  revision BIGINT UNSIGNED NOT NULL,
  schema_version INT UNSIGNED NOT NULL,
  profile_id VARCHAR(64) NOT NULL,
  payload JSON NOT NULL,
  updated_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  UNIQUE KEY uq_device_config_revision (device_id, revision),
  CONSTRAINT fk_config_device FOREIGN KEY (device_id) REFERENCES devices(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS device_events (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  device_id BIGINT UNSIGNED NOT NULL,
  event_uuid CHAR(36) NOT NULL,
  event_type VARCHAR(48) NOT NULL,
  fault_code VARCHAR(48) NULL,
  occurred_at TIMESTAMP(3) NOT NULL,
  details JSON NULL,
  received_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  UNIQUE KEY uq_device_event (device_id, event_uuid),
  INDEX idx_device_event_time (device_id, occurred_at),
  CONSTRAINT fk_event_device FOREIGN KEY (device_id) REFERENCES devices(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS firmware_releases (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  release_id VARCHAR(64) NOT NULL UNIQUE,
  model_id VARCHAR(48) NOT NULL,
  version VARCHAR(64) NOT NULL,
  artifact_digest_sha256 CHAR(64) NOT NULL,
  signature_reference VARCHAR(255) NOT NULL,
  rollout_state ENUM('draft','staged','released','revoked') NOT NULL DEFAULT 'draft',
  created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT fk_firmware_model FOREIGN KEY (model_id) REFERENCES product_models(model_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS audit_events (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  actor_type ENUM('user','device','admin','system') NOT NULL,
  actor_id VARCHAR(128) NOT NULL,
  action VARCHAR(96) NOT NULL,
  target_type VARCHAR(48) NOT NULL,
  target_id VARCHAR(128) NOT NULL,
  result ENUM('accepted','rejected','failed') NOT NULL,
  occurred_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  metadata JSON NULL,
  INDEX idx_audit_target (target_type, target_id, occurred_at)
) ENGINE=InnoDB;

-- Device credentials store a one-way verifier only; raw secrets are never persisted.
CREATE TABLE IF NOT EXISTS device_credentials (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  device_id BIGINT UNSIGNED NOT NULL,
  key_id VARCHAR(96) NOT NULL UNIQUE,
  secret_hash CHAR(64) NOT NULL,
  public_key_base64 VARCHAR(64) NULL,
  public_key_algorithm VARCHAR(24) NULL,
  hash_algorithm VARCHAR(24) NOT NULL DEFAULT 'sha256',
  credential_status ENUM('active','revoked') NOT NULL DEFAULT 'active',
  created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  last_used_at TIMESTAMP(3) NULL,
  revoked_at TIMESTAMP(3) NULL,
  INDEX idx_device_credential_active (device_id, credential_status),
  CONSTRAINT fk_credential_device FOREIGN KEY (device_id) REFERENCES devices(id)
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS device_claim_codes (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  device_id BIGINT UNSIGNED NOT NULL,
  code_hash CHAR(64) NOT NULL UNIQUE,
  expires_at TIMESTAMP(3) NOT NULL,
  used_at TIMESTAMP(3) NULL,
  created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  INDEX idx_claim_device_unused (device_id, used_at, expires_at),
  CONSTRAINT fk_claim_device FOREIGN KEY (device_id) REFERENCES devices(id)
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS device_telemetry (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  device_id BIGINT UNSIGNED NOT NULL,
  sample_uuid CHAR(36) NOT NULL,
  observed_at TIMESTAMP(3) NOT NULL,
  battery_voltage_mv INT UNSIGNED NOT NULL,
  battery_current_ma INT NULL,
  temperature_centi_c SMALLINT NULL,
  state_code ENUM('normal','charging','discharging','protected','fault','unknown') NOT NULL,
  engine_running ENUM('yes','no','unknown') NOT NULL DEFAULT 'unknown',
  received_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  UNIQUE KEY uq_device_telemetry_sample (device_id, sample_uuid),
  INDEX idx_device_telemetry_time (device_id, observed_at),
  CONSTRAINT fk_telemetry_device FOREIGN KEY (device_id) REFERENCES devices(id),
  CONSTRAINT chk_telemetry_voltage CHECK (battery_voltage_mv <= 60000),
  CONSTRAINT chk_telemetry_current CHECK (battery_current_ma IS NULL OR battery_current_ma BETWEEN -1000000 AND 1000000),
  CONSTRAINT chk_telemetry_temperature CHECK (temperature_centi_c IS NULL OR temperature_centi_c BETWEEN -5000 AND 20000)
) ENGINE=InnoDB;
