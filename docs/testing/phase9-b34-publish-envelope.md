# Phase 9 B34 — host publication envelope integration

B18–B33 separated checkpoint persistence, two-slot recovery, quorum witness,
external revision probes, byte-exact readback, and non-aliased outputs. B34 adds
an **integration adapter** that gathers four B33 outputs into one bounded,
versioned publication envelope and cross-checks the materialized generation,
confirmed ACK, witness and revision before exposing it to sequential consumers.

The adapter rejects overlapping target/source buffers before dereferencing,
constructs the entire envelope privately, never writes caller output on rejection,
marks the envelope valid only after B33's two independent revision reads pass,
and records CRC32 as **noncryptographic corruption detection**. 35 deterministic
cross-process C99 tests (1 accept, 34 reject), a source contract, negative checks,
CI registration and full B18–B34 regression guard.

**Scope limit:** This is **not** an atomic write for concurrent tasks, not a
trusted CAS/witness provider, not authenticated data, not durable flash/NVS
storage, and not ESP32 firmware integration. A live-system publisher still needs
serialization, atomic visibility, evidence of NVS power-loss safety and bench
verification. Do not claim production or formal gate closure.
