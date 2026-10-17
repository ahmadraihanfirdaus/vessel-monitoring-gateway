# Traceability Semantic Coverage Review

**Project:** Vessel Monitoring Gateway

**Engineering Baseline:** Internal Engineering Blueprint v1.0

**Document Status:** Working Semantic Review

**Traceability Status:** ACCEPTED_FOR_DEVELOPMENT

**Implementation Status:** NOT_IMPLEMENTED

**Verification Status:** NOT_RUN

**Semantic Coverage:** PARTIAL

**Final Verification Approval:** NOT_APPROVED

## 1. Purpose

This document reviews the semantic relevance of planned verification mappings for the Vessel Monitoring Gateway.

The review distinguishes between:

- Structural traceability, which establishes links between requirements and planned tests.
- Semantic coverage, which evaluates whether the planned tests adequately address required behavior.
- Test execution, which produces observed results and supporting evidence.
- Final verification approval, which requires completed and reviewed evidence.

A mapped test represents planned verification coverage. It does not establish successful execution or requirement compliance.

The current working traceability matrix contains 38 requirements mapped to 15 simulation scenarios and 19 supplemental verification tests.

## 2. Simulation Coverage Review

The following assessments are retained from the initial engineering review.

| Scenario | Assessment | Required follow-up |
|---|---|---|
| SIM-001 | PARTIAL | Verify hatch state, quality and permit reason |
| SIM-002 | PARTIAL | Verify configurable blocking rule and reason code |
| SIM-003 | PARTIAL | Verify full alarm metadata, local output and event |
| SIM-004 | PARTIAL | Verify missing quality never becomes safe |
| SIM-005 | PARTIAL | Verify configurable action without invented interlock |
| SIM-006 | PARTIAL | Verify demo thresholds, quality and event |
| SIM-007 | PARTIAL | Verify four-engine profile and deviation; separately test N-engine support |
| SIM-008 | PARTIAL | Verify invalid input rejection and navigation data age; separately test generator/reference constraints |
| SIM-009 | DIRECT | Verify configurable VALID to STALE to OFFLINE thresholds |
| SIM-010 | PARTIAL | Verify uninterrupted local operation, bounded retry and offline UI |
| SIM-011 | CONDITIONAL | Use compartment temperature to cover SAF-006; verify isolation |
| SIM-012 | PARTIAL | Verify combined failures, event ordering and no deadlock |
| SIM-013 | PARTIAL | Verify recovery only after valid data and reconnect behavior |
| SIM-014 | DIRECT | Test identical duplicate and conflicting duplicate |
| SIM-015 | PARTIAL | Verify rejected authentication; separately test full API contract and HTTPS |

Assessment interpretation:

- **DIRECT:** The scenario directly addresses an identified requirement behavior. It does not mean the test has passed or that every acceptance criterion is covered.
- **PARTIAL:** The scenario addresses relevant behavior but requires additional assertions, test cases, or acceptance criteria.
- **CONDITIONAL:** The relationship depends on selecting the appropriate channel, stimulus, configuration, or implementation context.

These assessments describe planned coverage only.

No simulation scenario has been marked as executed or passed.

## 3. Supplemental Verification Coverage

The initial simulation-only review identified 19 requirements requiring additional planned verification.

Those gaps have since been addressed at the structural mapping level by defining supplemental tests SUP-001 through SUP-019.

| Test ID | Requirement ID | Planned Verification Focus |
|---|---|---|
| SUP-001 | SYS-001 | Prototype scope and certification disclaimer review |
| SUP-002 | SYS-002 | Source-mode separation |
| SUP-003 | SYS-004 | Prohibited physical and third-party mission-system control |
| SUP-004 | ALM-002 | Alarm acknowledgement behavior |
| SUP-005 | ENG-002 | Simulated engine state and diagnostic fields |
| SUP-006 | ENG-004 | Physical engine provider placeholder |
| SUP-007 | NAV-002 | Navigation state fields and data quality |
| SUP-008 | MOT-001 | Attitude/motion labeling and limitations |
| SUP-009 | VIB-001 | Vibration indicator and fault behavior |
| SUP-010 | PWR-001 | Safe low-power monitoring boundary |
| SUP-011 | TEL-001 | Telemetry identity and quality contract |
| SUP-012 | TEL-002 | Missing and invalid value handling |
| SUP-013 | NET-002 | Offline state and bounded event journal |
| SUP-014 | DB-001 | Database migration control |
| SUP-015 | UI-002 | Required dashboard views |
| SUP-016 | SEC-001 | Public repository confidentiality and secret review |
| SUP-017 | TST-001 | Requirement-to-code-to-test-to-evidence traceability |
| SUP-018 | TST-002 | Firmware/backend CI checks and conditional Wokwi CI |
| SUP-019 | DOC-001 | Engineering documentation and evidence inventory |

All supplemental tests remain PLANNED.

The introduction of these tests resolves the previously identified absence of planned test mappings for the listed requirements.

