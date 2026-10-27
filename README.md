# Vessel Monitoring Gateway

**Survey preparation, 2026-10-27:** [Phase14 six-area checklist](docs/testing/vessel-survey-readiness.md)
and [38-requirement local software review](docs/testing/local-software-review-20261027.md)
are available. Checklist PREPARED; survey NOT_RUN and physical integration
NOT_AUTHORIZED. Hosted CI, bench hardware and deployed TLS remain open; system
PARTIAL. Historical checkpoint metrics below retain their dated execution scope.

**Integrated Vessel Monitoring & Diagnostic Gateway**

**Portfolio category:** Embedded firmware prototype and traceable engineering development (simulation only).

This repository contains a **partial development-only monitoring prototype**, not a completed or production-ready vessel system. Roadmap Phases 3 through 8 have closed their scoped development/software-simulation exit gates: firmware core, simulator/bench-interface providers, safety policy, four-engine model, NMEA-style navigation, and telemetry contract. Phase 9 Laravel/MySQL source and historical scoped evidence are present. All **SIM-001 through SIM-015 have scoped PASS records**, including dedicated actual simulator-host outage/multifault/valid-data recovery cases; these are not physical ESP32/RTOS or final system approval. Eighteen SUP cases are recorded PASS, including bounded host-file, guarded migration and public-reference cases; SUP-018 hosted CI remains PLANNED. See the [dedicated provider evidence](evidence/test-results/formal-provider-summary-20261026.md) for the actual execution scope and navigation time-regression fix. Complete-system backend/dashboard verification, ESP32 network transport, end-to-end validation, physical bench execution, calibration, vessel integration, certification, and production readiness are not complete.


The design emphasizes modular embedded software, sensor quality, fault handling, data-source separation, and requirement traceability. Public examples are intended to use synthetic or laboratory-generated data; no operational vessel deployment is claimed.

## What Is Available Now

| Deliverable | Available content |
|---|---|
| Requirements | [38 system requirements](requirements/system-requirements.md) with priorities and defined scope |
| Traceability | [Requirement-to-test matrix](requirements/traceability-matrix.csv) linking all 38 requirements to planned cases |
| Architecture | [Architecture and interface control document](docs/architecture/architecture-and-icd.md) |
| Hardware planning | [Bill of materials and unresolved items](docs/bom-and-tbd.md) |
| Verification planning | [15 simulation scenarios](docs/testing/verification-simulation-plan.md), [19 supplemental tests](docs/testing/supplemental-verification-plan.csv), and [coverage review](docs/testing/traceability-semantic-review.md) |
| Standards research | [Standards applicability matrix](docs/standards/standards-applicability-matrix.md), for conceptual reference only |
| Executable repository tooling | Python scripts for [security screening](scripts/audit_precommit_security.py), [documentation review](scripts/audit_public_documentation.py), [host firmware self-tests](scripts/test_firmware_core_host.py), and [living traceability checks](scripts/check_living_traceability.py) |

**Available development evidence:** the [firmware evidence index](docs/testing/firmware-evidence-index.md) links the Phase 3 core history and the later Phase 4–8 development/formal-simulation evidence. Phase 5 records SIM-001..SIM-006 PASS, Phase 6 records SIM-007 PASS, and Phase 7 records SIM-008/SIM-009 PASS. Phase 8 records the telemetry-contract development gate; its dedicated backend deduplication case SIM-014 now has actual isolated MariaDB/TLS evidence; broader hardware verification remains open. This evidence does not establish full-system verification, hardware readiness, certification, or production readiness.

## Project Status

**Current resilience checkpoint2026-10-27:** dedicated actual host SIM010/012/013
[case review](evidence/test-results/formal-resilience-case-review-20261027.md) PASS:
60047ms outage,3actual503 requests,561native cycles, explicit-reset and VALID-only
recovery with4original alarm facts. Fresh PHP388, normalTLS248checks, approved
Chrome155 component and unchanged-source248command regression PASS. All15SIM
cases and18SUP have scoped PASS records; SUP018 hostedCI remains PLANNED. Derived
formal37PASS/1NOT_RUN; implementation22UNVERIFIED/16PARTIAL, no VERIFIED. Host
NO_DB_WRITE is separate from real owned DB/UI integration. Hardware/RTOS/NVS/PSA/
powerloss/deployedTLS NOT_RUN. Earlier dated checkpoints below are historical.


