# Vessel Monitoring Gateway

**Integrated Vessel Monitoring & Diagnostic Gateway**

**Portfolio category:** Engineering design, requirements, architecture, and verification planning.

This repository contains a **planning baseline**, not a completed monitoring system. It defines a proposed ESP32-based monitoring gateway with simulated propulsion, NMEA 0183-style navigation data, configurable local safety policies, offline telemetry, and a Laravel backend. Firmware, simulator, backend, dashboard, and system tests have **not** been implemented or executed.

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
| Executable repository tooling | Two Python scripts for [security screening](scripts/audit_precommit_security.py) and [documentation review](scripts/audit_public_documentation.py) |

**What is not available yet:** executable ESP32 firmware, a running simulator, Laravel application, monitoring dashboard, functional test results, or hardware test evidence. The Python audit tools check repository content; they do not test the proposed monitoring system.

## Project Status

**Phase 2 — Repository Foundation and Documentation Review (In Progress)**

This repository is under active development. The capabilities described below represent engineering requirements and planned functionality unless explicitly identified as implemented and verified.

Current development status:

| Item | Status |
|---|---|
| Engineering requirements | 38 defined |
| Planned verification cases | 34 |
| Requirement-to-test mapping | 38/38 planned |
| Semantic verification coverage | PARTIAL |
| Firmware implementation | NOT_IMPLEMENTED |
| Simulator implementation | NOT_IMPLEMENTED |
| Backend implementation | NOT_IMPLEMENTED |
| System verification | NOT_RUN |
| Physical integration | NOT_IMPLEMENTED |

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
| `firmware/` | Planned edge firmware and automated tests |
| `simulator/` | Planned hardware, engine, navigation, and fault simulation |
| `backend/` | Planned Laravel API, database integration, and dashboard |
| `docs/` | Architecture, interfaces, engineering decisions, standards, and verification plans |
| `evidence/` | Test results, logs, and screenshots when available |
| `.github/workflows/` | Planned continuous integration workflows |
| `scripts/` | Repository maintenance, validation, and audit utilities |

Directory descriptions include **planned locations**. In this engineering-planning snapshot, the `firmware/`, `simulator/`, `backend/`, `evidence/`, and `.github/workflows/` paths do not contain published implementation or test evidence. Their appearance in the table is a roadmap, not a claim that those directories or components exist.

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

Start with the [system requirements](requirements/system-requirements.md), [architecture and interfaces](docs/architecture/architecture-and-icd.md), and [traceability status](docs/testing/traceability-status.md). The [development roadmap](docs/github-repository-plan.md) distinguishes future implementation phases from the current planning baseline.

With Python 3 and Git available, the two **repository-content checks** can be run from the repository root:

```bash
python scripts/audit_precommit_security.py
python scripts/audit_public_documentation.py
```

The first script screens Git candidates for prohibited paths and selected secret patterns. The second produces an inventory of terms requiring contextual review. **A passing audit does not authorize publication, prove confidentiality, or indicate firmware/backend test success.** Manual review is still required.

## Next Engineering Milestones

The next work is to refine executable acceptance criteria, add automated tests for the repository audit tools, implement simulation and firmware modules, and record genuine verification evidence. Backend and dashboard implementation remain later development work as described in the [roadmap](docs/github-repository-plan.md).

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
