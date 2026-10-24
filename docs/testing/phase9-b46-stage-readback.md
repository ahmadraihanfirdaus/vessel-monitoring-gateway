# B46 — Authenticated staged nonce-ledger readback admission (HOST ONLY)

## Objective

Avoid promoting a candidate nonce-ledger snapshot when a simulated inactive-slot
write/readback does not exactly match the staged bytes or the candidate breaks the
monotonic generation/nonce history contract. This is a **pure validation gate**
that makes **no actual storage writes**. It composes B44 HMAC, B45 two-slot
selection, and explicit memory region isolation; it does not replace secure storage.

## Preconditions and transition

- One or both current slots must contain a B44-authenticated snapshot passing
  trusted source ID and caller-supplied generation floor. B45 decides the active
  slot and denies authenticated split-brain equal-generation conflicts.
- Staged and readback buffers must be distinct, disjoint from slots, key, outputs,
  and exactly 192 bytes each. Stage must be HMAC authenticated and canonical.
- Stage generation == current generation + 1, with overflow denied.
- Stage ledger count == prior count + 1, and its prior nonce list is an exact
  prefix. A full eight-nonce ledger cannot accept another nonce.
- Every readback byte must match staged bytes. Re-running B45 selection with the
  candidate in the *inactive* slot must choose the candidate uniquely.
- No output is modified unless every check passes.

## Tests and limits

Python HMAC/struct oracle is independent of the C99 algorithm; a standalone
C99 executable validates cross-process fixture inputs. Cases cover valid inactive
slot admissions, torn/truncated/reordered/corrupt readbacks, wrong MAC/source,
wrong trust floor, stale/equal/overflow generations, replayed/altered nonce history,
and output/slot aliasing.

**Explicitly NOT verified:** actual atomic two-slot IO, fsync, media flush,
crash/power-loss durability, external generation-floor trust, multi-process
locking/CAS, secure hardware key storage, ESP32/NVS physical bench, production.
