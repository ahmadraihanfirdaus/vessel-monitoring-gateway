# Phase 7 G2 Summary — 2026-10-16

**PASS — formal software-simulation evidence for SIM-008 and SIM-009.**

## Formal scenario results

- SIM-008: 1/1 PASS.
  - valid navigation state established first;
  - checksum-invalid NMEA-style sentence injected;
  - invalid input rejected;
  - last-valid timestamp not refreshed;
  - last-valid navigation payload preserved;
  - age continues from the prior valid update.
- SIM-009: 1/1 PASS.
  - configurable development thresholds applied;
  - navigation stream then stops;
  - VALID before stale threshold;
  - STALE at/after stale threshold;
  - OFFLINE at offline threshold;
  - last-valid timestamp remains unchanged during stream loss.
- Combined Phase 7 formal target scenarios: 2/2 PASS.
- Timed runtime regression: 6/6 PASS.
- Stack watermark stable: 432 -> 432.

## Roadmap meaning

This evidence supports formal software-simulation **SIM-008 PASS** and
**SIM-009 PASS**, which are the Phase 7 roadmap exit scenarios.

## Boundary retained

- NAV-002 maps to SUP-007; SUP-007 remains NOT_RUN.
- The living requirement-status ledger is not modified here.
- This evidence does not claim full NMEA 0183 conformance.
- Furuno GP-39 remains a requirements reference only; installed/connected GP-39
  hardware is not claimed.
- Physical GNSS/NMEA bench verification remains NOT_RUN.
- No vessel-approved thresholds, calibration, certification, field validation
  or production readiness is claimed.
