-- 006_device_presence: server-observed last successful telemetry/event contact.
ALTER TABLE devices
  ADD COLUMN last_seen_at TIMESTAMP(3) NULL AFTER fw_version,
  ADD INDEX idx_devices_last_seen (last_seen_at);
