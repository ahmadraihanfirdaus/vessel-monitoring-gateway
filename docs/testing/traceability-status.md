# Requirement Traceability Status

**Project:** Vessel Monitoring Gateway

**Engineering Baseline:** Internal Engineering Blueprint v1.0

**Review Date:** 2026-10-25 (actual B46 HEAD and guarded integration worktree; locked matrix unchanged)

**Matrix Version:** Working v2 — Public Editorial Edition

**Matrix Status:** ACCEPTED_FOR_DEVELOPMENT

**Semantic Coverage:** PARTIAL

**Implementation Status:** PHASE3_TO_PHASE8_SCOPED_GATES_COMPLETE / OVERALL_SYSTEM_PARTIAL (locked matrix remains the initial snapshot)

**Verification Status:** PARTIAL — formal SIM-001..SIM-009 PASS; SIM-010..SIM-015 NOT_RUN; 11 SUP PASS and 8 PLANNED

**Final Verification Approval:** NOT_APPROVED

## 1. Purpose

This document records the current requirement traceability, implementation, and verification status of the Vessel Monitoring Gateway.

The working matrix supports development planning and requirement-to-test traceability.

It does not constitute evidence of implemented functionality, completed testing, standards conformity, or operational deployment.

The editable [living implementation assessment](living-traceability-guide.md) supplements the LOCKED initial matrix without changing its historical statuses. Formal SIM execution is recorded separately and currently includes SIM-001..SIM-009 PASS; later SIM and all SUP items remain open unless explicitly recorded.

## 2. Requirement Coverage

| Metric | Current Value |
|---|---|
| Total requirements | 38 |
| Mandatory requirements | 37 |
| Target requirements | 1 |
| Requirements with planned tests | 38 |
| Unmapped requirements | 0 |
| Simulation scenarios | 15 |
| Supplemental planned tests | 19 |
| Total planned test cases | 34 |
| Structural mapping coverage | 38 / 38 |
| Semantic verification coverage | PARTIAL |

All 38 requirements are linked to at least one planned verification test.

This establishes structural traceability coverage. It does not demonstrate complete acceptance-criteria coverage, successful execution, or requirement satisfaction.

## 3. Implementation Status

| Component | Current Status |
|---|---|
| Firmware core | Phase 3 scoped core-unit gate COMPLETE; overall system still PARTIAL |
| Simulator / provider interfaces | Phase 4 scoped development/simulator provider gate COMPLETE; physical bench execution NOT_RUN |
| Safety policy | Phase 5 scoped software-simulation gate COMPLETE; SIM-001..SIM-006 PASS |
| Engine model | Phase 6 scoped gate COMPLETE; SIM-007 PASS; ENG-003 also maps to SIM-012 which remains NOT_RUN |
| Navigation | Phase 7 scoped gate COMPLETE; SIM-008/SIM-009 PASS; SUP-007 now has dedicated host PASS; physical GNSS remains NOT_RUN |
| Telemetry contract | Phase 8 scoped contract gate COMPLETE; SUP-011/SUP-012, TEL-003 backend dedup and SIM-014 remain NOT_RUN |
| Laravel backend | PARTIAL; ingestion, migrations, authenticated read APIs and historical scoped evidence present |
| Monitoring dashboard | IMPLEMENTED_UNVERIFIED; grant-scoped connected views, configured freshness, event/health/evidence rendering; SIM-010/SUP-015 not executed |
| Network / offline transport | PARTIAL; actual ESP-IDF Wi-Fi/HTTPS adapter compiled locally, host oracles retained; NVS worker/transaction code connected; physical TLS/NVS durability unverified |
| CI | PARTIAL; PR workflow source present; hosted run unverified here |
| C99 / Laravel / database integration | PHP 8.2.35 / approved MariaDB migration roundtrip and 335 tests PASS; direct MySQL 8 / hosted CI NOT_RUN |
| Hardware bench verification | NOT_RUN |

Roadmap gate completion is scoped evidence, not a declaration that every mapped mandatory requirement is fully verified.

## 4. Verification Status

