-- 004_device_claim_codes: one-time, expiring owner enrollment codes.
CREATE TABLE IF NOT EXISTS device_claim_codes (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  device_id BIGINT UNSIGNED NOT NULL,
  code_hash CHAR(64) NOT NULL,
  expires_at TIMESTAMP(3) NOT NULL,
  used_at TIMESTAMP(3) NULL,
  created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  UNIQUE KEY uq_claim_code_hash (code_hash),
  INDEX idx_claim_device_unused (device_id, used_at, expires_at),
  CONSTRAINT fk_claim_device FOREIGN KEY (device_id) REFERENCES devices(id)
) ENGINE=InnoDB;
