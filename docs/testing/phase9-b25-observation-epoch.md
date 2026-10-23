# Phase 9 Batch 25 — External Observation Epoch Guard (HOST ONLY)

## Scope and boundaries
- NET-002: forbid stale, repeated or skipped externally supplied observation epochs during checkpoint restore.
- TEL-003: preserve ACK high-water and clear pending ACK after restart through B24/B23 restore policy.
- SYS-003 / SEC-001: bind device tag and observation source domain to a trusted witness, and deny mismatched source or stale tickets.
- ALM-002: bounded journal/critical event content preserved via B18–B24 codec and restore chain.
- TST-001/TST-002: 18 independent-process C99 verification scenarios, deterministic evidence and CI.

## Threat model and limitations
- The external witness, its source domain, epoch, identity, and durability MUST be established and authenticated by the caller. This host policy cannot authenticate any of those values. It is unsafe to use an in-memory epoch after loss of power without independently trusted persistent state.
- `last_observation_epoch+1` must equal `verified_epoch`; equal/older values, gaps and UINT64 wrap are rejected.
- The ticket's *previous witness* must match the guard state. Existing B24 receipt verification runs before promotion; old witness leaves old ACK, new witness permits promotion.
- Output state, restored checkpoint and committed flag remain unchanged on rejection.
- No firmware hardware integration, no NVS durability, no power-loss atomicity, no signed receipts, no database/HTTP access, no production or formal closure.

## Test execution
`python3 -B scripts/test_phase9_b25_observation_epoch.py` compiles with C99 strict warnings and runs two processes (stage and verify). Test vectors: old, new, repeated observations, stale/skip/zero epochs, wrong domain/tag/witness, bad receipt, corrupt slots, reordered/future witness, overflow and zero identifiers. Full Windows batch runner requires B9–B17 PHPUnit and 49 prior suite regression PASS before exact-scope local commit.
