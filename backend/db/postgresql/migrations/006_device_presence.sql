-- Server-observed last successful signed telemetry/event contact.
ALTER TABLE devices ADD COLUMN IF NOT EXISTS last_seen_at TIMESTAMPTZ(3);
CREATE INDEX IF NOT EXISTS idx_devices_last_seen ON devices(last_seen_at);