**Current roadmap position:** scoped Phases 3-8 and pre-Phase-9 R1 gates have committed evidence. Phase 9 implementation and historical scoped closure exist; formal verification remains open. The [guarded integration gate](docs/testing/mysql-integration-gate.md) has historical migration-roundtrip evidence; the [continuous integration checkpoint](evidence/test-results/continuous-simulation-summary-20261025.md) recorded 348 methods before the later [alarm metadata integration](evidence/test-results/alarm-metadata-summary-20261025.md), which passes 362 PHPUnit cases on the approved isolated MariaDB profile after the sixth Laravel migration and guarded roundtrip. [Security content review](docs/testing/security-scanner-review.md) has zero unresolved findings/privacy warnings with exact documented non-secret/metadata reviews; this is not publication authorization. MySQL 8 and hosted CI remain NOT_RUN. System PARTIAL; final approval NOT_APPROVED.

**Recovered event replay continuation:** the [local replay checkpoint](evidence/test-results/recovered-replay-summary-20261026.md) adds a bounded zero-wait recovery view and fair publication of original cross-boot critical facts. Native two-slot recovery fixtures traverse the actual PHP 8.2.35/MariaDB and loopback TLS/read/UI paths: 366 PHPUnit cases and 142 integration checks PASS. Queue/HTTP completion alone never deletes a retained fact or clears an alarm. The [authenticated receipt continuation](evidence/test-results/event-receipt-summary-20261026.md) implements exact-body/status HMAC, bounded durable retirement and shared owner RAM-prefix release: current PHP373 cases and actual localTLS187 checks PASS; broad229-command regression, working security and manual review PASS; exact staged gate required before local commit. Physical NVS/PSA/power-loss and formal verification remain open. Both [Codex resume](docs/handoff/CODEX_RESUME.md) and [ChatGPT context](docs/handoff/CHATGPT_CONTEXT.md) retain current Git/WIP/gates and the complete 38-requirement matrix.

**Failed event retry ordering:** the [2026-10-27 software checkpoint](evidence/test-results/event-delivery-retry-summary-20261027.md) repairs an actual native cursor skip after failed publication. Real committed TLS response loss now retries the original event, retains one MariaDB row, authenticates the duplicate200 receipt and advances only the durable host-file prefix. PHP388, TLS225, Chrome,247regression commands and both current SDK builds PASS within their recorded scopes. Explicit exhausted transport reset remains; hardware/physical durability/formal recovery are unverified.

**Receipt display lifetime:** the [latest local software checkpoint](evidence/test-results/receipt-expiry-summary-20261026.md) records actual Chrome155 open-page expiry without polling, neutral SNAPSHOT fallback without script/asset, UNKNOWN when timing is unusable, and all four receipt labels. Current PHP8.2.35/MariaDB regression is388/0fail/0skip; current strict local TLS215 and browser component gates PASS. Final broad/security/exact-index review is recorded in that checkpoint. Browser HTTP localhost to verified HTTPS upstream does not establish deployed browser TLS or physical measurement freshness. SIM010 remains NOT_RUN.

**Fault/storage and gate integrity:** [current software checkpoint](evidence/test-results/fault-storage-summary-20261026.md) records 382 PHP tests, 215 actual local TLS checks and 241 regression commands PASS, with dedicated SIM011/SUP013/SUP014/SUP017 evidence. Source drift, missing post-suite catalog checks and duplicate case shadowing are fixed in verification tooling. Formal status is 32 PASS / 2 PARTIAL / 4 NOT_RUN; implementation stays 22 IMPLEMENTED_UNVERIFIED / 16 PARTIAL. Host-file recovery is not physical NVS durability; protected files remain intact and cleanup removal count is0.

**Project entry and data/UI verification:** [current checkpoint](evidence/test-results/data-ui-summary-20261026.md) routes root to authenticated monitoring, records 377 PHP tests and 215 actual local TLS checks, and adds dedicated native identity/null/zero plus source/dedup/auth/eight-section evidence. SUP015 review is read-only; its separate integration producer writes approved owned fixtures. Physical-labelled inputs are synthetic. Canonical formal status is 28 PASS / 3 PARTIAL / 7 NOT_RUN; implementation remains 22 IMPLEMENTED_UNVERIFIED / 16 PARTIAL. Welcome cleanup is DEFERRED, removed0; protected files remain intact.

