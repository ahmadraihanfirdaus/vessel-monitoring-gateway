# Batch 32 — Host checkpoint input separation

## Gap
B31 guarded output overlaps and readback independent of control sources, but did not reject aliasing among three immutable control inputs (`vg_b30_pending`, `vg_b29_cas_receipt`, `vg_b30_readback_receipt`). A caller can supply overlapping address ranges to distinct logical roles, violating the independence assumption before B30 checks exact bytes.

## Exact host-only change
`vg_b32_finalize_separated_inputs` checks every pair among four input regions (pending, CAS receipt, readback receipt, readback byte buffer) using B31 overflow-safe address ranges, **before dereferencing any of them**. Only fully non-overlapping inputs reach the full B31 → B30 → B29 gates. Output/immutable isolation and same-value readback still execute in those older gates. No heap, transport, MySQL/SQLite, Arduino/NVS or firmware flashing.

## Demonstration
C99 -std=c99 -Wall -Wextra -Werror -pedantic, two-process stage/verify; 24 fixed cases (1 valid, 23 denied). All denied cases preserve checkpoint candidate, both receipt instances, stored readback bytes and all result output fields. Six rejection cases specifically alias control inputs pairwise. Existing B31/B30 tests remain required.

## Formal boundary
Address separation does not certify independently acquired or authenticated receipts, does not prevent malicious pointers, and does not establish atomic external CAS, durable storage, ESP32 hardware memory protection, or production readiness. LOCKED requirements unchanged; total system PARTIAL_NOT_PRODUCTION_READY; hardware NOT_RUN.
