# 05 - GitHub Repository and Development Plan

**Project:** Vessel Monitoring Gateway

**Document Status:** Engineering Development Roadmap

**Current Phase:** Phases 3–8 scoped roadmap gates COMPLETE; pre-Phase-9 hardening in progress; Phase 9 NOT_STARTED

**Implementation Status:** PHASE3_TO_PHASE8_SCOPED_GATES_COMPLETE / OVERALL_SYSTEM_PARTIAL

**System Verification Status:** PARTIAL — formal software-simulation SIM-001..SIM-009 PASS; SIM-010..SIM-015 and SUP-001..SUP-019 remain open

## 1. Purpose

This document defines the planned repository structure, development phases, verification milestones, and publication boundaries for the Vessel Monitoring Gateway.

The project is a standards-aware engineering prototype focused on embedded monitoring, simulated propulsion, navigation data processing, fault management, local safety-policy evaluation, and telemetry.

The repository is intended to demonstrate a traceable engineering development process.

This roadmap does not represent completed system implementation, operational deployment, or successful functional verification.

## 2. Repository Identity

The repository identifier is:

`vessel-monitoring-gateway`

The public presentation title is:

**Integrated Vessel Monitoring & Diagnostic Gateway**

The repository identity is independent of any specific operational vessel, organization, or external affiliation.

## 3. Planned Repository Structure

The following directory structure represents the intended development organization.

Some directories and files may not exist during the initial project phases.

```text
vessel-monitoring-gateway/
├── README.md
├── CHANGELOG.md                 # Planned
├── .gitignore
├── .gitattributes
├── requirements/
│   ├── system-requirements.md
│   └── traceability-matrix.csv
├── firmware/
│   ├── platformio.ini
│   ├── src/
│   │   ├── core/
│   │   ├── drivers/
│   │   ├── providers/
│   │   ├── safety/
│   │   ├── alarms/
│   │   ├── engines/
│   │   ├── navigation/
│   │   ├── telemetry/
│   │   └── diagnostics/
│   └── test/
├── simulator/
│   ├── wokwi/
│   ├── nmea0183/
│   ├── engines/
│   └── scenarios/
├── backend/
│   └── laravel/
├── docs/
│   ├── architecture/
│   ├── interfaces/
│   ├── standards/
│   ├── electrical/
│   ├── fmea/
│   ├── adr/
│   ├── api/
│   └── testing/
├── scripts/
├── evidence/
│   ├── test-results/
│   ├── logs/
│   └── screenshots/
└── .github/
    └── workflows/
```

The directory tree is a development target, not an assertion that all listed modules or artifacts already exist.

Git does not preserve empty directories unless tracked files are added.

## 4. Development Phase Plan

The project follows sequential implementation and verification phases.

Each phase has defined work and exit criteria. Advancement requires review of the relevant results and evidence.

| Phase | Name | Planned Work | Exit Criterion |
|---|---|---|---|
| 0 | Baseline Package | Approve the internal engineering baseline; freeze scope, naming, and exclusions. | No coding before baseline sign-off. |
| 1 | Environment Audit | Audit Windows, VS Code, Git, PlatformIO, PHP, Composer, Laravel, MySQL, Node.js, and Wokwi. | Exact tool versions and required build commands recorded. |
| 2 | Repository Skeleton | Establish directories, README, ADRs, requirement IDs, and planned CI configuration. | Repository can be cloned cleanly and required foundation files are available. |
| 3 | Firmware Core | Implement scheduling, data quality, diagnostics, event journal, and alarm state model. | Core unit tests completed with recorded results. |
| 4 | Bench/Simulator Drivers | Implement door, gas surrogate, bilge, temperature, motion, vibration, and power providers. | Each required driver supports the specified simulation and bench interfaces. |
| 5 | Safety Policy Engine | Implement configurable pre-start safety policies and reason codes. | SIM-001 through SIM-006 pass with evidence. |
| 6 | Four-Engine Model | Implement configurable N-engine abstraction, four-engine demonstration profile, and deviation detection. | SIM-007 passes with evidence. |
| 7 | NMEA Navigation | Implement development sentence generation/parsing, data-age handling, and checksum validation. | SIM-008 and SIM-009 pass with evidence. |
| 8 | Telemetry Contract | Define and implement versioned JSON schema, quality/source metadata, and deduplication identity. | Fixtures and contract tests pass. |
| 9 | Laravel/MySQL | Implement migrations, authenticated ingestion, state/history/event persistence, device health, and API validation. | Backend API tests pass. |
| 10 | Dashboard | Implement monitoring overview, safety, propulsion, navigation, power, alarms, diagnostics, and evidence views. | Live, stale, offline, and source-mode states are clearly distinguishable. |
| 11 | End-to-End Simulation | Integrate simulation sources, ESP32 processing, API, database, and dashboard. | SIM-001 through SIM-015 have recorded verification evidence. |
| 12 | CI and Evidence | Configure GitHub Actions, unit/integration checks, evidence artifacts, and Wokwi CI if feasible. | Required CI checks pass on a clean clone. |
| 13 | Bench Hardware | Assemble selected prototype components in a controlled laboratory environment. | Bench-test evidence is recorded separately from simulation evidence. |
| 14 | Vessel Survey Readiness | Prepare a technical checklist for future verification of engine, navigation, radar, electrical, and compartment interfaces. | Survey-readiness documentation completed; no physical vessel integration authorized. |

