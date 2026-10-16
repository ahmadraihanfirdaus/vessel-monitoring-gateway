# Phase 5 E2 — Fuel-Vapor Safety Policy Development Gate

**Baseline:** `develop@e75e592`
**Status:** BATCH COMPLETE — development host/Wokwi gate PASS; formal SIM-003/SIM-004 NOT_RUN

## Scope

Batch E2 extends the Phase 5 virtual pre-start policy foundation to the existing
IF-02 fuel-vapor provider. The development target is preparation for SIM-003
and SIM-004 without claiming formal scenario completion.

Implemented development behavior:

- configuration-driven `DISABLED`, `ALERT_ONLY`, and `BLOCK` fuel-vapor rule;
- current `ALARM` state can produce an explicit blocking reason;
- missing, invalid, unknown, and stale fuel-vapor data are not treated as safe;
- a condition can create a boot-scoped local alarm and bounded volatile event;
- alarm acknowledgement does not clear the underlying active condition;
- a logical local LED/buzzer request is derived without dashboard/backend input.

## Explicit boundaries

- No physical starter/ignition control or relay/GPIO interlock.
- No physical LED/buzzer driver; only a logical local-output request model.
- No calibrated gas concentration, ppm, %LEL, certified threshold, or field rule.
- No claim that MQ-2 or another sensor is installed or calibrated.
- No physical provider acceptance, vessel integration, or production readiness.
- Formal SIM-003/SIM-004 remain NOT_RUN until the dedicated scenario-evidence
  gate is executed and recorded.

## Development acceptance criteria

1. Legacy 226/226 core suites remain PASS.
2. Phase 4 D1-D7 provider suites remain PASS.
3. Phase 5 E1 51/51 remains PASS.
4. E2 fuel-vapor safety-policy self-test passes exactly 60/60 on host and Wokwi.
5. Missing/invalid/unknown/stale fuel-vapor data do not become a safe NORMAL decision.
6. SIM-003 preparation produces virtual start rejection, alarm metadata, event,
   and logical local output for an ALARM sample under a blocking configuration.
7. SIM-004 preparation produces fail-safe rejection with visible fault reason/event
   for MISSING quality under a blocking configuration.
8. Acknowledgement preserves the active underlying condition and local output.
9. Journal-full failure rolls back the attempted safety alarm transaction.
10. Wokwi timed demo remains 6/6 with no fatal markers and stack watermark recorded.
11. LOCKED requirement files retain their approved SHA-256 values.
