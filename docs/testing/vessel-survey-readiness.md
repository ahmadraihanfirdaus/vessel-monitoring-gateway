# Vessel survey readiness: preparation only

**Prepared against:** develop `98455c392562d582d34051b2dfd2171f80a27df2`, 2026-10-27.
**Roadmap:** Phase 14 documentary deliverable; does not advance past the open
Phase 12 hosted-CI or Phase 13 bench-hardware exit gates.
**Checklist:** PREPARED. **Survey execution:** NOT_RUN.
**Physical integration:** NOT_AUTHORIZED. **Final approval:** NOT_APPROVED.

This checklist organizes questions for a separately authorized future technical
review. It is not a wiring guide, procurement instruction, operational procedure,
new requirement, or acceptance of residual risk. It introduces no numerical
electrical limits, pin assignments, alarm thresholds, equipment models, protocol
details, calibration values, or standards-conformity claims. Unknowns remain TBD.
No equipment, network, asset, or real-world data was surveyed to prepare it.

Use the unchanged [requirements](../../requirements/system-requirements.md),
[ICD](../architecture/architecture-and-icd.md), [BOM/TBD register](../bom-and-tbd.md),
[preliminary FMEA](../fmea/fmea-prototype.md), and
[roadmap](../github-repository-plan.md) as the authority. IF and TBD identifiers
below are existing identifiers; no new physical interface is defined here.

## Conditions before any future survey

- Obtain separate authorization for the exact review activity and information
  handling. This repository and its local software test results grant none.
- Keep asset identity, operational positions/routes, frequencies, photographs,
  confidential diagrams, credentials and other restricted material outside the
  public repository. A future public summary needs separate disclosure review.
- Review documents first. Connection, electrical measurement, packet capture,
  intrusive inspection, equipment operation, provisioning and installation each
  require their own approved scope and appropriate technical oversight.
- Preserve all LOCKED selections, TBD values, source classifications and the
  prohibition on physical starter/ignition/steering/radar/radio control.
- Stop a proposed activity if its authorization, electrical protection, interface
  specification or disclosure boundary is unknown. Record an unresolved question;
  do not infer compatibility from a software provider name or simulator result.

## Six technical review areas

All rows have **execution NOT_RUN**. The requested future evidence is a question
for an authorized reviewer, not a claim that equipment or approval exists.

