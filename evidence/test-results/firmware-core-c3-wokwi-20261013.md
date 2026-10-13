# Batch C3 — Wokwi finite simulated runtime evidence (2026-10-13)

**Scope:** Development-only self-tests on Wokwi ESP32 with ESP-IDF 6.1.0 and a bounded six-step `esp_timer`/FreeRTOS synthetic demonstration. The UART below is derived from operator-provided serial console content. These are **not** formal SIM/SUP verification, real hardware results, calibration, or a continuous monitoring runtime.

## Identity and provenance

- Source checkpoint at build time: `develop@4840366-dirty` (uncommitted Batch C3 + stack hotfix).
- App compile timestamp reported: `Oct 13 2026 16:00:39`.
- ELF SHA-256: `ee962efd62475a41fded8b6ba9a6b085b1f2fc2c953a77d4aa722a8b04764b5f` (Wokwi boot prefix `ee962efd6`).
- App BIN SHA-256: `afe036cf8282c7039fbdbf2cf308321e023be57bcdaeeff407fc0638e77f1d97`.
- Wokwi merged BIN SHA-256: `fa4efc7be9706fc233693ef709cdf5941920bea650253e4667fcbdfc978e2a80` (229360 bytes; 2MB image setting is simulator only).
- Archived UART: [`firmware-core-c3-wokwi-serial-20261013.txt`](../logs/firmware-core-c3-wokwi-serial-20261013.txt), SHA-256 `811ecff43b583a2c5a180ed0e417e733d799a8abc0e00b33a788b1d688d24965`.
- Build report: a matching `vessel_gateway_C3_esp32_build_*.log` was checked locally during closure; the report itself is not included in this commit.

## Observed results

- ESP-IDF Wokwi app booted, SHA matched the current build, and returned normally from `app_main()`.
- Ten development self-test suites: **201/201 PASS** (includes `CORE_RUNTIME_SIM_SELFTEST 32/32`).
- Bounded actual timer demonstration: `RUNTIME_TIMED_STEP 0` through `5` PASS and `CORE_RUNTIME_TIMED_DEMO: PASS (6/6)`.
- No panic, `***ERROR***`, stack overflow, or forced reboot is present in the archived latest-boot session.

## Failure and mitigation record

- Before the hotfix, an earlier Wokwi build identified by ELF prefix `6241938e8` repeatedly reset with `***ERROR*** A stack overflow in task main has been detected.` That failing build **must not be counted as PASS**.
- The C3 hotfix relocated six test/demo runtime workspaces from `main` task stack to static-duration storage. The new image `ee962efd6` completed self-tests and the six-step timed demonstration without the previous error.
- The evidence establishes a single finite demonstration only. It does not establish unlimited runtime stack headroom, thread safety, or durability across power failures.

## Engineering limitation / status

- Journal is a bounded 8-entry RAM-only model; no nonvolatile persistence or crash recovery.
- Synthetic SIMULATION inputs only. No physical sensor, GPIO alarm outputs, field calibration, vessel connection, remote API, or operational policy thresholds.
- Locked 38 requirement baseline remains unchanged; living traceability is structural, not verification. Formal `SIM-001..SIM-015` and `SUP-001..SUP-019` are still NOT_RUN and Phase 3 remains PARTIAL.
- Security screening is automated only, not a release or publication approval.
