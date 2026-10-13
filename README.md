# Vessel Monitoring Gateway

**Integrated Vessel Monitoring & Diagnostic Gateway**

**Portfolio category:** Embedded firmware prototype and traceable engineering development (simulation only).

This repository contains a **planning baseline plus partial development-only firmware implementation**, not a completed monitoring system. The ESP32 firmware has recorded Wokwi self-tests for data quality, source mode, numeric measurements, configurable ranges, alarm lifecycle, pure scheduler arithmetic, diagnostics, and an eight-entry volatile journal. Batch C2 connects these components for caller-injected simulation samples and has 169/169 native and ESP-IDF/Wokwi development self-tests PASS. Batch C3 has 201/201 development self-tests PASS on native GCC and Wokwi. Batch C4 adds 25 guard cases: **226/226** development self-tests PASS plus **6/6** ESP-IDF timed synthetic steps; formal SIM/SUP remains NOT_RUN. A continuous operational sampling loop, physical sensor providers, output alarms, nonvolatile journal storage, NMEA/engine simulators, telemetry API, Laravel backend, dashboard, and end-to-end verification are not implemented.

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

**Available firmware evidence:** [C4 Wokwi evidence](evidence/test-results/firmware-core-c4-wokwi-20261013.md) records 226/226 self-tests, six timed steps, and stack high-water-mark diagnostic; [C3 Wokwi evidence](evidence/test-results/firmware-core-c3-wokwi-20261013.md) records 201/201 self-tests plus six actual-timer simulated steps, after a verified stack overflow hotfix; [C2 evidence](evidence/test-results/firmware-core-c2-wokwi-20261013.md) records the prior 169/169 run and [C1 evidence](evidence/test-results/firmware-core-c1-wokwi-20261013.md) the prior 133/133 run. This is not full system or requirement verification. **Not available yet:** operational monitoring loop, connected sensors, Laravel application, dashboard, formal SIM/SUP execution, calibration, or hardware test evidence.

## Project Status

**Batch C4 development verified on Wokwi:** finite guard and journal-full/error latching, **226/226** native+Wokwi self-tests and **6/6** simulated timed steps, with matching firmware identity. Main-task high-water mark was 1952 bytes on the passing build versus 256 bytes before the test-only stack allocation fix. It is an observation for this bounded scenario, **not** an approved operational stack margin. Formal SIM/SUP, hardware and continuous monitoring remain NOT_RUN.

**Phase 3 — Firmware Core (PARTIAL; exit criteria NOT MET)**

This repository is under active development. The capabilities described below represent engineering requirements and planned functionality unless explicitly identified as implemented and verified.

Current development status:

| Item | Status |
|---|---|
| Engineering requirements | 38 defined |
| Planned verification cases | 34 |
| Requirement-to-test mapping | 38/38 planned |
| Semantic verification coverage | PARTIAL |
| Firmware implementation | PARTIAL: eleven firmware self-test suites and bounded ESP32 simulated timed demo; no continuous operational acquisition loop |
| Wokwi firmware simulation | 226/226 development-only self-tests and finite timed demo 6/6 recorded; formal SIM/SUP NOT_RUN |
| Backend implementation | NOT_IMPLEMENTED |
| Formal SIM/SUP and end-to-end system verification | NOT_RUN |
| Physical integration | NOT_AUTHORIZED / NOT_RUN |

Structural traceability audits have been completed. These audits do not constitute functional verification of the proposed system.

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
| Continuous Integration | GitHub Actions (planned) |

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
| `backend/` | Planned Laravel API, database integration, and dashboard |
| `docs/` | Architecture, interfaces, engineering decisions, standards, and verification plans |
| `evidence/` | Recorded historical and current firmware self-test evidence |
| `.github/workflows/` | Planned continuous integration workflows |
| `scripts/` | Repository maintenance, validation, and audit utilities |

Directory descriptions distinguish present source/evidence from future locations. `simulator/`, `backend/`, and `.github/workflows/` remain planned; firmware files and low-level evidence are already tracked.

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

Start with the [system requirements](requirements/system-requirements.md), [architecture and interfaces](docs/architecture/architecture-and-icd.md), and [traceability status](docs/testing/traceability-status.md). The [development roadmap](docs/github-repository-plan.md) distinguishes future phases from the partial Phase 3 firmware implementation.

With Python 3 and Git available, the two **repository-content checks** can be run from the repository root:

```bash
python scripts/audit_precommit_security.py
python scripts/audit_public_documentation.py
```

Batch A2 development-only verification aids can be run separately:

```bash
python scripts/test_firmware_core_host.py
python scripts/check_living_traceability.py
python scripts/audit_esp32_build_config.py
```

Native C test execution requires a GCC/Clang compiler on PATH; without one, the runner returns `BLOCKED` rather than a false PASS. See [host testing](docs/testing/host-core-testing.md), [editable traceability register](docs/testing/living-traceability-guide.md), [preliminary FMEA](docs/fmea/fmea-prototype.md), and [ESP32 configuration review](docs/engineering/esp32-build-configuration-review.md).

The first repository-content script screens Git candidates for prohibited paths and selected secret patterns. The second produces an inventory of terms requiring contextual review. **A passing audit does not authorize publication, prove confidentiality, or indicate firmware/backend test success.** Manual review is still required.

## Next Engineering Milestones

The next work is to complete Firmware Core Phase 3 (alarm lifecycle, scheduler, diagnostics, bounded journal) with executable tests and evidence before proceeding to planned providers and safety simulation. See the [roadmap](docs/github-repository-plan.md).

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