| Verification Activity | Current Status |
|---|---|
| Formal simulation SIM-001..SIM-006 | PASS — Phase 5 E4 dedicated host/Wokwi evidence |
| Formal simulation SIM-007 | PASS — Phase 6 F2 dedicated host/Wokwi evidence |
| Formal simulation SIM-008..SIM-009 | PASS — Phase 7 G2 dedicated host/Wokwi evidence |
| Formal simulation SIM-010..SIM-015 | NOT_RUN |
| Supplemental tests SUP-001..SUP-019 | SUP-001/003/006/016/019 PASS; other 14 PLANNED |
| Phase 8 telemetry contract fixtures/self-tests | PASS at scoped development-contract gate; not formal SUP-011/SUP-012 or SIM-014 |
| Final requirement verification approval | NOT_APPROVED |
| Total system verification | PARTIAL |

Formal scenario PASS is tracked at test level in `formal-scenario-status.csv`. The living requirement register derives requirement-level `formal_verification` as PASS only when every mapped test for that requirement has accepted PASS evidence, or PARTIAL when only some mapped tests have passed. This does not automatically promote `implementation_assessment` to `VERIFIED`.

## 5. Public Requirements and Matrix Integrity

The current public requirements and traceability matrix use approved neutral editorial wording for SYS-004 and SEC-001.

The two public wording changes preserve requirement IDs, priorities, test mappings, implementation statuses, and verification statuses.

The approved original engineering baseline and historical traceability artifacts remain preserved separately from the public repository.

### 5.1 Public System Requirements

**File:** `requirements/system-requirements.md`

**SHA-256:**

`a60167d9f2a1f852a091048447f6f4acf8d2cbfd6d11f04c2a6e2f6896f5b92b`

### 5.2 Public Working Traceability Matrix

**File:** `requirements/traceability-matrix.csv`

**SHA-256:**

`bc1fc7ce697fc6180cab760320de2a1bd814f9bc78731d4a22fdae838c303fe3`

### 5.3 Matrix Integrity Decision

The working traceability matrix is accepted for development planning.

The current public edition contains:

- 38 requirement records.
- 37 Mandatory requirements and 1 Target requirement.
- 34 distinct planned verification test IDs.
- Unchanged requirement-to-test mappings.
- Implementation status NOT_IMPLEMENTED.
- Verification status NOT_RUN.
- No recorded functional verification evidence.

The public editorial edition is not a replacement for the controlled internal engineering baseline.

## 6. Engineering Controls

The following restrictions remain in effect:

1. Preserve the approved internal engineering baseline.
2. Do not change LOCKED hardware or technical scope without documented approval.
3. Do not assign assumed values to TBD items.
4. Keep FUTURE interfaces identified as future work.
5. Separate `simulation`, `bench_test`, and `physical` data.
6. Do not invent test execution results or evidence.
7. Use Laravel migrations for all database schema changes.
8. Do not claim marine equipment certification or operational approval.
9. Do not disclose confidential vessel or third-party operational information.
10. Require appropriate verification evidence before declaring development milestones complete.

No physical vessel integration is authorized by the current project documentation.

## 7. Remaining Actions

The following work remains necessary:

1. Complete the clean tracked-only public archive procedure before publication use.
2. Preserve the [executed security/PHP 8.2.35/MariaDB gates](../../evidence/test-results/security-php8235-summary-20261025.md); separately execute the MySQL 8 CI profile. No manual database shortcut.
3. Complete ESP32 network/storage, authorized dashboard deployment configuration, receipt ordering semantics, and end-to-end verification.
4. Execute remaining formal scenarios SIM-010 through SIM-015.
5. Execute the 14 remaining supplemental tests using their specified verification methods; preserve the five existing accepted records.
6. Record actual results, source commit SHA, test environment, expected/actual outcomes, and supporting evidence.
7. Perform hardware/bench work only under the later authorized hardware gate.
8. Complete final requirement verification review before any `VERIFIED`, certification, deployment, or production-readiness claim.

## 8. Related Public Documents

- `requirements/system-requirements.md`
- `requirements/traceability-matrix.csv`
- `docs/testing/verification-simulation-plan.md`
- `docs/testing/supplemental-verification-plan.csv`
- `docs/testing/traceability-semantic-review.md`

The controlled internal engineering baseline is not included in the public repository.

## 9. Development Decision

**Working Matrix v2 Public Edition:** ACCEPTED_FOR_DEVELOPMENT

**Requirements:** 38 / 38 structurally mapped

**Planned Tests:** 34

**Semantic Coverage:** PARTIAL

**Implementation:** scoped roadmap gates Phases 3–8 COMPLETE; Phase 9 source and historical scoped closure present; complete system PARTIAL

**Formal Verification:** SIM-001..SIM-009 PASS; SIM-010..SIM-015 NOT_RUN; 11 SUP PASS and 8 PLANNED

