# Phase 9 B43 — Bounded host nonce replay ledger (development-only)

B42's nonce-bound HMAC can be replayed when a challenge is reused. B43 adds
`vg_b43_verify_once`, a host-only eight-entry fixed-capacity in-memory ledger
which fails closed on previously consumed nonces and ledger exhaustion. It
refuses malformed ledger states, duplicate entries, output/input aliasing and
invalid HMAC; unsuccessful operations leave both ledger and output unchanged.

## Scope and test evidence

- `VG_B43_NONCE_CAPACITY=8`, initializes with `vg_b43_ledger_init`.
- Only a valid B42 HMAC with stable B41 revision may consume one nonce.
- No nonce is evicted when full; all subsequently presented receipts are denied.
- 41 cross-process C99 cases using an independent Python `hmac` oracle, including
  same-process replay, bad MAC, mutation, tampering, buffer overlap, and saturation.
- All B18–B42 host tests and older CI suites remain required before any local commit.
- No database access, no key hardcoding, no firmware hardware changes, no push.

## Formal limitations (OPEN)

No trusted nonce issuer, durable ledger, atomic compare-and-insert, concurrent
access serialization, restart continuity, process isolation, ESP32/NVS, or
hardware evidence is implemented. `vg_b43_ledger_init` is not safe to call to
re-enable a previously accepted challenge. Neither this header nor its tests
may authorize a production ACK or checkpoint release.

System remains `PARTIAL_NOT_PRODUCTION_READY`.
