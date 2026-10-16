# Phase 7 G2 — Formal SIM-008 / SIM-009 Scenario Evidence

**Status:** BATCH COMPLETE — dedicated formal host/Wokwi SIM-008/SIM-009 gate PASS

## Purpose

G2 is a dedicated formal software-simulation scenario gate for the Phase 7
roadmap exit criterion:

- SIM-008 — NMEA checksum error / malformed-invalid sentence injection;
- SIM-009 — navigation stream loss and data-age transition.

G2 does not count the G1 unit/self-test labels as formal scenario evidence. It
executes a separate formal harness using the committed G1 navigation module.

## SIM-008

Locked verification intent:

`SIM-008 | NMEA checksum error | Malformed/invalid sentence injected | Rejected input; last valid state not refreshed.`

The dedicated G2 scenario must prove:

- a valid development navigation state exists first;
- an NMEA-style sentence is corrupted without updating its checksum;
- checksum-invalid input is rejected;
- `last_valid_ms` is unchanged;
- last valid navigation payload is preserved;
- data age continues from the previous valid update rather than from the
  rejected sentence.

## SIM-009

Locked verification intent:

`SIM-009 | Navigation stream loss | Stop NMEA input | VALID -> STALE -> OFFLINE.`

The dedicated G2 scenario must prove:

- development thresholds are supplied through configuration;
- a valid state exists before stream loss;
- no additional navigation sentence is ingested;
- before stale threshold the state remains VALID;
- at stale threshold the state becomes STALE;
- before offline threshold it remains STALE;
- at offline threshold it becomes OFFLINE;
- the last-valid timestamp remains unchanged during stream loss.

G2 demonstration thresholds are 2000 ms stale / 5000 ms offline. They are
test parameters only and are not vessel-approved operational thresholds.

## Traceability boundary

- NAV-001 maps to SIM-008.
- NAV-003 maps to SIM-008.
- NAV-004 maps to SIM-009.
- NAV-002 maps to SUP-007 and is not closed by this G2 formal scenario gate.
- The living requirement-status ledger is not modified by G2.

## Evidence rule

Formal SIM-008/SIM-009 may be marked PASS only after fresh target/Wokwi
execution and persisted evidence passes the dedicated verifier.

## Non-scope

This gate does not claim:

- full NMEA 0183 conformance;
- installed or connected Furuno GP-39 hardware;
- physical GNSS/GPS acquisition;
- antenna or serial electrical integration;
- physical bench completion;
- vessel-approved navigation thresholds;
- calibration, certification, field validation or production readiness.
