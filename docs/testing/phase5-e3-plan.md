# Phase 5 Batch E3 — Bilge / Temperature Monitoring Policy Development Gate

**Date:** 2026-10-16
**Baseline:** `develop@0036120`
**Status:** BATCH COMPLETE — development host/Wokwi gate PASS; formal SIM-005/SIM-006 NOT_RUN

## Scope

E3 prepares the development implementation path for SIM-005 and SIM-006 only.

- SIM-005: bilge/high-water monitoring condition, alert/event path, and configuration-driven behavior.
- SIM-006: compartment-temperature warning/alarm state using configurable demonstration thresholds, with alert/event path.
- Reuse the existing Phase 4 bilge and temperature provider contracts.
- Reuse the existing boot-scoped alarm, volatile journal, and logical local-output foundations.

## Safety boundary

E3 deliberately supports only `DISABLED` and `ALERT_ONLY` monitoring actions.

`VG_POLICY_RULE_BLOCK` is rejected by the E3 monitoring policy. This prevents the
SIM-005 high-water scenario from being silently interpreted as an engine-stop,
starter inhibit, pump command, or any other physical interlock.

The temperature thresholds in this batch are test/demo values only. They are not
field-verified vessel limits, machinery limits, trip points, calibration data,
or certified safety thresholds.

The local LED/buzzer output remains a logical software request only. No GPIO,
buzzer, LED, relay, starter, ignition, bilge pump, engine-stop, or other physical
control output is implemented.

## Development acceptance

Before E3 can be committed:

1. Existing core and Phase 4/Phase 5 E1/E2 host regressions remain PASS.
2. E3 host self-test passes exactly 85/85.
3. The Wokwi parser self-test passes.
4. ESP-IDF target build succeeds and Wokwi artifacts are regenerated.
5. A fresh full Wokwi boot log shows all prior suites plus E3 PASS, the timed
   demo PASS, stable recorded stack-watermark values, no fatal marker, and
   normal `app_main()` return.
6. E3 evidence is finalized and hashes verify.
7. LOCKED requirement files retain their approved SHA-256 values.
8. Exact staging excludes local `firmware/.gitignore` and `firmware/.vscode/`.

## Formal verification status

Passing this batch is **not** formal SIM-005 or SIM-006 completion.

Formal SIM-005 must still demonstrate the planned high-water scenario and
preserve configuration-driven behavior without inventing an operational
high-water interlock.

Formal SIM-006 must still demonstrate high compartment temperature against the
declared demo thresholds with the required state/event evidence.

No physical bench execution, calibration, physical integration, certification,
or production-readiness claim is authorized by this batch.
