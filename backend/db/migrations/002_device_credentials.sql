-- 002_device_credentials: per-device credential verifier metadata.
-- Never store raw device secrets in this table or in application logs.
CREATE TABLE IF NOT EXISTS device_credentials (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  device_id BIGINT UNSIGNED NOT NULL,
  key_id VARCHAR(96) NOT NULL UNIQUE,
  secret_hash CHAR(64) NOT NULL,
  hash_algorithm VARCHAR(24) NOT NULL DEFAULT 'sha256',
  credential_status ENUM('active','revoked') NOT NULL DEFAULT 'active',
  created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  last_used_at TIMESTAMP(3) NULL,
  revoked_at TIMESTAMP(3) NULL,
  INDEX idx_device_credential_active (device_id, credential_status),
  CONSTRAINT fk_credential_device FOREIGN KEY (device_id) REFERENCES devices(id)
) ENGINE=InnoDB;
