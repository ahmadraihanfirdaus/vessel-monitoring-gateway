# Phase 9 B24 — Host-only external witness observation gate

Baseline B23 implements exact external-witness proposal after validated candidate readback. B24 explicitly separates **proposal**, **external observation**, and **restore selection**, without asserting external storage or network truth.

- `vg_b24_issue_ticket`: emits an in-memory ticket after `vg_b23_propose_after_readback` PASS, capturing old/new generation, confirmed ACK, bounded candidate size, slot, device tag and CRC. Ticket is NOT authentication or persistence evidence.
- `vg_b24_resolve_observation`: revalidates the full before/after slot and original candidate bytes. A **caller-trusted old witness** restores the old ACK; a **caller-trusted exact proposed witness** restores the new ACK; any wrong, stale, future, mismatched, torn or corrupt observation fails closed. Out parameters remain unchanged on refusal.
- Host fixture runs **two separate C99 processes**. Staging writes a same-ABI fixture only, a restart simulation. A second process exercises two accepted states plus 12 refusal conditions.

**UNVERIFIED:** true freshness/authenticity/rollback resistance of externally observed witness; atomic disk/NVS storage; process crash fsync barriers; ESP32 power-loss, real networking, DB and production certification. CRC32 cannot authenticate an attacker. No hardware/production claim. Existing LOCKED requirements and traceability baseline unchanged.

Evidence target: strict C99 `-Wall -Wextra -Werror -pedantic`, 14 scenario checks, B18–B23 host and historic regressions, isolated 82 Laravel PHPUnit cases, B17 HTTP reconciliation, exact 8 ADD + 1 CI MODIFY, no database writes, no push and local commit only ALL PASS.
