# Firmware Development Evidence Index

**Basis:** Historical firmware-core evidence starts at `develop@cad6505` and B1–C4, followed by committed Phase 4–8 scoped development/software-simulation evidence through 2026-10-17. The original C4 cumulative core remains **226/226 PASS** plus **6/6** finite timed demonstration; later phases add their own provider, safety, engine, navigation, and telemetry-contract suites and must not be arithmetically added to that historical C4 count.

| Foundation suite | Historical 2026-10-10 tests | Evidence | Formal requirement verified? |
|---|---:|---|---|
| Core Quality | 7/7 PASS | `evidence/test-results/firmware-core-range-wokwi-20261010.md` | No |
| Source Mode | 5/5 PASS | `evidence/test-results/firmware-core-range-wokwi-20261010.md` | No |
| Core Measurement | 16/16 PASS | `evidence/test-results/firmware-core-range-wokwi-20261010.md` | No |
| Core Range | 21/21 PASS | `evidence/test-results/firmware-core-range-wokwi-20261010.md` | No |

The historical baseline **49/49 PASS** was one self-test run containing the first four suites. The latest C4 run includes those and later suites (**226/226 total**); **do not add counts across historical runs**. The retained firmware entrypoint is a development-only test runner; the separate `esp32dev_continuous` candidate now runs `esp32_continuous_main.h` with explicit external demo configuration. Both remain hardware-unverified.

**Locked traceability snapshot:** `requirements/traceability-matrix.csv` intentionally remains unchanged and has `NOT_IMPLEMENTED/NOT_RUN` placeholders for 38 requirement rows. No requirement is declared verified by this index.

**Remaining:** hostedSUP018, independent ESP32/RTOS/bench/hardware/NVS/powerloss/deployedTLS evidence, calibration and physical integration (not authorized). All15SIM and18SUP have scoped records; this does not approve the system.

## Additional evidence after the original foundation

- Alarm lifecycle: [Batch B1 Wokwi 79/79](../../evidence/test-results/firmware-core-alarm-wokwi-20261013.md); includes the original four suites and 30 alarm cases.
- Pure scheduler, diagnostics, bounded RAM journal: [Batch C1 Wokwi 133/133](../../evidence/test-results/firmware-core-c1-wokwi-20261013.md), with [full latest-boot UART](../../evidence/logs/firmware-core-c1-wokwi-serial-20261013.txt). Includes earlier suites and 54 C1 cases.
- Integrated simulated scheduler/diagnostics/alarm/journal flow: [Batch C2 Wokwi 169/169](../../evidence/test-results/firmware-core-c2-wokwi-20261013.md), with [operator-reported latest-boot UART](../../evidence/logs/firmware-core-c2-wokwi-serial-20261013.txt). Includes the prior 133 suites cases and 36 orchestrator cases; formal SIM/SUP NOT_RUN.

- Finite ESP-IDF runtime with synthetic source: [Batch C3 Wokwi 201/201 and timed demonstration 6/6](../../evidence/test-results/firmware-core-c3-wokwi-20261013.md), with [successful latest-boot UART](../../evidence/logs/firmware-core-c3-wokwi-serial-20261013.txt); earlier stack overflow build is excluded from passing evidence. Runtime is bounded, journal remains volatile, and formal SIM/SUP NOT_RUN.

Recorded counts are cumulative software self-tests on a single build, **not additive across historical runs**. The index and living traceability do not approve or complete formal SIM/SUP tests, hardware calibration, persistence, or operational sampling.

## Development evidence — Batch C4

- [Batch C4 Wokwi 226/226 self-tests, timed demo 6/6, and stack watermark](../../evidence/test-results/firmware-core-c4-wokwi-20261013.md), with [archived operator UART](../../evidence/logs/firmware-core-c4-wokwi-serial-20261013.txt) (LF-normalized for Git).
- The passing hotfix build showed 1952-byte main-task stack high-water mark (pre-hotfix 256 bytes); finite test only, no approved minimum for production.
- C4 remains historical core evidence. Later formal SIM-001..SIM-009 evidence is listed below; continuous operational monitoring, backend persistence, physical hardware and final system approval remain incomplete.
## Roadmap evidence after Phase 3