It does not demonstrate complete semantic coverage, implemented behavior, or successful verification.

The authoritative supplemental test definitions are maintained in:

`docs/testing/supplemental-verification-plan.csv`

### 3.1 Verification Method and Coverage Boundaries

The following notes clarify selected existing mappings. They do not introduce new tests, alter approved requirement-to-test relationships, or establish completed verification.

- **SIM-011 / SAF-006:** The specified stimulus is one invalid sensor while other channels remain valid. Compartment-temperature fault isolation is relevant only when that channel is selected. This scenario alone does not verify a shared sensor-bus outage or all valid, invalid, missing, stale, and configurable-temperature-threshold behaviors required by SAF-006.
- **SUP-002 / SYS-002:** The planned contract test checks source_mode separation using synthetic payloads, including data labelled physical. Such labels do not establish real physical acquisition, connected equipment, or authorized operational integration.
- **SUP-010 / PWR-001:** The planned simulation test evaluates synthetic low-power measurements and quality handling. PWR-001 allows an INA219 or simulator, but this simulation does not demonstrate physical INA219 measurements, wiring compatibility, or electrical safety validation.

All three mappings remain planned verification activities. Semantic coverage remains PARTIAL, and execution status remains NOT_RUN.

## 4. Current Traceability Assessment

| Metric | Current Value |
|---|---|
| Total requirements | 38 |
| Mandatory requirements | 37 |
| Target requirements | 1 |
| Simulation scenarios | 15 |
| Supplemental planned tests | 19 |
| Total planned test cases | 34 |
| Requirements with planned test mappings | 38 / 38 |
| Structural mapping coverage | 100% |
| Semantic coverage | PARTIAL |
| Implementation status | NOT_IMPLEMENTED |
| Verification execution | NOT_RUN |
| Final verification approval | NOT_APPROVED |

Structural mapping coverage measures the presence of planned test references for requirement IDs.

It does not measure the completeness of assertions, adequacy of acceptance criteria, implementation correctness, or actual verification results.

Semantic coverage remains PARTIAL until the planned test definitions and their acceptance criteria have undergone further review.

## 5. Coverage and Evidence Rules

1. Every requirement must have planned verification.
2. One scenario may cover multiple requirements.
3. A mapping does not imply complete requirement coverage.
4. Requirements may need multiple test cases.
5. Simulation and bench evidence must remain distinct.
6. No test shall be marked PASS before execution.
7. Evidence must reference requirement ID, test ID, commit SHA, environment, input and actual result.
8. Physical integration must not be claimed from simulation.
9. Security verification must include more than bad-token tests.
10. Documentation and CI requirements need their own checks.

Additional controls:

- Requirement IDs, priorities, and approved scope shall remain traceable to the internal engineering baseline.
- Public editorial wording must remain consistent with the approved public requirements and traceability matrix.
- Test results must distinguish expected outcomes from observed outcomes.
- Missing evidence shall not be replaced with assumed results.
- All unverified hardware and physical interface details must retain their approved TBD or FUTURE designation.
- A planned verification mapping must not be interpreted as marine certification or operational approval.

## 6. Review Decision

The working traceability matrix has been accepted for development planning.

All 38 requirements are structurally mapped to at least one planned verification test.

However:

- System implementation remains NOT_IMPLEMENTED.
- Simulation and supplemental tests remain NOT_RUN or PLANNED, as applicable.
- Supporting functional verification evidence has not been produced.
- Semantic verification coverage remains PARTIAL.
- Final verification approval remains NOT_APPROVED.

**Decision: ACCEPTED_FOR_DEVELOPMENT — NOT_APPROVED_FOR_FINAL_VERIFICATION.**

This decision authorizes continued development planning under the approved scope. It does not authorize deployment, physical integration, or claims of completed verification.

## 7. Next Actions

The following activities remain necessary:

1. Review and refine acceptance criteria for partial and conditional simulation coverage.
2. Validate the detailed verification methods for all 19 supplemental tests.
3. Establish requirement-to-implementation references as development progresses.
4. Execute tests in their designated simulation or controlled bench environments.
5. Record actual results, configurations, logs, and evidence.
6. Reassess semantic coverage after implementation and test execution.
7. Perform final verification review before claiming requirement satisfaction.

## 8. Related Documents

- `requirements/system-requirements.md`
- `requirements/traceability-matrix.csv`
- `docs/testing/verification-simulation-plan.md`
- `docs/testing/supplemental-verification-plan.csv`
- `docs/testing/traceability-status.md`

The internal engineering blueprint remains the controlled technical reference and is not included in the public repository.

## 9. Current Status

**Requirements:** 38

**Planned Verification Tests:** 34

**Structural Traceability:** 38 / 38

**Semantic Coverage:** PARTIAL

**Implementation:** NOT_IMPLEMENTED

**Verification:** NOT_RUN

**Final Approval:** NOT_APPROVED

This document records a working semantic coverage assessment, not a completed system verification report.
