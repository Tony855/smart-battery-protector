# Device credential storage and lifecycle

## Implemented Ed25519 credential contract
- Each device request uses a unique `key_id` and Ed25519 signature.
- The backend stores the 32-byte Ed25519 public key as Base64, with both `public_key_algorithm` and `signature_algorithm` required to equal `ed25519`.
- The corresponding private key belongs to the device and must never be stored in the backend database, source control, logs, analytics or support exports.
- The API credential lookup is read-only and returns only the device ID and decoded public key.
- The `secret_hash` column is a legacy schema field and is not used by the current Ed25519 request verifier. One-time owner claim codes are separate credentials and are stored only as SHA-256 digests.

## Current provisioning boundary
The repository includes a controlled claim-code provisioning script. It does not yet implement device-side Ed25519 key generation, secure-element injection, public-key enrollment, signed manufacturing records or automated key rotation. Do not create production credentials by inserting ad-hoc keys into the database or copying private keys through support channels.

## Rotation and revocation requirements
1. Generate a replacement device key inside the approved device/manufacturing trust boundary.
2. Enroll its public key under a new unique key ID through a reviewed administrative workflow.
3. Validate signed requests with the new key on a representative device.
4. Revoke the old credential and record operator, device, key ID and change evidence without recording private material.
5. Define recovery for lost, damaged or compromised devices before production deployment.

The database supports credential status and key metadata, but an operator-facing rotation/revocation workflow and production key custody are not yet implemented. Local firmware protection must remain independent of cloud authentication.
