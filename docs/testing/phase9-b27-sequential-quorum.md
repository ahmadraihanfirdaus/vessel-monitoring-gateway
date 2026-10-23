# Phase 9 Batch 27 — Two-Round Quorum Sequence (HOST ONLY)

## Purpose and scope
NET-002 / TEL-003: a checkpoint must not advance by two generations when only
one of two sequential dual-source witness decisions is approved.
SYS-003 / ALM-002: the preserved offline journal and ACK cursor must remain at
the last fully witnessed generation on any denial; host-only simulation.
SEC-001: both vote domains, epochs and witnesses remain **caller-authenticated
external preconditions**, not cryptographic or durable properties of this code.
TST-001 / TST-002: deterministic C99 subprocess evidence, negative matrix,
full previous host/PHP regression and CI registration.

## Transactional boundary
The caller provides consecutive before/middle/after two-slot snapshots and two
readback tickets. Round 1 uses the old B26 quorum guard; round 2 consumes the
round-1 in-memory guard and must pass both independent source observations.
`vg_b27_confirm_sequence` rejects stale/mismatched witnesses, epoch replay,
ACK regression, malformed slot or receipt, disagreement and candidate corruption.
**All three caller-visible outputs are unchanged on ANY denial**, including a
valid first promotion followed by a denied second promotion. This is a
pure host policy for in-memory output, NOT an atomic filesystem transaction.
The intermediate candidate and external witness observations are caller inputs,
not independently proven by the fixture.

## Evidence and exclusions
30 independent-process verify cases (1 accepted, 29 denied); C99 strict compile
and prior B18–B26 regressions. No real trusted source, independent authentication,
separate durable anti-replay floor, ESP-IDF, power-loss hardware, NVS, production
or formal certification has been verified. MySQL is not accessed by these tests.
