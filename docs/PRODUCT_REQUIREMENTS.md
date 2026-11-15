# Product Requirements v0.1

Status: draft baseline; electrical ratings are not frozen.

## Confirmed requirements
| Item | Requirement |
|---|---|
| System voltage | Automatic 12V/24V compatibility |
| Vehicle coverage | Passenger cars, SUVs and trucks through validated product grades/modules |
| Product type | Main-power and auxiliary-power versions |
| Connectivity | BLE base; BLE + Wi-Fi and/or 4G high-end |
| Platforms | WeChat Mini Program, Android, iOS |
| Recovery | Automatic and manual recovery, both subject to local safety checks |

## SKU matrix
- SP-AUX-BLE
- SP-AUX-PRO
- SP-MAIN-BLE
- SP-MAIN-PRO

## Rating freeze requirements
For each main-power SKU separately specify continuous current, cranking peak current and duration, make/inrush current, DC breaking voltage/current and load conditions, short-circuit withstand/protection coordination, contact resistance, temperature rise, wiring, terminals and fuse coordination. For auxiliary SKUs specify continuous current, overload curve, current limiting/short-circuit strategy and thermal conditions.

## Safety requirements
- Protection logic executes locally and does not depend on phone/cloud.
- App/cloud commands are requests; local safety state machine authorizes execution.
- Engine-running main power must not be disconnected by undervoltage logic, communications, or software restart.
- Sensor/driver/overtemperature/overcurrent faults enter defined fault handling.
- Recovery checks voltage, temperature, current, vehicle state and fault lockout.
- Thresholds depend on battery chemistry and vehicle profile; no universal defaults.

## Open decisions
Vehicle/engine envelope, current ratings, DC interruption capability, battery chemistry, IGN/D+ signal, environmental limits, IP rating, harness/terminal, target markets, LTE bands and certification.