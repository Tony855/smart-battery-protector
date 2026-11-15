-- 003_ed25519_device_keys: use asymmetric device signatures.
-- Existing secret_hash values are retained for controlled migration/audit but no longer used.
ALTER TABLE device_credentials
  MODIFY secret_hash CHAR(64) NULL,
  ADD COLUMN public_key_base64 VARCHAR(64) NULL AFTER secret_hash,
  ADD COLUMN signature_algorithm VARCHAR(24) NOT NULL DEFAULT 'ed25519' AFTER hash_algorithm;

CREATE INDEX idx_device_credential_key_status
  ON device_credentials (key_id, credential_status);
