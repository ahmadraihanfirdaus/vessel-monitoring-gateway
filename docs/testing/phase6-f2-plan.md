# Phase 6 F2 — Formal SIM-007 Scenario Evidence

**Status:** BATCH COMPLETE — dedicated formal host/Wokwi SIM-007 gate PASS

## Purpose

Execute the roadmap Phase 6 exit scenario as a dedicated scenario-level harness:

`SIM-007 | Engine 3 RPM deviation | Engine 1/2/4 near same RPM, engine 3 lower | Cross-engine deviation warning.`

F2 uses the committed Phase 6 F1 engine model. It does not change the LOCKED
requirements or traceability matrix.

## Scenario input

The four-engine demonstration profile supplies:

- engine 1: 2000 rpm
- engine 2: 2020 rpm
- engine 3: 1500 rpm
- engine 4: 1990 rpm

The demonstration warning threshold is configured as 250 rpm for this scenario.
This is a software-simulation test parameter only. It is not a vessel-calibrated
or field-approved threshold.

## Formal pass conditions

SIM-007 passes this F2 scenario gate only when a fresh target execution proves:

1. the four-engine demonstration profile is active in simulation;
2. engine 3 RPM is lower than engines 1, 2 and 4;
3. the deviation threshold is supplied through configuration;
4. engine 3 is evaluated against three eligible peers;
5. engine 3 produces a cross-engine RPM deviation warning;
6. engines 1, 2 and 4 do not produce a false warning in the same scenario.

The target must emit:

`F2_FORMAL_SCENARIO SIM-007: PASS`

and:

`PHASE6_F2_FORMAL_SCENARIOS: PASS (1/1)`

The Wokwi verifier must then pass against the full latest boot UART log.

## Traceability boundary

- ENG-001 maps to SIM-007. F1 separately demonstrated bounded configurable
  N-engine support; F2 formally exercises the four-engine demonstration profile.
- ENG-003 maps to SIM-007 and SIM-012. Passing SIM-007 does not complete the
  later SIM-012 obligation.
- ENG-002 maps to SUP-005 and is not closed by SIM-007.

No living-requirement-status update is made in F2.

## Non-scope / safety boundary

F2 does not implement or claim:

- physical engine starter, ignition, throttle, stop, steering, radar or radio control;
- physical engine provider integration;
- vessel-specific RPM calibration or acceptance limits;
- bench-hardware completion;
- certification, field validation or production readiness.

Phase 6 roadmap closure may be considered only after formal SIM-007 target
evidence is persisted and reviewed.
