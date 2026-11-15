-- 005_device_telemetry: append-only normalized telemetry snapshots.
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