[Device read integration evidence](evidence/test-results/device-read-summary-20261025.md) records authenticated event history, filters, exact integer provenance and bounded telemetry channel hydration. [Connected dashboard evidence](evidence/test-results/dashboard-summary-20261025.md) now records per-device user grants, session security, configurable freshness and eight data-driven views. Deployment policy/channel assignments and formal verification remain open.

Current development status:

| Item | Status |
|---|---|
| Engineering requirements | 38 defined; LOCKED baseline unchanged |
| Planned verification cases | 15 SIM + 19 SUP = 34 |
| Requirement-to-test mapping | 38/38 planned |
| Firmware/provider/safety/engine/navigation/telemetry development | Scoped roadmap gates Phases 3–8 complete; total system still PARTIAL |
| Formal SIM execution | SIM-001..SIM-015 scoped PASS; host boundaries and current case review apply |
| Supplemental SUP execution | 18 recorded PASS; SUP-018 PLANNED; no requirement VERIFIED |
| Laravel/MySQL backend | PARTIAL; PHP 8.2.35 / approved MariaDB six-migration schema and current 388 tests PASS; prior guarded roundtrip recorded; direct MySQL 8 NOT_RUN |
| Dashboard / end-to-end integration | Per-grant C99/Laravel/MariaDB views, Chrome expiry/fallback and dedicated host SIM010 PASS locally; graphical operator acceptance/deployed browser TLS/physical runtime NOT_RUN |
| Firmware network / offline recovery | Host-only adapters and B3–B46 development fixtures; ESP32 Wi-Fi/TLS, durable storage and physical recovery unverified |
| CI | PR workflow source exists; hosted execution not verified in this local session |
| Physical integration | NOT_AUTHORIZED / NOT_RUN |

Roadmap-gate completion is not equivalent to complete requirement verification. The editable living register records current implementation assessments and derives per-requirement formal status from the executed SIM/SUP records. No requirement is marked `VERIFIED` by this reconciliation.

## Project Objectives

The project is designed to:

- Develop an ESP32-based edge monitoring gateway.
- Acquire, validate, and classify simulated and laboratory sensor inputs.
- Support configurable local safety-policy evaluation.
- Model a configurable number of propulsion engines with a four-engine demonstration profile.
- Detect cross-engine operating deviations in simulation.
- Process and validate NMEA 0183-style navigation data.
- Implement structured alarms, faults, events, and recovery handling.
- Maintain local monitoring behavior during network or backend outages.
- Transmit versioned telemetry to an authenticated Laravel REST API.
- Store telemetry, events, and device status in a relational database.
- Present operational data and diagnostic information through a monitoring dashboard.
- Maintain traceability between requirements, implementation, tests, and evidence.

## System Architecture

The planned system consists of four main layers:

| Layer | Responsibility |
|---|---|
| Edge Gateway | Data acquisition, validation, quality assessment, local policies, alerts, and offline handling |
| Provider Interfaces | Separation of simulation, laboratory hardware, and future verified physical interfaces |
| Backend Services | API validation, authentication, telemetry ingestion, persistence, and event management |
| Monitoring Interface | Visualization of monitoring states, diagnostics, events, and verification evidence |

Local monitoring and safety-policy evaluation are designed to operate independently of remote backend availability.

The backend is not intended to serve as a safety-critical control system.

## Technology Stack

| Component | Technology |
|---|---|
| Edge Hardware | ESP32-DevKitC V4 / ESP32-WROOM-32E |
| Firmware | C/C++ with PlatformIO |
| Simulation | Wokwi and host-based simulators |
| Backend | Laravel / PHP |
| Database | MySQL-compatible relational database |
| Dashboard | Laravel-based web interface |
| Development Environment | Windows, Visual Studio Code, Git Bash |
| Version Control | Git and GitHub |
| Continuous Integration | GitHub Actions workflow source present; hosted execution unverified here |

The listed technologies describe the selected development architecture and toolchain. Their inclusion does not imply that every software component has been implemented.

## Planned Monitoring Capabilities

### Safety and Environmental Monitoring

- Ventilation hatch or access-state monitoring.
- Fuel-vapor surrogate monitoring for laboratory demonstrations.
- Bilge or high-water surrogate monitoring.
- Compartment temperature monitoring.
- Sensor validity, fault, missing-data, and stale-data handling.
- Configurable demonstration safety policies and alert generation.

