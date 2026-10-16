# Phase 4 Batch D1 — Provider Contract + IF-01 Door/Hatch

**Status:** BATCH COMPLETE — development/simulator gate PASS; bench hardware NOT_RUN
**Baseline required:** `develop@6069f89`
**Phase:** 4 — Bench/Simulator Drivers
**Batch:** D1
**Physical integration:** NOT_AUTHORIZED
**Bench hardware verification:** NOT_RUN

## 1. Scope

Batch D1 establishes the Phase 4 software-provider pattern and implements only IF-01 Door/Hatch.

Included:

- Common provider metadata contract: `source_mode`, `quality`, monotonic `sampled_at_ms`, non-zero provider-local `sequence`.
- Phase 4 provider provenance restricted to `simulation` and `bench_test`.
- Typed door/hatch state: `OPEN`, `CLOSED`, `UNKNOWN`.
- Deterministic software simulation provider with explicit VALID/MISSING/INVALID/STALE samples.
- Bench-facing sample constructor using already interpreted logical state.
- Negative/boundary development self-tests.
- Host validation that the existing 226 legacy core self-tests remain unchanged while D1 tests run separately.

Excluded:

- GPIO pin mapping, pull-up/pull-down choice, contact polarity, debounce implementation, electrical protection, hardware purchase/assembly, calibration, accuracy claims.
- Start-permission/blocking rules or any Phase 5 safety-policy behavior.
- Local LED/buzzer outputs.
- Telemetry schema/backend/dashboard work.
- Physical source provider.
- Formal SIM-001..015 or SUP-001..019 execution.

## 2. Requirement and interface relationship

D1 is an implementation increment toward:

- `SYS-002` source-mode separation.
- `SAF-001` door/hatch OPEN/CLOSED/UNKNOWN with quality.
- Architecture IF-01 provider abstraction and data-quality principles.

D1 does **not** mark any of these requirements VERIFIED. Formal traceability/verification remains subject to the locked baseline and later evidence.

## 3. Acceptance criteria

D1 may be called **BATCH COMPLETE** only when all items below are satisfied on the operator repository:

1. Preflight confirms branch `develop` and baseline HEAD `6069f89` before patch application.
2. SHA-256 of both LOCKED files remains unchanged.
3. No unexpected tracked modifications exist before patching; the two known local untracked files are not staged.
4. Existing `scripts/test_firmware_core_host.py` remains PASS at exactly **226/226**.
5. New `scripts/test_phase4_d1_host.py` compiles with strict C11 warnings-as-errors and reports **38/38** D1 cases PASS while confirming legacy 226/226 summaries.
6. PlatformIO ESP-IDF target build completes on the operator workstation.
7. Wokwi executes the actual built firmware and the latest boot shows:
   - all 11 legacy suite summaries unchanged,
   - `PHASE4_D1_DOOR_PROVIDER_SELFTEST: PASS (38/38)`,
   - existing finite timed demo still `CORE_RUNTIME_TIMED_DEMO: PASS (6/6)`,
   - no panic/reset in the reviewed boot.
8. Security/build-config/living-traceability checks pass or any non-applicable item is explicitly recorded as `NOT_RUN/BLOCKED`; no false PASS is allowed.
9. Actual UART/build/test logs are captured with source commit/worktree provenance before evidence is marked PASS.
10. Review confirms D1 makes no claim of bench hardware execution, calibration, marine suitability, or physical integration.
11. Explicit file manifest is reviewed before staging.
12. Local commit is created only after operator approval; **no push**.

## 4. Phase status after D1

Even if D1 passes, **Phase 4 remains PARTIAL** because IF-02 through IF-07 and their simulation/bench contracts are still pending, and bench hardware verification is not established by this batch.
