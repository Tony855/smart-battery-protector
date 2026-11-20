-- Match accepted telemetry to the TMP117 and portable firmware conversion envelope.
ALTER TABLE device_telemetry
  DROP CONSTRAINT IF EXISTS device_telemetry_temperature_deci_c_check;

ALTER TABLE device_telemetry
  ADD CONSTRAINT device_telemetry_temperature_deci_c_check
  CHECK (temperature_deci_c IS NULL OR temperature_deci_c BETWEEN -550 AND 1500);
