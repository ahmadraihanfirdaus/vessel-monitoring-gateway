# Phase 8 H1 — Telemetry Contract Foundation

**Status:** BATCH COMPLETE — development host/Wokwi telemetry-contract gate PASS

## Purpose

Implement the Phase 8 development telemetry contract:

- versioned JSON schema;
- TEL-001 identity/source/quality fields;
- TEL-002 explicit null handling for invalid/missing values;
- stable deduplication identity definition;
- contract-level identical/conflicting duplicate classification;
- deterministic fixtures and contract tests.

## Boundary

The stable v1 identity tuple is a Phase 8 design decision:

`(device_id, boot_id, sequence)`

H1 defines duplicate semantics but does not implement backend/database
deduplication. Therefore:

- TEL-003 backend implementation is not claimed complete;
- formal SIM-014 remains NOT_RUN.

SUP-011 and SUP-012 remain NOT_RUN until their dedicated mapped verification
is explicitly executed or accepted as separate evidence.

## Network/backend boundary

Phase 8 is Telemetry Contract, not network transport or Laravel integration.

H1 does not implement NET-001, API-001 or SEC-002 behavior.

## Physical boundary

A synthetic fixture may use the `physical` source label solely to verify the
wire contract. No physical acquisition or vessel integration is implied.


## H1 execution result — 2026-10-17

- Host C telemetry-contract self-test: PASS (62/62).
- JSON fixtures/contract checks: PASS.
- ESP32/Wokwi telemetry-contract self-test: PASS (62/62).
- Wokwi log parser: PASS (21/21).
- Timed runtime regression: PASS (6/6).
- Main stack watermark: 432 -> 432.
- Target execution completed normally and returned from `app_main()`.

Two development-harness corrections were required before the final Wokwi pass:

1. Target-side per-check PASS printing was compacted because the first H1 run
   hit the ESP-IDF interrupt watchdog while repeatedly flushing console output.
   Host builds retain detailed per-check output.
2. Large H1 scratch payload/JSON buffers were moved to static boot-scoped
   self-test storage after a target IllegalInstruction/corrupted-backtrace
   failure indicated stack corruption pressure.

These corrections change only the H1 development self-test harness behavior
and scratch storage. They do not alter the telemetry v1 contract semantics.

Outstanding boundaries remain unchanged:

- SUP-011: NOT_RUN.
- SUP-012: NOT_RUN.
- TEL-003 backend/database deduplication: NOT_RUN.
- Formal SIM-014: NOT_RUN.
- Network transport/backend integration: not implemented in H1.
- Production readiness: not claimed.
