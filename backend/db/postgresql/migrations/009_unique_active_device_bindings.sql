-- Prevent concurrent membership writes from creating duplicate active bindings.
-- This migration intentionally does not delete or merge existing rows. If duplicate
-- active bindings exist, inspect and reconcile them before retrying the migration.
CREATE UNIQUE INDEX IF NOT EXISTS uq_device_bindings_active_device_user
  ON device_bindings(device_id, user_id)
  WHERE revoked_at IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_device_bindings_active_owner
  ON device_bindings(device_id)
  WHERE role = 'owner' AND revoked_at IS NULL;
