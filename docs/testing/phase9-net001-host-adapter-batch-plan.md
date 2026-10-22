# Phase 9 NET-001 — Host Adapter Batch Plan (External Draft)

**Status:** Content draft generated **outside** `vessel-monitoring-gateway-public-cleanroom`.
Nothing in the Git repository has been added, modified, staged, committed, or pushed.
This is NOT a production network transport, NOT a formal NET-001 PASS and NOT approval to apply.

## Exactly three candidate additions

1. `firmware/src/network_transport_host_adapter.h` — portable C99 header-only nonblocking state machine. The caller injects a `net001_host_driver` (`begin`, `observe`, `cancel`) and monotonic `now_ms` ticks.
2. `scripts/test_phase9_net001_host_adapter.py` — proposed host test SOURCE; **not executed** in this gate. Uses a fake driver and fixture-only timing values; no network requests.
3. `docs/testing/phase9-net001-host-adapter-batch-plan.md` — this scope and evidence plan.

## State and safety boundaries

- States: `IDLE`, `CONNECTING`, `READY`, `BACKOFF`.
- One bounded `net001_host_step()` invocation performs no sleep or blocking retry loop. External driver functions are **required** to be nonblocking; this draft cannot prove that a future real driver respects that obligation.
- Connection attempt timeout, reconnect backoff, and maximum attempts are **injected policy values**; numeric production values remain **TBD**, with no defaults embedded in the header.
- Timeout, error, loss of link, bounded attempts and tick wrap have dedicated **planned** fake-driver tests. Tests are **NOT_RUN** until separately authorized.
- After exhaustion, the adapter stays idle until an explicit reset. It does not touch safety, sampling, alarm or diagnostic engine code.
- No ESP Wi-Fi, HTTP, HTTPS, TLS, endpoints, certificates, credentials, live transport, `main.c` or CMake integration.
- No telemetry schema changes, database access, requirements or traceability changes, or manual DB edits.

## Required future independent gates

1. Review all three new file SHA-256 hashes against `PAYLOAD_SHA256.csv` and `MANIFEST.sha256` (generated externally).
2. Review exact three-file add-only scope and the ten byte-pinned source anchors against the live `develop` HEAD.
3. Obtain **explicit user approval** for any repository apply. Do not treat this draft as that approval.
4. Only after separately authorized execution, run focused host tests and collect evidence. Runtime integration and formal SIM/NET gates remain separate.

## Open statuses

NET-001 `NOT_STARTED`; NET-002, SYS-003 and SEC-002 remain open. SIM-010/012/013 `NOT_RUN`. TST-001 formal `NOT_RUN`; SUP017 `PLANNED`. Five implementation blockers and six evidence gaps remain open. Total system `PARTIAL_NOT_PRODUCTION_READY`.
