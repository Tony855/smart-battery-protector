-- 003_ed25519_device_keys: use asymmetric device signatures.
-- Existing secret_hash values are retained for controlled migration/audit but no longer used.
-- IF NOT EXISTS keeps this DDL retryable after MariaDB's implicit DDL commits.
ALTER TABLE device_credentials
  MODIFY secret_hash CHAR(64) NULL,
  ADD COLUMN IF NOT EXISTS public_key_base64 VARCHAR(64) NULL AFTER secret_hash,
  ADD COLUMN IF NOT EXISTS signature_algorithm VARCHAR(24) NOT NULL DEFAULT 'ed25519' AFTER hash_algorithm;
