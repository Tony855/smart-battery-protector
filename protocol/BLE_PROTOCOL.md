# BLE GATT Protocol Draft v0.1

Logical characteristics only; UUIDs and wire encoding are TBD.

| Characteristic | Properties | Fields |
|---|---|---|
| DeviceInfo | Read | model, hw_rev, fw_rev, serial, capabilities |
| LiveTelemetry | Read/Notify | voltage_mV, current_mA, temperature_dC, switch_state, operating_state |
| ProtectionConfig | Auth Read/Write | low_voltage_mV, recovery_voltage_mV, delay_s, mode, revision |
| ControlRequest | Auth Write | request_id, action, nonce/counter, expiry |
| CommandResult | Notify | request_id, accepted, reason_code, resulting_state |
| FaultLog | Read | event_id, fault_code, timestamp, details |
| OtaControl | Auth | manifest, image_size, digest, transfer_state |

Security: no fixed plaintext password; MAC address is not identity; authenticated binding; anti-replay counters/nonces; command expiry and idempotency; strict parameter validation; signed OTA with model/version checks.