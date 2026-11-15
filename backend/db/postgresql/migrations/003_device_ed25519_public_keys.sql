-- Public-key fields for Ed25519 device request verification.
ALTER TABLE device_credentials
  ADD COLUMN IF NOT EXISTS public_key_base64 VARCHAR(64),
  ADD COLUMN IF NOT EXISTS public_key_algorithm VARCHAR(24),
  ADD COLUMN IF NOT EXISTS signature_algorithm VARCHAR(24) NOT NULL DEFAULT 'ed25519';
