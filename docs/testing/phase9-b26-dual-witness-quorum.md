# Phase 9 Batch 26 — Two-Source Witness Agreement (HOST ONLY)

## Context and scope
NET-002/TEL-003: checkpoint promotion and ACK advancement require BOTH independently verified external witness observations to match exactly on generation and ACK. A single favorable source never authorizes promotion.
SEC-001/SYS-003: distinct source domains and per-source contiguous observation epochs are mandatory; mismatched, stale, missing, ambiguous or split-brain observations fail closed.
ALM-002: existing bounded checkpoint journal recovery remains delegated to the B18–B25 path.
TST-001/TST-002: cross-process C99 fixture, negative evidence, regression and retained CI policy.

## Explicit trust boundary
The two source domains are caller-supplied integers; they do NOT authenticate identities or prove actual source independence. The caller MUST independently authenticate and persist EACH source's domain, epochs and witness. Matching two attacker-controlled observations offers no security guarantee. No NVS, ESP-IDF, hardware, flash power-loss or production claim is made.

## Host policy
`vg_b26_seed` refuses duplicate or zero domains, invalid epochs and witness. `vg_b26_confirm` refuses split votes or any stale per-source epoch; it calls B25 verification for each source. The restored checkpoint and ACK high-water are output-atomic on failure. The old agreed witness retains old ACK; the exact new agreed witness promotes only after B24 readback verification. Replay of either epoch fails.

## Evidence
29 synthetic scenarios: 2 accept (old/new agreement), 22 verify-time reject and 5 seed-time reject; cross-process stage/verify, C99 strict compilation, no real I/O except temporary fixture file. Full Windows runner additionally enforces B9–B17 PHPUnit 82 cases, previous host suites, pinned Git tree and exact-scope local commit only after all PASS.