| Area and existing references | Questions for a future authorized review | Evidence needed before proposing an interface | Present software boundary and decision |
|---|---|---|---|
| Propulsion: IF-09, TBD-02; ENG-001..004, SYS-004 | Confirm exact Yamaha model, actual engine quantity, available read-only diagnostic interface and whether access is permitted. Who owns the authoritative protocol and its use rights? What fault/communication states can be distinguished without control? | Authorized model/interface documentation, permitted read-only signals, units/quality/time semantics, electrical-isolation review and a separately approved verification plan. Keep asset-specific answers private. | Configurable N-engine simulation, demo four; per-engine quality and RPM deviation have scoped host evidence. Physical Yamaha provider stays a placeholder. Do not infer an installed engine count, OEM protocol, bus, connector or control command. |
| Navigation: IF-08, TBD-03; NAV-001..004 | Identify permitted navigation sources, exact equipment/interface documentation, available sentence/version information and timestamp/fix validity semantics. Is passive acquisition permitted and can a protected isolated receiver be designed? | Authorized interface description, signal direction/electrical review, permitted development examples, checksum/quality/data-age test plan. No operational position/route samples in public evidence. | RMC/GGA/VTG-style synthetic development generator/parser; GP-39 is a reference only. Corrupt/regressing input and stale/offline behavior have host evidence. No direct NMEA line-to-GPIO connection, installed GP-39 claim or complete NMEA conformity claim. |
| Radar, echo and radio: TBD-03, SYS-004; architecture equipment placeholders | Establish whether any future monitoring data interface is available, documented, permitted and actually needed within a separately approved scope. Identify operational-control paths that must remain excluded. | Authorized equipment/interface inventory and rights review, read-only boundary, isolation/protection assessment and change-control decision before any implementation proposal. | FUTURE/TBD, not an implemented acquisition path. No invented IF identifier, radar/echo/radio model, message format, frequency, connector, installed status or operational command. Presence in an architecture drawing is not implementation. |
| Electrical and low-power bench: IF-07, TBD-06; PWR-001, NET-002, SEC-002 | What power sources, grounding, protection and permitted interface points can be verified privately? What independent protected bench setup is approved? How will reset, clock trust, flash wear and power-loss behavior be evaluated? | Separately reviewed power/isolation/protection design and manufacturer documentation; approved low-power test circuit and measurement plan; explicit physical ESP32/NVS/TLS/clock/power-cut evidence before any durability or timing claim. | INA219 safe low-power bench/simulator only; no propulsion-current measurement. Potential ship supply remains TBD. SDK build and host-file recovery do not validate wiring, total stack/heap, flash durability, real-time scheduling or safe connection. No new voltage/current/pin/protection ratings are assigned. |
| Compartment sensors, local alarms and virtual start: IF-01..06, TBD-04/05/07; SAF-001..006, ALM-001..003, MOT-001, VIB-001 | Which access states, procedures and safety rules can be field-verified by an authorized party? Which sensor faults/unknown states and common-bus failures need observation? What independent bench indications and calibration/reference-frame review are required? | Authorized procedure/rule review and selected sensor specifications; protected bench design; separately recorded input failure, missing/stale data, GPIO indication and backend-outage observations. No real-vessel rule label before verification. | Adafruit 375/4965, MQ-2 surrogate, DS18B20, MPU-6050 and ADXL345 remain the selected prototype references in the BOM. No marine vapor/water/fire protection, machinery diagnosis or vessel-stability claim. Missing is never safe; ACK is not CLEAR. Pushbutton/start policy is virtual; no physical actuation. |
| Data, uplink and publication boundary: IF-10/11, TBD-01/08; TEL-001..003, API-001, DB-001, UI-001/002, SEC-001/002, TST-001/002, DOC-001 | Who authorizes collection/disclosure? What isolated development environment and deployment security policy are approved? How will device identity, external provisioning, trusted time, TLS, access grants, retention and original alarm identity be verified without exposing secrets? | Private approvals and data classification; synthetic public examples; separate deployed-TLS/physical-device/hosted-CI evidence; schema changes only through reviewed Laravel migrations. Test DB identity must be admitted fail-closed before any DB operation. | Actual local PHP/MariaDB/TLS/Chrome evidence exists; this is not deployed transport or physical ESP32 proof. Do not include secrets/APP_KEY/dotenv contents or actual coordinates in any checklist result. Physical-labelled synthetic test data is not a physical provider. No main-DB access or remote/publication action is authorized. |

## Record a future review without implying approval

For each area, record only a public-safe review identifier, existing IF/TBD and
requirement IDs, activity authorization reference, source-document revision,
question disposition, test/evidence reference and remaining dependency. Private
answers stay in their authorized location; do not copy them here. An empty answer
means unresolved, not compatible or PASS. Separate documentary review, bench
measurement, physical integration and disclosure decisions.

The existing eight TBD items remain unresolved: physical platform (01), propulsion
(02), navigation/equipment (03), access/rules (04), fuel/ventilation (05), electrical
(06), sensing (07), and disclosure (08). Preparing this checklist resolves none.

Before changing a provider, contract, selected component or rule, use the existing
engineering change-control process. Before a local commit, use the existing
scope/testing/security/exact-index gates. Never reinterpret survey preparation as
authorization to run commands on operational equipment or a production database.

## Existing evidence and continuation

The [current local software review](local-software-review-20261027.md) maps all
38 requirements to their present evidence and remaining verification boundaries.
The [living registry](living-requirement-status.csv) remains authoritative for
editable implementation/formal status; the LOCKED initial matrix is unchanged.

Current scoped software observations are in
[the resilience summary](../../evidence/test-results/formal-resilience-summary-20261027.md)
and [postcommit proof](../../evidence/test-results/formal-resilience-postcommit-98455c3-20261027.json).
Preparing this checklist does not rerun those tests, close an FMEA row, mark a
requirement VERIFIED, execute SUP-018 or satisfy any hardware/deployment gate.
Overall system status stays PARTIAL.
