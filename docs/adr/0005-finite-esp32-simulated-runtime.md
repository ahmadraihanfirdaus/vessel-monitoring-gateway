# ADR-0005 — Finite Simulation-Only ESP32 Timer Driver

**Status:** PROPOSED, development-only. This does not establish an operational vessel monitor, source authenticity, or safety policy.

## Design decision

Batch C3 supplies a finite six-sample synthetic source to the C2 transactional single-channel flow. The samples are (1) VALID, (2) MISSING, (3) INVALID, (4) VALID, (5) STALE, (6) VALID. Valid samples carry arbitrary 42.0 test units; no measurement threshold is evaluated and the values must never be interpreted as propulsion/safety measurements. All samples explicitly identify the source as `SIMULATION`.

The pure C11 runtime stepper polls the existing scheduler against caller-provided monotonic milliseconds. The cursor advances only after a successful due-time processing operation. Failed or journal-full operations retain the cursor and C2 atomic rollback guarantees. Existing `bench_test` injected samples remain supported in C2, but this specific scripted runtime driver only emits `simulation` data. No automatic alarm acknowledgement is attempted: acknowledgement must remain explicit.

For actual ESP-IDF builds only, `app_main()` runs a **bounded, six-step** demo using `esp_timer_get_time()` and cooperative `vTaskDelay()` polling at approximately 20-ms intervals, with a 200-ms nominal sample period. It prints six per-step results and one final summary. It does not run forever, claim real-time deadlines, or use GPIO, physical instruments, NMEA, network, hardware alarm outputs, or persistent storage. Do not use this scaffold on physical vessel systems.

## Boundaries and remaining engineering gates

- Finite and single-channel, *not* a production continuous acquisition task or scheduler SLA.
- The event journal is still RAM-only (eight events), with no reboot recovery or guaranteed offline retention.
- Alarm reason/priority remain opaque simulation codes, not a defined marine hazard policy.
- No backend outage testing, sensor-age timeout, watchdog, physical calibration, nor source authentication.
- All formal SIM/SUP tests remain `NOT_RUN`; previous requirements status remains unchanged.
- Host C11 32-case runtime regression and ESP-IDF/Wokwi six-step timing are **separate evidence gates**. Host results must not be presented as Wokwi results.