## 5. Current Development Status

Roadmap Phases 3 through 8 have each satisfied their **scoped development/software-simulation exit criterion** with committed evidence. This includes the firmware-core gate, development simulator/bench-interface providers, safety-policy scenarios, four-engine model, NMEA-style navigation, and telemetry-contract foundation. Pre-Phase-9 repair R1 subsequently corrected identified firmware edge cases and hardened Wokwi log verification without changing the LOCKED baseline.

This does **not** mean the complete system or every requirement is verified. Phase 9 Laravel/MySQL, Phase 10 dashboard, Phase 11 end-to-end scenarios, CI/evidence consolidation, bench hardware, and survey-readiness work remain ahead. Physical integration, calibration, certification, field validation and production readiness remain unclaimed.

The working traceability state is:

| Metric | Current Value |
|---|---|
| Defined requirements | 38 |
| Simulation scenarios | 15 |
| Supplemental planned tests | 19 |
| Total planned test cases | 34 |
| Requirements with planned verification mappings | 38/38 |
| Formal SIM execution | SIM-001..SIM-009 PASS; SIM-010..SIM-015 NOT_RUN |
| Supplemental execution | SUP-001..SUP-019 PLANNED / NOT_RUN |
| Requirement-level final approval | NOT_APPROVED |
| Total system status | PARTIAL |

The LOCKED matrix remains a historical initial snapshot. Current implementation/formal status is maintained in `docs/testing/living-requirement-status.csv` and test-level execution records. Roadmap closure never overrides unresolved requirement scope.

## 6. Verification and Evidence Requirements

Engineering verification shall maintain traceability from requirements to implementation, tests, and evidence.

An executed test record shall identify:

- Requirement ID.
- Test case ID.
- Source commit SHA.
- Firmware or backend software version, where applicable.
- Test environment and data source mode.
- Test input or stimulus.
- Expected outcome.
- Actual observed outcome.
- PASS or FAIL result.
- Supporting logs, screenshots, or other evidence.
- Known limitations.

Test execution evidence must be produced from actual test runs.

Planned or proposed test cases must not be reported as completed verification.

## 7. Data Source Separation

The system defines three source modes:

| Source Mode | Intended Meaning |
|---|---|
| `simulation` | Software-generated development data |
| `bench_test` | Controlled laboratory prototype measurements |
| `physical` | Reserved classification for separately verified and authorized future interfaces |

Defining a source mode does not prove that the corresponding physical integration exists.

All published demonstrations shall use synthetic or appropriately approved laboratory data.

## 8. Safety and Integration Boundaries

The following engineering restrictions apply throughout development:

