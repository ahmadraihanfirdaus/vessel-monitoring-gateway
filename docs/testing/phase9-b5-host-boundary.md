# Phase 9 Batch 5 — Host Contracts (development-only)

Batch 5 contexts: API-001, TEL-003, NET-002, SEC-002 and TST-001. Scope: JSON duplicate-key refusal including escaped keys; in-memory bounded identity deduplication with conflicting replay refusal; offline event replay acknowledgement requiring **injected** verification claim; injected authentication and TLS gate; cross-context host tests and trace evidence.

- The PHP support classes are **NOT wired into routes, middleware, requests, persistence, or MySQL**. Phase9B4IngestContract is reused as an existing synthetic schema check.
- No true HTTPS handshake, device authentication, authorization decisions, production secret or network transport is verified; boolean fixture claims are untrusted outside this host-only test.
- Dedup state is bounded in-process demo memory; no inter-process atomicity, durable MySQL unique key, multi-device concurrency or SIM-014 formal verification.
- C99 replay cursor uses volatile host journal and fake acknowledgements. No flash/NVS durability, real server response, timeout policy or approved production limits.
- `firmware/src/main.c`, locked requirements and all prior B1–B4 sources remain byte-identical except the CI workflow allowlisted modification.
- Tests run with local GCC and PHP CLI; no local MySQL access, ESP32 build, Wi-Fi, real sensors or physical actuators.
- TST-001 is scoped mapping only; formal test evidence and SUP017 remain open. Production readiness **NOT CLAIMED**.
- On success runner may stage and commit only this batch's exact allowlist to `develop`, then verify parent/child blobs and tracked cleanliness. **Never pushes.** On test failure, no stage/commit occurs; partial worktree is left for controlled recovery.
