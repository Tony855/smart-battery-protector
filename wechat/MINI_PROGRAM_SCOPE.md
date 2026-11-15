# WeChat Mini Program Scope v0.1

## Main pages
- Scan / bind device
- Nearby BLE devices
- Device dashboard
- Telemetry and fault status
- Protection profile
- Event history
- Help / support

## BLE workflow
1. Request required Bluetooth permissions.
2. Initialize adapter and scan.
3. Identify compatible product using advertised service/manufacturer data (final format TBD).
4. Authenticate and bind through approved ownership flow.
5. Discover GATT services and negotiate protocol version.
6. Read device state before allowing user actions.
7. Submit command request; wait for device result and independently read back actual state.

## Constraints
Mini Program suspension and phone OS background restrictions mean it cannot provide continuous safety monitoring. Device-local protection is mandatory.
