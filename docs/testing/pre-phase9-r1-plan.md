# Pre-Phase 9 Repair R1 — Correctness and Verification Hardening

**Baseline:** `develop@947b9d3`

**Status:** BATCH COMPLETE — host/build/Wokwi repair gate PASS

## Scope

This repair batch addresses repository audit findings before Phase 9:

- F-02: NMEA coordinate minute rounding/carry normalization.
- F-03: telemetry channel lookup bounds hardening.
- F-04: Phase 6–8 Wokwi verifier latest-boot isolation/order checking.
- F-06: `provider_contract.h` standalone include correctness.
- F-07: low-risk compiler/formatting cleanup.

It intentionally does not yet close:

- F-01 current status/living traceability reconciliation;
- F-05 clean public archive procedure.

Those remain separate repair batches after R1 target regression.

## Verification gates

- legacy host core 226/226;
- Phase 8 H1 host regression;
- focused NMEA rollover and telemetry malformed-count regression;
- all firmware headers standalone compile with strict warnings;
- historical Phase 6–8 verifier valid-log regression;
- mutation tests rejecting later/incomplete boot captures;
- security scan;
- ESP-IDF target build;
- fresh Wokwi full-UART verification using the R1 verifier.

No LOCKED requirement or traceability file is modified.
No database, Laravel, network transport, physical hardware, push, or production
readiness claim is part of R1.

## Execution result — 2026-10-17

R1 correctness and verifier-hardening gate passed:

- legacy host core: PASS (226/226);
- Phase 8 H1 host regression: PASS (62/62);
- focused R1 code regression: PASS (5/5);
- standalone firmware headers: PASS (44/44);
- Wokwi verifier boot-isolation regression: PASS (15/15);
- automated security screen: PASS;
- ESP-IDF target build: PASS;
- fresh Wokwi parser: PASS (21/21);
- G1 navigation target regression: PASS (64/64);
- H1 telemetry target regression: PASS (62/62);
- timed demo: PASS (6/6);
- stack watermark: 432 -> 432.

R1 does not complete F-01 status/living-traceability reconciliation or F-05
clean public archive procedure. Those remain separate pre-Phase-9 repair
batches. Formal SIM/SUP status is not promoted by R1. TEL-003 backend
deduplication, SIM-014, physical verification and production readiness remain
unclaimed. Total system status remains PARTIAL.
