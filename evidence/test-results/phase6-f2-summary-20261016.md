# Phase 6 F2 Evidence Summary — 2026-10-16

## Result

**PASS — formal software-simulation evidence for SIM-007.**

- Phase 6 F1 host regression: 62/62 PASS.
- F2 host formal scenario: SIM-007 1/1 PASS.
- Wokwi log parser: 25/25 PASS.
- F2 Wokwi formal SIM-007: 1/1 PASS.
- Timed runtime regression: 6/6 PASS.
- Main stack watermark: 432 -> 432.
- `app_main()` returned normally.
- Fresh F2 build artifact hashes were rechecked.
- LOCKED requirements files remained unchanged.

## SIM-007 demonstrated

A four-engine simulation profile was executed with engines 1/2/4 near the same
RPM and engine 3 lower. A configurable 250 rpm demonstration threshold was
applied. Engine 3 produced the cross-engine RPM deviation warning, while engines
1/2/4 did not produce false warnings in the same scenario.

This 250 rpm value is a software-simulation test parameter only. It is not a
vessel-calibrated or field-approved threshold.

## Verification boundary

This evidence supports formal **SIM-007 PASS** as a software-simulation
scenario.

It does **not** by itself complete every requirement associated with the engine
domain:

- ENG-003 also maps to SIM-012, which remains NOT_RUN.
- ENG-002 maps to SUP-005, which remains NOT_RUN.
- The living requirement-status ledger is not modified in this batch.

This evidence does not claim physical engine control, physical engine provider
integration, bench-hardware completion, vessel calibration, certification,
field validation or production readiness.
