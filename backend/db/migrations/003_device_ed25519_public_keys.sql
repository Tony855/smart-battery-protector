-- 003_device_ed25519_public_keys: add public-key material for Ed25519 request verification.
-- Existing HMAC verifier metadata remains untouched; never store private keys here.
ALTER TABLE device_credentials
  ADD COLUMN public_key_base64 VARCHAR(64) NULL AFTER secret_hash,
  ADD COLUMN public_key_algorithm VARCHAR(24) NULL AFTER public_key_base64;
