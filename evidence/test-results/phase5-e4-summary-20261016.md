# Phase 5 E4 Formal Simulation Scenario Gate — 2026-10-16

**Baseline parent:** `develop@d04a014`
**Gate result:** **PASS — formal software-simulation scenarios SIM-001..SIM-006 (6/6)**
**Execution:** native host formal harness + fresh ESP-IDF build + fresh Wokwi target execution + UART verifier

## Scenario results

- SIM-001: PASS — normal pre-start permits virtual start.
- SIM-002: PASS — blocking hatch CLOSED rejects virtual start with reason.
- SIM-003: PASS — fuel-vapor ALARM rejects virtual start and raises logical local alarm/event.
- SIM-004: PASS — missing fuel-vapor input fails safe and keeps fault reason/event visible.
- SIM-005: PASS — bilge HIGH raises ALERT_ONLY alarm/event; no engine/starter/pump interlock is invented.
- SIM-006: PASS — high compartment temperature crosses configurable demo alarm threshold and raises alarm/event.

## Regression / target evidence

- Legacy core regression: 226/226 PASS.
- Phase 4 D1-D7 regressions: PASS.
- Phase 5 E1: 51/51 PASS.
- Phase 5 E2: 60/60 PASS.
- Phase 5 E3: 85/85 PASS.
- E4 native-host formal scenarios: 6/6 PASS.
- E4 Wokwi formal scenarios: 6/6 PASS.
- Wokwi parser self-test: 16/16 PASS.
- Wokwi timed demo: 6/6 PASS.
- Main-task stack watermark: 432 before / 432 after.
- Wokwi app version for the uncommitted E4 candidate: `d04a014-dirty`.
- Wokwi ELF prefix matches the recorded E4 target build.

## Interpretation boundary

This closes the **Phase 5 formal software-simulation scenario gate for
SIM-001..SIM-006 only**. It does not automatically make every mapped
requirement fully VERIFIED.

The evidence does not claim physical starter/ignition/engine/pump control,
physical LED/buzzer output, durable/global alarm identity, approved production
priority taxonomy, real UTC clock semantics, bench hardware execution,
calibration, physical vessel integration, field verification, certification,
or production readiness.

LOCKED requirements remain unchanged.