### Propulsion Simulation

- Configurable N-engine data model.
- Four-engine demonstration configuration.
- Simulated engine state, RPM, temperature, runtime, and communication quality.
- Configurable cross-engine RPM deviation detection.
- Separation between simulated engine data and future physical interface providers.

### Navigation and Motion

- NMEA 0183-style development data parsing and generation.
- Navigation position, speed over ground, course over ground, fix status, and data age.
- Navigation quality transitions, including valid, stale, and offline states.
- Prototype roll and pitch indicators.
- Vibration and motion fault indicators.

Navigation and motion features are intended for engineering demonstration and diagnostic development, not certified navigation or vessel stability assessment.

### Telemetry and Diagnostics

- Versioned telemetry payloads.
- Device and firmware identification.
- Per-channel quality metadata.
- Local event journaling and bounded offline storage.
- Backend sample deduplication.
- Network timeout, reconnection, and retry handling.
- Device health and diagnostic reporting.

## Data Source Classification

All monitoring data must identify its source mode:

| Source Mode | Definition |
|---|---|
| `simulation` | Software-generated or simulated data |
| `bench_test` | Measurements obtained from controlled laboratory hardware |
| `physical` | Reserved classification for future interfaces requiring separate verification and approval |

The `physical` classification is defined in the data contract but does not indicate that physical vessel integration has been implemented.

Invalid, missing, or stale data must not be silently presented as valid measurements.

## Safety and Engineering Limitations

This project is an engineering prototype. It is not certified marine safety, navigation, or control equipment.

The following limitations apply:

- The system is not intended to replace approved onboard equipment.
- No physical starter, ignition, steering, radar, or radio control is included.
- Safety policies are configurable demonstration rules unless separately verified.
- Simulated measurements must never be represented as actual operational measurements.
- Direct connection of ESP32 GPIO to vessel power circuits, communication buses, or NMEA electrical interfaces is prohibited.
- Any future physical interface requires appropriate isolation, protection, electrical engineering, and independent verification.
- Public test data must not contain confidential operational information.
- No claim of vessel installation, field acceptance, type approval, or regulatory certification is made.

## Repository Structure

| Directory | Purpose |
|---|---|
| `requirements/` | System requirements and traceability matrices |
| `firmware/` | ESP-IDF development firmware and Wokwi config; low-level self-tests present |
| `simulator/` | Planned hardware, engine, navigation, and fault simulation |
| `backend/` | Laravel API, migrations, read services, tests, and connected grant-scoped dashboard views |
| `docs/` | Architecture, interfaces, engineering decisions, standards, and verification plans |
| `evidence/` | Recorded historical and current firmware self-test evidence |
| `.github/workflows/` | Scoped firmware host and Laravel/MySQL CI workflow source |
| `scripts/` | Repository maintenance, validation, and audit utilities |

Directory descriptions distinguish present source/evidence from future integration. The separate `simulator/` directory remains planned; firmware simulation, backend source, and CI configuration are already tracked. Source presence does not establish executed integration or hosted CI success.

## Verification and Traceability

Development follows a requirement-driven verification process.

Planned verification includes simulation scenarios, supplemental unit and integration tests, documentation reviews, security checks, and laboratory assessments.

Each executed test must record:

- Requirement ID and test case ID.
- Relevant source commit and software version.
- Test environment and data source mode.
- Test inputs and expected behavior.
- Actual observed results.
- PASS or FAIL outcome.
- Supporting logs or screenshots.
- Known limitations.

A requirement-to-test mapping represents planned verification, not successful implementation or test execution.

The current working traceability matrix is accepted for development tracking. Final verification approval remains pending.

## How to Review This Repository

Start with the [system requirements](requirements/system-requirements.md), [architecture and interfaces](docs/architecture/architecture-and-icd.md), and [traceability status](docs/testing/traceability-status.md). The [roadmap](docs/github-repository-plan.md) records scoped Phase 3-9 history. [Current security/runtime evidence](evidence/test-results/security-php8235-summary-20261025.md) separates executed checks from historical results and remaining blockers.

With Python 3 and Git available, the two **repository-content checks** can be run from the repository root:

```bash
python scripts/audit_precommit_security.py
python scripts/audit_public_documentation.py
```

Current development verification aids can be run separately:

