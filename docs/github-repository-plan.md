# 05 - GitHub Repository and Development Plan

**Project:** Vessel Monitoring Gateway

**Document Status:** Engineering Development Roadmap

**Current Phase:** Phases 3–8 scoped roadmap gates COMPLETE; Phase 9 scoped implementation audit PASS; Phase 9 scoped documentary closure RECORDED; Phase 10 local dashboard software IMPLEMENTED; formal verification OPEN

**Implementation Status:** PHASE9_SCOPED_IMPLEMENTATION_AUDIT_PASS / PHASE9_SCOPED_DOCUMENTARY_CLOSURE_RECORDED / FORMAL_VERIFICATION_OPEN / OVERALL_SYSTEM_PARTIAL

**System Verification Status:** PARTIAL — formal software-simulation SIM-001..SIM-009 PASS; SIM-010..SIM-015 NOT_RUN; 11 SUP PASS (six dedicated host cases added); 8 SUP PLANNED

Current local dashboard integration (2026-10-25): per-grant user sessions, configurable freshness, eight connected views and C99/MariaDB rendering pass 325 Laravel tests with explicit PHP 8.2.35. See [execution matrix](../evidence/test-results/dashboard-summary-20261025.md). Local software implementation is recorded; deployment policy, hosted CI, physical integration and formal verification remain open.

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
â”œâ”€â”€ README.md
â”œâ”€â”€ CHANGELOG.md                 # Planned
â”œâ”€â”€ .gitignore
â”œâ”€â”€ .gitattributes
â”œâ”€â”€ requirements/
â”‚   â”œâ”€â”€ system-requirements.md
â”‚   â””â”€â”€ traceability-matrix.csv
â”œâ”€â”€ firmware/
â”‚   â”œâ”€â”€ platformio.ini
â”‚   â”œâ”€â”€ src/
â”‚   â”‚   â”œâ”€â”€ core/
â”‚   â”‚   â”œâ”€â”€ drivers/
â”‚   â”‚   â”œâ”€â”€ providers/
â”‚   â”‚   â”œâ”€â”€ safety/
â”‚   â”‚   â”œâ”€â”€ alarms/
â”‚   â”‚   â”œâ”€â”€ engines/
â”‚   â”‚   â”œâ”€â”€ navigation/
â”‚   â”‚   â”œâ”€â”€ telemetry/
â”‚   â”‚   â””â”€â”€ diagnostics/
â”‚   â””â”€â”€ test/
â”œâ”€â”€ simulator/
â”‚   â”œâ”€â”€ wokwi/
â”‚   â”œâ”€â”€ nmea0183/
â”‚   â”œâ”€â”€ engines/
â”‚   â””â”€â”€ scenarios/
â”œâ”€â”€ backend/
â”‚   â””â”€â”€ laravel/
â”œâ”€â”€ docs/
â”‚   â”œâ”€â”€ architecture/
â”‚   â”œâ”€â”€ interfaces/
â”‚   â”œâ”€â”€ standards/
â”‚   â”œâ”€â”€ electrical/
â”‚   â”œâ”€â”€ fmea/
â”‚   â”œâ”€â”€ adr/
â”‚   â”œâ”€â”€ api/
â”‚   â””â”€â”€ testing/
â”œâ”€â”€ scripts/
â”œâ”€â”€ evidence/
â”‚   â”œâ”€â”€ test-results/
â”‚   â”œâ”€â”€ logs/
â”‚   â””â”€â”€ screenshots/
â””â”€â”€ .github/
    â””â”€â”€ workflows/
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

This does **not** mean the complete system or every requirement is verified. Phase 9 Laravel/MySQL scoped implementation has satisfied its roadmap exit criterion based on the recorded P1/P2 and post-security-fix P3 feature-test evidence; the historical P3 runtime HTTP reexecution was NOT_RUN at that checkpoint; current kernel/MariaDB reexecution is recorded separately, and Phase 9 scoped documentary closure is recorded; formal verification remains open. Phase 10 has local dashboard implementation evidence; Phase 11 end-to-end scenarios, CI/evidence consolidation, bench hardware, and survey-readiness work remain ahead. Physical integration, calibration, certification, field validation and production readiness remain unclaimed.

