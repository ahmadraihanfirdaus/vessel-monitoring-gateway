# Phase 6 F1 Evidence Summary — 2026-10-16

## Result

**PASS — development host/Wokwi gate only.**

- Prior host regressions: PASS.
- Phase 6 F1 host self-test: 62/62 PASS.
- Wokwi log parser: 17/17 PASS.
- Phase 6 F1 target self-test: 62/62 PASS.
- Timed runtime regression: 6/6 PASS.
- Main stack watermark: 432 -> 432.
- `app_main()` returned normally.
- Fresh build artifact hashes were rechecked against the pre-Wokwi build.
- LOCKED requirements files remained unchanged.

## F1 scope demonstrated

- bounded configurable N-engine software model;
- four-engine demonstration profile;
- per-engine state, RPM, temperature, runtime, alarm flag and communication quality;
- configurable cross-engine RPM deviation evaluation;
- development preparation for the SIM-007 pattern where engine 3 RPM is lower than engines 1/2/4.

## Verification boundary

Formal **SIM-007 remains NOT_RUN** in F1. F1 is a development gate, not the
roadmap Phase 6 exit gate.

This evidence does not claim:

- physical engine provider or physical engine control;
- starter, ignition, throttle, stop, steering, radar or radio control;
- vessel-specific RPM calibration or field-verified thresholds;
- bench-hardware completion;
- certification, field validation or production readiness;
- completion of later SIM-012 or the full Phase 11 scenario set.