```bash
python scripts/test_firmware_core_host.py
python scripts/check_living_traceability.py
python scripts/audit_esp32_build_config.py
```

Native C test execution requires a GCC/Clang compiler on PATH; without one, the runner returns `BLOCKED` rather than a false PASS. See [host testing](docs/testing/host-core-testing.md), [editable traceability register](docs/testing/living-traceability-guide.md), [preliminary FMEA](docs/fmea/fmea-prototype.md), and [ESP32 configuration review](docs/engineering/esp32-build-configuration-review.md).

The first repository-content script screens Git candidates for prohibited paths and selected secret patterns. The second produces an inventory of terms requiring contextual review. **A passing audit does not authorize publication, prove confidentiality, or indicate firmware/backend test success.** Manual review is still required.

## Next Engineering Milestones

Run the MySQL 8 CI profile where available; scoped local PHP 8.2.35/MariaDB and security content gates now have evidence. Configure authorized dashboard policy/channel assignments and continue ESP32 transport/storage, receipt-order semantics and dedicated remaining SIM/SUP protocols. Host checkpoint oracles do not establish durable storage or hardware recovery. Publication retains its separate archive and disclosure-review gates.

## Engineering Baseline and Scope Control

The project is developed against a versioned internal engineering baseline.

Public-facing requirements and architecture documentation describe the applicable technical scope without disclosing identifying information about external organizations, individuals, or specific operational assets.

Hardware selections and baseline requirements are subject to formal scope control. Unverified physical interfaces, installation characteristics, and device-specific protocols remain **TBD** until independently established.

The internal engineering baseline is not included in this public repository.

## Publication and Data Policy

Public repository materials are intended to contain:

- Generic system architecture and interface definitions.
- Source code and configuration templates without credentials.
- Synthetic demonstration data.
- Approved laboratory test evidence.
- Requirement and verification documentation.
- Clearly identified limitations and development status.

The repository does not claim an operational deployment, affiliation with an external organization, or validation on a particular vessel.

## License

All rights reserved. This repository is maintained as an engineering-planning portfolio. No open-source license or general permission to reuse, modify, or redistribute its contents is granted. Viewing and GitHub platform features remain subject to applicable law and GitHub's Terms of Service.

Earlier ESP32 transport checkpoint: actual SDK adapter, guarded local build and six-step core-to-Laravel/browser integration are recorded in [transport evidence](evidence/test-results/esp32-transport-summary-20261025.md). That checkpoint recorded 326 PHP 8.2.35/MariaDB tests; later evidence below supersedes its count. Hardware, trusted-clock/TLS handshake, durable storage, hosted CI and remaining formal protocols are unverified; overall status remains PARTIAL.

The [offline storage continuation](evidence/test-results/offline-nvs-summary-20261025.md) connects a bounded two-slot NVS worker to the finite simulation and recovered C99-wire integration. Physical persistence, confidentiality, power-loss and timing remain unverified; no formal status is promoted.

The [real loopback HTTP/TLS continuation](evidence/test-results/live-http-summary-20261025.md) records 335 PHP/Laravel methods, 65 actual network assertions and ten orchestration fault methods. Cookie/form, CSRF, session/grant and certificate negatives have local evidence. Graphical browser, deployed/ESP32 TLS, physical NVS and remaining formal gates stay open.

The [continuous all-domain simulation continuation](evidence/test-results/continuous-simulation-summary-20261025.md) adds an opt-in continuous ESP32 candidate, 48-channel four-engine snapshots, compatible telemetry 1.1, and explicit demo domain presentation. Local PHP/MariaDB suite: 348 methods PASS; actual loopback TLS also checks native full-domain replay. Hardware/NVS/power-loss, deployed TLS, hosted CI and remaining formal execution stay NOT_RUN; overall PARTIAL.

The [complete alarm transition continuation](evidence/test-results/alarm-metadata-summary-20261025.md) carries immutable source/priority/reason/state/lifecycle snapshots through bounded storage, event 1.1, MariaDB and event-fact UI. Local suite: 362 PHPUnit cases and 122 actual local integration assertions PASS (including four real two-process kernel/DB race cohorts); the schema now has six Laravel migrations. ALM-001/002 software assessments are IMPLEMENTED_UNVERIFIED; formal results are unchanged. Recovered-old-boot replay/application-ACK deletion and hardware remain open; system PARTIAL.
