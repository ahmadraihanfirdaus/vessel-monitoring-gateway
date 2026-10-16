# Phase 3 Closure Report — Firmware Core, development unit gate

**Report date:** 2026-10-16
**Reviewed baseline:** `develop@ec32315` (commit of Batch C4)
**Original audit:** `Vessel_Gateway_Phase3_Gate_ec32315_20261016_114615-return.zip`
**Audit bundle SHA-256:** `466eed7f6637e667b19a03c679be6fc2d435a4d4c6962671dc14fe8ba618ee9a`
**Decision scope:** Development-only **Phase 3 core-unit milestone**, not complete firmware, system, or production verification.
**Approval condition:** The local closeout script requires explicit human acknowledgement before writing the acceptance record and committing. No third-party, regulatory, safety, or formal SIM/SUP sign-off is implied.

## 1. Controlled exit criterion

The non-LOCKED repository roadmap states:

> Phase 3 | Firmware Core | Implement scheduling, data quality, diagnostics, event journal, and alarm state model. | Core unit tests completed with recorded results.

The audit accepts only this **specific** five-function core-unit exit criterion. Later-phase simulator drivers, safety policies, propulsion/navigation, telemetry, API, dashboard, CI and bench activities are not implicitly promoted to Phase 3 gates. The two LOCKED files are preserved without edits.

## 2. Traceable closure matrix

| Core-unit exit group | Implementation | Evidence at reviewed snapshot | Milestone assessment |
|---|---|---|---|
| Data quality | `core_types.h`, `core_quality.h`, `core_source_mode.h`, `core_measurement.h`, `core_range.h` | C4 Wokwi suites 7+5+16+21 = 49; regression 226/226 | PASS for development predicates |
| Alarm state model | `core_alarm.h` | C4 suite 30/30; prior B1 evidence | PASS for local lifecycle model |
| Scheduling | `core_scheduler.h` | C4 suite 16/16; ESP-IDF finite timed demonstration 6/6 | PASS for pure due-time and bounded demo |
| Diagnostics | `core_diagnostics.h` | C4 suite 19/19; C2 transactional flow and C4 runtime | PASS for simulated channel health |
| Event journal | `core_event_journal.h` | C4 suite 19/19; capacity-full/no-overwrite and rollback regression | PASS for **volatile eight-event development model only** |
| Integration / runtime guard (supporting evidence) | `core_flow.h`, `core_runtime_sim.h`, `core_runtime_guard.h`, `main.c` | C4 suite 36+32+25; timed demo 6/6 | PASS for finite **SIMULATION** path only |

Evidence files: `evidence/test-results/firmware-core-c4-wokwi-20261013.md` and `evidence/logs/firmware-core-c4-wokwi-serial-20261013.txt` (plus B1, C1–C3 historical records). The cumulative 226 cases represent one C4 test suite collection, not 226 requirement verifications. No operational alarm output is claimed.

## 3. Checkpoint and provenance review

- Operator-run read-only automated audit of `develop@ec32315`: **19/19 automated checks PASS**. It re-ran native C11 (226/226), checked living traceability (38/38 structurally mapped; 7 PARTIAL, 31 NOT_STARTED, 0 VERIFIED), static ESP32 build config and automated security scan (0 findings).
- The C4 code committed at `ec32315` has `firmware/src/main.c` SHA-256 `72ca86f78cfba3dbd614c42b1a5e509f670ef807acfabf5bbb37439778d3bc7f`, and `firmware/src/core_runtime_guard.h` SHA-256 `acb90d7827c218100ef4e0c2c11890d114033022a98002dc1a4046b48f2adc78`.
- Normalized committed UART SHA-256 `5fd1b84b3875a47332b6a75f24cf995ec1cb09b89bd5edb4117d1528dbab4ada`; it logs 226/226, 6/6, one successful return, and ELF prefix `c198d7937`.
- Original precommit dirty-build ELF SHA-256 `c198d79378986c50925d06f45919974a601baf88311a48d40395ea6c427eefc1` is in C4 evidence. It was built when Git reported `d49fa7f-dirty`; the subsequently committed C4 source files match the reported C4 source identities. **This corroborates source/evidence provenance but does not independently prove bit-for-bit reproducibility of the toolchain output.** A later clean-clone rebuild could strengthen assurance.
- Reported 3584-byte main-task stack with **1952-byte minimum remaining** before and after six runtime steps is bounded diagnostic evidence, not a production safety threshold. First uncorrected run showed 256 bytes and led to the C4 static-test-workspace hotfix.
- LOCKED hashes: requirements `a60167d9f2a1f852a091048447f6f4acf8d2cbfd6d11f04c2a6e2f6896f5b92b`; matrix `bc1fc7ce697fc6180cab760320de2a1bd814f9bc78731d4a22fdae838c303fe3`.

## 4. Explicit deferrals and boundaries

**Not covered by this development unit milestone:** continuous sensor acquisition; physical sensor inputs and calibration/accuracy; safety policy, approved alarm outputs or fail-safe actuation; nonvolatile event retention; memory load/stress or long-duration testing; production-sized RAM/flash budget; versioned telemetry, network/offline delivery, Laravel/MySQL, dashboard; engine and NMEA models; end-to-end testing; environmental/EMC checks; certified marine use.

Formal **SIM-001..015 NOT_RUN** and **SUP-001..019 NOT_RUN/PLANNED**, including the SUP-017 full traceability acceptance. No original requirement becomes `VERIFIED`. No hardware/vessel connection, public release, or publication authorization is granted.

## 5. Milestone disposition

**Core-unit gate:** `PASS — ELIGIBLE FOR PROJECT-OWNER LOCAL APPROVAL`. The user/operator must explicitly accept the evidence and scope at closeout. When the accompanying local acceptance record is written and committed, milestone status becomes **PHASE_3_CORE_UNIT_GATE_COMPLETE**.

**Overall firmware/system:** PARTIAL. **Formal SIM/SUP:** NOT_RUN. **Production ready:** NO. **Phase 4:** NOT_STARTED until this milestone is explicitly accepted; its drivers have their own independent exit tests and must not be represented as finished.

**Records:** Local approval evidence: `evidence/test-results/phase3-core-unit-acceptance-20261016.md` (written only after typed confirmation). This is an internal engineering checkpoint; it does not replace independent formal design review where required.
