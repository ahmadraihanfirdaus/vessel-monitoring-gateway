# Phase 7 G1 — NMEA Navigation Development Foundation

**Status:** BATCH COMPLETE — development host/Wokwi gate PASS; formal SIM-008/SIM-009 NOT_RUN

## Purpose

Implement the Phase 7 development foundation required before dedicated formal
scenario evidence:

- NMEA 0183-style development sentence generation/parsing;
- checksum validation;
- navigation state with latitude, longitude, SOG, COG, fix, data age and quality;
- configurable data-age transitions VALID -> STALE -> OFFLINE;
- preservation of the last valid state when malformed or checksum-invalid input
  is rejected.

## Development sentence scope

G1 implements a **minimal RMC-shaped development subset** (`GPRMC`) because it
carries the navigation properties required by NAV-002.

This is intentionally narrow:

- it is not a full NMEA 0183 implementation;
- it does not claim Furuno GP-39 hardware is installed onboard;
- it does not claim GP-39 electrical/protocol compatibility has been bench
  verified;
- Furuno GP-39 remains a requirements reference only.

## Development thresholds

G1 self-tests use configurable demonstration values:

- stale after 2000 ms;
- offline after 5000 ms.

These values are test parameters only. They are not vessel-approved operational
thresholds.

## Verification boundary

G1 self-tests prepare the required behavior but do **not** make the formal
scenario gates PASS.

- SIM-008 remains NOT_RUN until a later dedicated scenario-evidence gate proves
  checksum/malformed rejection and that the last valid state is not refreshed.
- SIM-009 remains NOT_RUN until a later dedicated scenario-evidence gate proves
  VALID -> STALE -> OFFLINE under stopped navigation input.
- NAV-002 maps to SUP-007; SUP-007 remains NOT_RUN.
- The living requirement-status ledger is not modified by G1.

## Safety / non-scope

G1 does not implement or claim:

- physical GNSS/GPS acquisition;
- antenna, serial electrical interface, or vessel wiring;
- radar/radio/steering/engine control;
- vessel-specific navigation thresholds;
- bench-hardware completion;
- certification, field validation or production readiness.
