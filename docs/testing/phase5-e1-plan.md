# Phase 5 Batch E1 — Safety Policy Foundation

**Status:** BATCH COMPLETE — development host/Wokwi gate PASS; formal SIM-001/SIM-002 NOT_RUN

## Scope

Batch E1 introduces a pure, development-only pre-start safety policy evaluator
for the hatch/door channel. It prepares formal SIM-001 and SIM-002 execution
without implementing a physical starter interlock.

Implemented in E1:

- configuration-driven hatch rule modes: DISABLED, ALERT_ONLY, BLOCK;
- stable development reason codes for hatch closed and hatch not-current;
- virtual `start_permitted` decision only;
- explicit preservation of simulation/bench source and input quality;
- fail-safe behavior for non-current hatch data when the configured rule is
  ALERT_ONLY or BLOCK;
- strict rejection of PHYSICAL provider provenance in the Phase 5 development
  policy path;
- host/Wokwi self-test scaffolding and negative/boundary cases.

## Requirement / scenario focus

- SAF-001 — hatch OPEN/CLOSED/UNKNOWN with quality: consumed from Phase 4 provider.
- SAF-002 — virtual start request decision foundation.
- SAF-003 — blocking/alert-only behavior is configuration-driven.
- SIM-001 — normal pre-start with hatch open: prepared for formal execution.
- SIM-002 — blocking hatch closed: prepared for formal execution.

Formal SIM-001/SIM-002 are **not** claimed PASS by this batch until an explicit
scenario-evidence gate is executed and recorded. SIM-003..SIM-006 are outside
E1 and remain NOT_RUN.

## Explicit non-scope

- No physical starter, ignition, relay, GPIO, or vessel interlock.
- No certified or field-verified vessel operating rule.
- No fuel-vapor, bilge, or temperature policy integration yet.
- No local buzzer/LED implementation.
- No formal SIM/SUP completion.
- No bench hardware execution, calibration, physical integration, or production
  readiness claim.
- LOCKED requirements and traceability baseline are not modified.

## E1 development gate

1. Legacy core 226/226 remains PASS.
2. Phase 4 D1-D7 provider suites remain PASS.
3. E1 safety-policy self-test passes all expected cases.
4. Host compiler build uses strict warnings.
5. Wokwi parser self-test passes before manual simulator run.
6. ESP-IDF target build succeeds and Wokwi ELF/merged artifacts are present.
7. LOCKED SHA values remain unchanged.
8. No stage, commit, push, hardware flash, or formal scenario PASS is implied.