The working traceability state is:

| Metric | Current Value |
|---|---|
| Defined requirements | 38 |
| Simulation scenarios | 15 |
| Supplemental planned tests | 19 |
| Total planned test cases | 34 |
| Requirements with planned verification mappings | 38/38 |
| Formal SIM execution | SIM-001..SIM-009 PASS; SIM-010..SIM-015 NOT_RUN |
| Supplemental execution | SUP-001/003/006/016/019 PASS; other 14 PLANNED |
| Requirement-level final approval | NOT_APPROVED |
| Total system status | PARTIAL |

The LOCKED matrix remains a historical initial snapshot. Current implementation/formal status is maintained in `docs/testing/living-requirement-status.csv` and test-level execution records. Roadmap closure never overrides unresolved requirement scope.

Earlier 2026-10-25 checkpoint reconciliation: network/outage host adapters, authenticated dashboard placeholders and PR workflow source already exist as partial foundations. The [guarded integration gate](testing/mysql-integration-gate.md) now records explicit PHP 8.2.35 / approved MariaDB migration roundtrip, 215 Laravel/PHPUnit tests and C99 receipt crosscheck PASS. [Scoped security review](testing/security-scanner-review.md) has zero unresolved findings/warnings with exact review records. Direct MySQL 8/hosted CI, connected dashboard, durable ESP32 storage and formal closure remain open.

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

**Current Phase:** Phases 3–8 scoped roadmap gates COMPLETE; Phase 9 scoped implementation audit PASS; Phase 9 scoped documentary closure RECORDED; Phase 10 local dashboard software IMPLEMENTED; formal verification OPEN

**Implementation Status:** PHASE9_SCOPED_IMPLEMENTATION_AUDIT_PASS / PHASE9_SCOPED_DOCUMENTARY_CLOSURE_RECORDED / FORMAL_VERIFICATION_OPEN / OVERALL_SYSTEM_PARTIAL

**Functional Verification Status:** PARTIAL — SIM-001..SIM-009 PASS with formal software-simulation evidence; SIM-010..SIM-015 NOT_RUN; 11 SUP PASS (six dedicated host cases added); 8 SUP PLANNED

**Final Requirement Verification Approval:** NOT_APPROVED

**Public Publication Approval:** PENDING

**Physical Integration:** NOT_AUTHORIZED / NOT_RUN

Current ESP32 transport continuation: actual SDK adapter, guarded local build and six-step core-to-Laravel/browser integration are recorded in [transport evidence](../evidence/test-results/esp32-transport-summary-20261025.md). The complete approved PHP 8.2.35/MariaDB suite has 326 passing tests. Hardware, trusted-clock/TLS handshake, durable storage, hosted CI and remaining formal protocols are unverified; overall status remains PARTIAL.

The [offline storage continuation](../evidence/test-results/offline-nvs-summary-20261025.md) connects a bounded two-slot NVS worker to the finite simulation and recovered C99-wire integration. Physical persistence, confidentiality, power-loss and timing remain unverified; no formal status is promoted.

The [real loopback HTTP/TLS continuation](../evidence/test-results/live-http-summary-20261025.md) records 335 PHP/Laravel methods, 65 actual network assertions and ten orchestration fault methods. Cookie/form, CSRF, session/grant and certificate negatives have local evidence. Graphical browser, deployed/ESP32 TLS, physical NVS and remaining formal gates stay open.

Current continuation2026-10-26: six dedicated host casesSUP004/005/007/008/009/010
have actual121native assertions/303independent comparisons and a reproduced/fixed
navigation clock-regression defect. The current formal-provider summary records
PHP373/TLS187/broad230/bothSDK local PASS, with final staged review mandatory.
Canonical SUP11PASS/8PLANNED and per-requirement formal21PASS/3PARTIAL/14NOT_RUN
do not mean requirementVERIFIED, physical provider, hardware or production approval.
