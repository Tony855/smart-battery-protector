-- Record the firmware's boot-locked 12V/24V classification with each sample.
ALTER TABLE device_telemetry
  ADD COLUMN IF NOT EXISTS system_voltage_class SMALLINT
  CHECK (system_voltage_class IS NULL OR system_voltage_class IN (12,24));
