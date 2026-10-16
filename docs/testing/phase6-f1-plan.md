# Phase 6 F1 — N-Engine Model and RPM-Deviation Development Gate

**Status:** BATCH COMPLETE — development host/Wokwi gate PASS; formal SIM-007 NOT_RUN

## Scope

F1 implements the software-only foundation required by roadmap Phase 6:

- configurable runtime N-engine model, bounded by a prototype capacity of 8;
- four-engine demonstration profile;
- per-engine state, RPM, temperature, runtime, alarm flag, and communication quality;
- configurable cross-engine RPM-deviation evaluation;
- deterministic preparation profile where engines 1/2/4 are near the same RPM and engine 3 is lower.

The implementation is simulation-only and rejects physical source mode.

## Verification boundary

F1 development self-tests prepare SIM-007 but do **not** make formal SIM-007 PASS.
Formal SIM-007 requires a later dedicated scenario-evidence gate using the
four-engine model and fresh target execution.

ENG-003 also maps to SIM-012, so Phase 6 closure does not imply every broader
engine requirement or later end-to-end scenario is complete.

## Non-scope

- No physical starter, ignition, throttle, engine-stop, steering, radar or radio control.
- No physical engine provider.
- No vessel-specific RPM threshold or field calibration.
- No claim that the bounded prototype capacity represents vessel hardware limits.
- No bench hardware, certification, field validation, production readiness, stage, commit or push.
