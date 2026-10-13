# Batch C4 — Wokwi finite runtime guard evidence (2026-10-13)

**Category:** Development self-tests only. This records operator-provided Wokwi ESP32 UART and an independently checked build ELF identity; not formal SIM/SUP, bench/physical test, safety approval or production readiness.

## Source, artifacts and provenance

- Source build identity: `develop@d49fa7f-dirty` (Batch C4 source and test-only static-allocation hotfix were uncommitted when built).
- Framework: ESP-IDF 6.1.0; Wokwi ESP32 simulator.
- ELF SHA-256: `c198d79378986c50925d06f45919974a601baf88311a48d40395ea6c427eefc1` (UART prefix `c198d7937`).
- Application BIN SHA-256: `f4ca8f8ba053c9d94fe6a1686d1669caf11b68852673570757c539cbc8b8a5e0`.
- Wokwi merged BIN SHA-256: `1b4bf3fa2da44daf48d547e8b635afaad3a89692ed9701ce7df2f32ece2e041d` (232320 bytes; simulator 2MB image setting, not physical flash validation).
- Operator UART evidence: [`firmware-core-c4-wokwi-serial-20261013.txt`](../logs/firmware-core-c4-wokwi-serial-20261013.txt), SHA-256 **of LF-normalized repository file**: `5fd1b84b3875a47332b6a75f24cf995ec1cb09b89bd5edb4117d1528dbab4ada`.
- Original operator-pasted UART from ChatGPT attachment had CRLF endings; original SHA-256 `97b73604aa5a6e2982ed0ad175d131c424df7c684222f51de0e5dbe52ad7a253`. Text content was preserved with CRLF→LF normalization required by repository `.gitattributes`; one trailing space in a raw UART line remains part of the recorded data. The unmodified CRLF original remains in the downloaded closure ZIP.
- Build report checked locally: `vessel_gateway_C4_esp32_build_20261013_185004.log`. It was not committed and is not attached to this evidence.

## Observed target result

- 11 development self-test suites (quality 7, source mode 5, measurement 16, range 21, alarm 30, scheduler 16, diagnostics 19, journal 19, flow 36, runtime simulation 32, runtime guard 25): **226/226 PASS** in Wokwi.
- Real ESP-IDF timed synthetic demonstration: steps 0 through 5 **PASS**, summary `CORE_RUNTIME_TIMED_DEMO: PASS (6/6)`.
- One observed boot, normal `main_task: Returned from app_main()`; no reported panic, `***ERROR***`, or reboot in that session.
- Main-task stack allocation: 3584 bytes as reported by `CONFIG_ESP_MAIN_TASK_STACK_SIZE` for this development build. FreeRTOS minimum remaining stack watermark (ESP-IDF bytes) **1952 before and 1952 after timed demo**. Approximate maximum observed occupancy from that high-water mark: 1632 bytes.

## Failure investigation and corrective action

- First C4 Wokwi image `d9f30843e` passed 226/226 and six timed steps but showed **only 256 bytes** minimum remaining main-task stack.
- Four large flow workspaces allocated on the test function stack were changed to static-duration storage and explicitly reset before the tests. Corrected ELF `c198d7937` demonstrated a larger 1952-byte minimum remaining stack and normal completion.
- This is evidence of a bounded test-only stack improvement, **not a general production stack-usage threshold**, an indefinite runtime load test, or permission for real-world vessel operation. Changing allocations increases static RAM use; target capacity and fault coverage must be revisited before production.

## Open verification / deployment blockers

- Firmware supports synthetic/bench-oriented development predicates; no continuous operational sensor acquisition, physical sensor calibration/accuracy or approved vessel I/O.
- Event journal is an 8-entry volatile RAM model; no NVS/flash durable event log, reboot recovery, or full backlog retention policy.
- No backend/dashboard, authenticated telemetry, offline resilience validation, NMEA/engine simulators, approved safety policies or environment/long-duration testing.
- Requirements traceability is structurally complete at 38/38 but **formal SIM-001..SIM-015 and SUP-001..SUP-019 are NOT_RUN**. Phase 3 remains PARTIAL and FINAL PRODUCTION READY is NOT_APPROVED.
- Security audit is an automated screen only; not a confidentiality or safety certification.