**Final Verification Approval:** NOT_APPROVED

**Physical Integration:** NOT_AUTHORIZED / NOT_RUN

The LOCKED matrix remains unchanged as the historical initial snapshot. The editable living register and test-level execution records are the current companion status. No requirement is promoted to `VERIFIED` by this reconciliation, and no operational installation, physical integration, calibration, certification or production-readiness claim is authorized.

The [2026-10-25 device read integration](../../evidence/test-results/device-read-summary-20261025.md) adds own-device event history and verifies bounded telemetry channel hydration in 251 PHP 8.2.35/MariaDB tests. UI-002 still had placeholder views at that prerequisite checkpoint. The later [connected dashboard slice](../../evidence/test-results/dashboard-summary-20261025.md) implements browser grants, sessions, configured freshness and all eight views. UI-001/UI-002 are IMPLEMENTED_UNVERIFIED; their formal statuses remain NOT_RUN.

Current ESP32 transport continuation: actual SDK adapter, guarded local build and six-step core-to-Laravel/browser integration are recorded in [transport evidence](../../evidence/test-results/esp32-transport-summary-20261025.md). The complete approved PHP 8.2.35/MariaDB suite has 326 passing tests. Hardware, trusted-clock/TLS handshake, durable storage, hosted CI and remaining formal protocols are unverified; overall status remains PARTIAL.

The [offline storage continuation](../../evidence/test-results/offline-nvs-summary-20261025.md) connects a bounded two-slot NVS worker to the finite simulation and recovered C99-wire integration. Physical persistence, confidentiality, power-loss and timing remain unverified; no formal status is promoted.

The [real loopback HTTP/TLS continuation](../../evidence/test-results/live-http-summary-20261025.md) records 335 PHP/Laravel methods, 65 actual network assertions and ten orchestration fault methods. Cookie/form, CSRF, session/grant and certificate negatives have local evidence. Graphical browser, deployed/ESP32 TLS, physical NVS and remaining formal gates stay open.

The [continuous all-domain simulation continuation](../../evidence/test-results/continuous-simulation-summary-20261025.md) adds an opt-in continuous ESP32 candidate, 48-channel four-engine snapshots, compatible telemetry 1.1, and explicit demo domain presentation. Local PHP/MariaDB suite: 348 methods PASS; actual loopback TLS also checks native full-domain replay. Hardware/NVS/power-loss, deployed TLS, hosted CI and remaining formal execution stay NOT_RUN; overall PARTIAL.

The [complete alarm transition continuation](../../evidence/test-results/alarm-metadata-summary-20261025.md) carries immutable source/priority/reason/state/lifecycle snapshots through bounded storage, event 1.1, MariaDB and event-fact UI. Local suite: 362 PHPUnit cases and 122 actual local integration assertions PASS (including four real two-process kernel/DB race cohorts); the schema now has six Laravel migrations. ALM-001/002 software assessments are IMPLEMENTED_UNVERIFIED; formal results are unchanged. Recovered-old-boot replay/application-ACK deletion and hardware remain open; system PARTIAL.

Recovered-event continuation: native cross-boot recovery/export/serialization, actual366 PHP cases and142 local integration checks have scoped evidence in [replay summary](../../evidence/test-results/recovered-replay-summary-20261026.md). Living38 statuses remain22 IMPLEMENTED_UNVERIFIED/16 PARTIAL. No new formal or hardware approval. Both handoffs preserve current checkpoint/WIP and requirement evidence.

## Dedicated host alarm/provider verification 2026-10-26

SUP-004/005/007/008/009/010 were reviewed under their prescribed host/unit
execution classes and executed against actual modules with121native assertions
and303independent field comparisons. The dedicated run exposed/fixed navigation
arrival/age rewind; failure evidence is retained. Canonical SUP totals11PASS/
8PLANNED, per-requirement formal21PASS/3PARTIAL/14NOT_RUN. All38 implementation
assessments remain22IMPLEMENTED_UNVERIFIED/16PARTIAL; no requirementVERIFIED.
Source-bound current SDK,PHP373/TLS187 and230-command regression PASS locally.
See formal-provider-summary-20261026.md under evidence/test-results/ for exact
scope/hashes/failures and final staged gate. No new SIM/Wokwi/physical/hostedCI/
deployedTLS acceptance is inferred. Remaining requirement approval NOT_APPROVED.
