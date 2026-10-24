# Phase 9 B41 — Host-only HMAC rotation authority revision fence

**Baseline:** B40 local commit `594429ae7d4c8e5cda79f9b239314126ef771fb4`.
**Scope:** SEC-001, SEC-002, NET-002, TEL-003, SYS-003, TST-001, TST-002.

## Motivation and technical boundary

B40 verifies an HMAC under the supplied active master key and key-policy. It does
not independently verify that the externally supplied authority state remained
stable across an attempted verification. B41 adds a host-only reference wrapper
which requires two independent, caller-supplied authority observations to have
identical key policy, source identity, and nonzero revision above a supplied
minimum. It uses B40's C99 verifier to authenticate the 128-byte receipt and
only writes its output epoch after every check succeeds.

A strict C99 process exercises 52 cases: 3 accept (pre-cutover, post-cutover,
publish) and 49 deny. Rejection includes retired key, wrong MAC, source mismatch,
old/new revision disagreement, wrong device and purpose, overlapping memory,
malformed envelope, or monotonicity floor violation. Random 32-byte test keys
are generated in temporary directories; no secrets are committed or added to
persistent evidence. The wrapper is deterministic policy logic, not a trusted
revision source, lock, atomic compare-and-swap, or actual concurrent proof.

Requirements, external hardware and DB behavior are LOCKED. No DB access,
HTTP request, migration, push, or ESP32 flash is intended.

## Scope limits

The caller supplies both observations as ordinary in-memory structs, so
identical malicious/stale observations are NOT distinguishable from trusted
ones. On-device key provisioning, hardware secure erase, true atomic CAS,
persistent anti-rollback, inter-thread concurrency, marine use, and formal
certification remain **NOT_VERIFIED**. System status remains
`PARTIAL_NOT_PRODUCTION_READY`.
