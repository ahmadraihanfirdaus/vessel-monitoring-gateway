# Phase 9 B29 — External CAS Receipt Publication Barrier (host only)

B28 prepared a candidate revision but did not distinguish staged host state from a verified persisted CAS receipt. B29 splits these into `vg_b29_prepare` (private pending material, no committed runtime output) and `vg_b29_finalize` (publish only after externally supplied successful CAS receipt and separately verified revision).

- `NET-002`: the new state is not exposed as a published checkpoint on a stale/absent CAS receipt.
- `TEL-003`: generation and ACK must be bound to the confirmed persisted revision; pending ACK must be clear.
- `SYS-003`: guard rounds, source epochs, and witness consistency must be exact.
- `SEC-001`: source identity and independent source domains must match the externally confirmed receipt.
- `TST-001`: 31 cross-process fixture cases, 1 publish and 30 fail-closed denials; memory output unchanged on denial.
- `TST-002`: CI registration and exact scope preflight; 82 Laravel PHPUnit cases and historical host regression mandatory before auto-local-commit.

**Explicit trust boundary:** The receipt includes a caller-supplied `external_cas_confirmed` flag; code does NOT authenticate, persist, or verify actual storage CAS itself. A malicious caller can fabricate a receipt; an attacker who can roll back the external store remains in scope of future hardware design. This is C99 host policy, not durable storage proof. ESP32/NVS power-loss behavior, ship networks, bench and formal gate NOT_RUN. NO hardware flash, database reads/writes/migration or push.