- Phase 4 provider development/simulator closure: `evidence/test-results/phase4-closure-summary-20261016.md`; D1–D7 provider self-tests PASS. Physical bench execution remains NOT_RUN.
- Phase 5 safety-policy formal software simulation: `evidence/test-results/phase5-e4-summary-20261016.md`; SIM-001..SIM-006 PASS.
- Phase 6 engine-model formal software simulation: `evidence/test-results/phase6-f2-summary-20261016.md`; SIM-007 PASS.
- Phase 7 navigation formal software simulation: `evidence/test-results/phase7-g2-summary-20261016.md`; SIM-008 and SIM-009 PASS.
- Phase 8 telemetry contract: `evidence/test-results/phase8-h1-summary-20261017.md` and `evidence/test-results/phase8-closure-summary-20261017.md`; versioned schema/fixtures/contract self-tests PASS at the scoped development gate. SUP-011, SUP-012, TEL-003 backend deduplication and SIM-014 remain NOT_RUN.
- Pre-Phase-9 R1 hardening: `evidence/test-results/pre-phase9-r1-summary-20261017.md`; firmware edge-case fixes and later-verifier boot isolation regression PASS.

Formal execution is recorded in `docs/testing/formal-scenario-status.csv`: all15SIM scoped PASS, canonical18SUP PASS/SUP018 PLANNED. Dedicated current host resilience review is linked below; historical C4 evidence alone closes none of these cases. No requirement VERIFIED, physical or production approval.

## Dedicated host provider/ACK evidence 2026-10-26

SUP004/005/007/008/009/010 have actual dedicated host execution and reviewed
case evidence: [summary](../../evidence/test-results/formal-provider-summary-20261026.md).
Native121assertions and303 independent comparisons cover required fields,
quality/provenance/absence/zero boundaries and labels. Reproduced navigation
clock rewind was fixed; focused/new/broad regression and both SDK targets PASS.
These six existing protocols permit host execution; no current Wokwi/physical
bench, NMEA conformity, diagnosis, safety certification or full requirement
VERIFIED is claimed. Other SIM/SUP and external gates retain their own status.

## Project entry and dedicated data/UI contracts (2026-10-26)

[Current data/UI evidence](../../evidence/test-results/data-ui-summary-20261026.md): native30frames/1158channels, PHP377 and actualTLS215 checks PASS. Dedicated SUP002/011/012/015 and SIM014/015 local cases admitted with explicit execution/review boundaries; no requirement VERIFIED. Firmware source unchanged and exactly matches both current committed SDK proofs. Welcome cleanup DEFERRED/removed0; no historical evidence deletion. Both handoffs updated automatically. Hardware, hostedCI and deployedTLS remain NOT_RUN.

## Dedicated fault/storage/schema/reference gates (2026-10-26)

[Current software gate evidence](../../evidence/test-results/fault-storage-summary-20261026.md) records actual single-channel4frame/44channel isolation,72generation bounded host-file retention/reopen/corruption, guarded6migration rollback/reapply with382PHP cases,215actualTLS checks and241regression commands PASS. SIM011/SUP013/SUP014/SUP017 have prescribed dedicated local evidence; derived formal32PASS/2PARTIAL/4NOT_RUN, no requirement VERIFIED. Three verification-integrity gaps are fixed and negative reproductions preserved. Firmware source unchanged and matches both committed SDK proofs. Physical NVS/ESP32/outage/timing, currentWokwi, hostedCI and deployedTLS remain NOT_RUN. Cleanup removal count0, protected files unchanged, NO PUSH.

## Dedicated resilience host evidence2026-10-27

[SIM010/012/013 actual case review](../../evidence/test-results/formal-resilience-case-review-20261027.md):
60047ms real private-TLS API outage,561shared C99 cycles,3actual503 attempts then
explicit reset /up200, temperature invalid then STALE until VALID30, original
ordered2raise/2clear facts. Independent current-source reviewer PASS. Separate
real PHP388/TLS248checks/Chrome155/regression248 local evidence; host mode never
writes DB, normal integration owns disposable fixtures. SDK source unchanged,
prior both actual SDK builds bound by hash, not rebuilt/hardware executed here.
All15SIM/18SUP scoped PASS; hostedSUP018 PLANNED,37mapped PASS/1NOT_RUN, no VERIFIED.