- Backend failure must not disable required local monitoring, alarms, or safety-policy evaluation.
- The prototype shall not control an operational starter, ignition, steering, radar, or radio system.
- Direct connection of ESP32 GPIO to operational electrical circuits and communication lines is prohibited.
- Simulated sensor values shall not be represented as real-world operational measurements.
- Unverified physical interfaces must remain designated FUTURE or TBD.
- Selected LOCKED hardware and approved requirements must not be changed without documented review.
- No marine certification, regulatory approval, or operational safety capability is claimed.

Future physical interface development requires separate verification, appropriate electrical engineering, and authorization.

## 9. Public Repository Boundaries

Public documentation shall describe the engineering system without disclosing identifying or restricted third-party information.

The repository shall not include:

- Identifying details of specific operational vessels.
- Hull identifiers or asset registration codes.
- Confidential information about external organizations or individuals.
- Actual operational routes or coordinates.
- Radio frequencies or restricted communication details.
- Credentials, access tokens, private keys, or production secrets.
- Unapproved installation diagrams or operational asset configurations.
- Unsupported claims of external affiliation, deployment, or field validation.

Manufacturer names may be used as technical product references. Their inclusion does not imply endorsement, partnership, or equipment installation.

Internal engineering reference materials are maintained outside the public repository.

## 10. Scope and Change Control

The project follows a versioned internal engineering baseline.

Changes to requirements, hardware selections, interface contracts, or development scope require documented review and approval.

Public documentation may be edited to improve clarity, neutrality, and confidentiality without changing the underlying approved technical requirements.

Items marked TBD shall not be assigned assumed values.

Items marked FUTURE shall not be described as implemented functionality.

## 11. Repository Publication Criteria

Before the repository is made public:

1. Documentation must be reviewed for sensitive or identifying information.
2. Internal-only materials must be excluded from Git staging and publication.
3. No credentials or confidential information may be included.
4. Public descriptions must distinguish planned, implemented, and verified capabilities.
5. Scope and interface documentation must remain consistent with the approved baseline.
6. The repository must not claim unverified deployment, certification, or external affiliation.
7. Git history and staged content must be checked before publication.
8. Licensing must be reviewed before granting public reuse permissions.

### 11.1 Publication Authorization and Provenance Gate

The preceding checks support a publication decision but do not establish ownership, confidentiality clearance, third-party permissions, or permission to disclose internal engineering material. A passing automated scan is not publication authorization.

Before changing repository visibility, confirm and document:

- **Material rights and provenance:** Authorship or explicit permission to publish each relevant design, text, diagram, source file, image, dataset, and third-party inclusion. Exclude or replace any material with unresolved disclosure or reuse rights.
- **Public exposure review:** Review all files, tracked history, branches, tags, commit metadata, and any GitHub-exposed attachments or activity (including releases, issues, pull requests, and Actions artifacts or logs, where applicable).
- **Evidence provenance:** Restrict public examples to synthetic data or separately authorized bench material. Internal baseline records and private archives remain outside the public repository.
- **License decision:** All Rights Reserved; no open-source license or general reuse permission is granted. Public GitHub visibility does not override applicable law or GitHub's Terms of Service, nor grant rights to reproduce third-party material.
- **Explicit authorization:** Record a dated publication decision by the person or party authorized to approve disclosure. This is distinct from system verification, engineering approval, and any hardware integration authorization.

If the required rights or publication authorization cannot be confirmed, the repository shall remain **PRIVATE** and publication approval shall remain **PENDING**. This subsection is a disclosure-control checkpoint; it does not amend the engineering baseline or mark development and verification work as complete.

## 12. Current Decision

The repository is under preparation for continued engineering development and public portfolio review.

**Current Phase:** Phases 3–8 scoped roadmap gates COMPLETE; pre-Phase-9 hardening active; Phase 9 NOT_STARTED

**Implementation Status:** PHASE3_TO_PHASE8_SCOPED_GATES_COMPLETE / OVERALL_SYSTEM_PARTIAL

**Functional Verification Status:** PARTIAL — SIM-001..SIM-009 PASS with formal software-simulation evidence; SIM-010..SIM-015 and SUP-001..SUP-019 remain open

**Final Requirement Verification Approval:** NOT_APPROVED

**Public Publication Approval:** PENDING

**Physical Integration:** NOT_AUTHORIZED / NOT_RUN
