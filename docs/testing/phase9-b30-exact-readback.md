# Phase 9 B30 — Exact checkpoint image readback binding (HOST ONLY)

B29 verified a CAS receipt using generation/ACK and quorum. Two distinct payloads can share the same generation and ACK but contain different journal or telemetry bytes. B30 additionally binds publication to the **exact checkpoint slot image**.

`vg_b30_prepare_exact` calls B29 prepare, selects the unique canonical checkpoint slot, verifies the decoded store/ACK can reproduce exactly those bounded bytes and keeps them private. `vg_b30_finalize_exact` accepts an externally trusted readback receipt and independently verified revision, confirms device, slot index, byte length, CRC32 integrity metadata, **byte-for-byte readback**, and a fresh canonical re-encode before calling B29 finalize on temporary outputs. No output is published on denial.

- NET-002: require byte-identical readback of selected candidate slot.
- TEL-003: require journal/telemetry content parity, not only generation/ACK.
- SYS-003: pending state is not eligible if its store changed between prepare/finalize.
- SEC-001: reject stale revision, wrong receipt identity, wrong slot and missing external verification; CRC32 is not an authenticator. Two denials use different **validly re-encoded** checkpoints with unchanged generation/ACK but altered telemetry or journal data.
- TST-001: 42 separate-process C99 fixture cases (1 valid, 41 denials), failure outputs unchanged.
- TST-002: CI registration and exact-scope host regression with Windows Laravel gate.

**Trust boundary:** External CAS and readback flags are supplied by the caller, not issued or authenticated here. A malicious adapter may fabricate both receipts and images. This is NOT cryptographic authentication, durable external CAS, filesystem flush, ESP32 NVS integration, vessel hardware, or formal production readiness. No DB reads/writes/migrations or pushes are intended.
