# Phase 5 E4 — Formal Simulation Scenario Gate

**Baseline:** `develop@d04a014`
**Status:** BATCH COMPLETE — FORMAL SIM-001..SIM-006 PASS; evidence recorded

## Scope

E4 is the dedicated requirement-level simulation-scenario harness for the
Phase 5 exit criterion. It executes SIM-001 through SIM-006 using the existing
deterministic software providers and the actual Phase 5 policy/runtime paths.

The scenarios are fixed to the repository verification plan:

- SIM-001 — normal pre-start: hatch OPEN, fuel-vapor NORMAL, relevant inputs current/valid; virtual start permitted.
- SIM-002 — hatch CLOSED under configured BLOCK rule; virtual start rejected with hatch reason code.
- SIM-003 — fuel-vapor ALARM before start; virtual start rejected; local logical alarm and event raised.
- SIM-004 — fuel-vapor quality MISSING; fail-safe rejection; fault reason/event visible.
- SIM-005 — bilge HIGH monitoring condition; ALERT_ONLY alarm/event raised; no invented engine/starter/pump interlock.
- SIM-006 — compartment temperature exceeds configurable demonstration alarm threshold; alarm state/event raised.

## Formal-gate rule

Passing E1, E2, or E3 development self-tests did not make these formal
scenarios PASS. E4 only becomes formal scenario evidence after all of the
following are recorded on the operator workstation:

1. Existing legacy and Phase 4/Phase 5 E1-E3 regressions remain PASS.
2. The dedicated E4 native host harness reports SIM-001..SIM-006 as 6/6 PASS.
3. A fresh ESP-IDF target build succeeds from the E4 candidate source.
4. A fresh Wokwi boot executes the same six E4 scenario cases and all are PASS.
5. The E4 Wokwi verifier accepts the full latest-boot UART log, timed demo, normal return, and no fatal marker.
6. Build hashes, UART, verifier output, source hashes, and final summary are recorded as evidence.
7. LOCKED requirements remain byte-for-byte unchanged.

Until those steps complete, formal SIM-001..SIM-006 remain NOT_RUN.

## Interpretation boundaries

- All six scenarios use `source_mode=simulation` and deterministic software inputs.
- Virtual start permission/rejection never actuates a physical starter or ignition.
- SIM-005 uses the monitoring path only. Its "during run" scenario context does not create an engine-state model or stop interlock.
- Bilge monitoring remains `DISABLED` or `ALERT_ONLY`; `BLOCK` is rejected by the E3 contract.
- Temperature thresholds are demonstration/test values, not vessel trip limits.
- Local LED/buzzer behavior is a logical software request only; no GPIO driver is claimed.
- Boot-scoped alarm IDs, volatile journal events, opaque demo priority codes, and caller-provided monotonic timestamps do not establish a certified alarm system.
- No bench hardware, physical integration, calibration, field verification, certification, or production readiness is implied.

## Requirement-status boundary

A later evidence-finalization step may record SIM-001..SIM-006 as PASS if this
gate succeeds. That does not automatically make every mapped requirement fully
VERIFIED. In particular, requirements with broader unresolved scope such as
physical local output, durable/global alarm identity, approved priority
taxonomy, real clock semantics, bench execution, or field-verified vessel rules
must remain PARTIAL/NOT_RUN where appropriate.
