# ADR-0010 - Authenticated event receipt and durable outbox retirement

Status: implemented; mandatory local functional/build/regression/working-security/manual review PASS. Final exact staged-byte gate required before commit.
No receipt acceptance/deletion is authorized by this document alone. Baseline local develop `bb4f462db3d0692a7c6ae9a8f96c704b3aea43f5`.
Requirements/source/formal boundaries remain unchanged.

Recovered events now reach the actual API, but queue/HTTP success cannot free
the bounded journal. Complete an actual authenticated confirmation path and
durable retirement, preserving local observations and alarm ACK-not-CLEAR.

## Seven related scopes in dependency order

1. Opt-in post-commit backend event receipt, preserving ordinary JSON responses.
   Bind authenticated device and the exact original body bytes to the accepted
   HTTP result. Never sign an uncommitted caller-owned outer transaction.
2. Shared strict bounded receipt admission with actual standard SHA256/HMAC
   providers: PHP runtime and ESP-IDF PSA crypto. Independent Python/native
   reference interoperability is test evidence, not a replacement SDK verifier.
3. Versioned durable current-boot confirmed floor and exact event retirement
   transaction, backwards-readable VGS1/VGS2. Keep ordinary publication's
   no-deletion guard intact; separately authorize only the confirmed target.
4. Bounded storage receipt jobs and real verification using the immutable external
   device profile; no credential is written into offline snapshots. Update
   admission/prefix handling only after committed/read-back confirmation.
5. Continuous single-inflight request context and confirmed RAM-prefix release,
   preserving monotonic IDs/times, immutable recovered facts, bounded queues,
   local progression, explicit failures and separate operator/delivery ACK.
6. Actual C99/PHP/MariaDB/TLS signed-receipt/reboot/retirement integration plus
   forged/wrong-key/body/status/context/boundary/partial-write/uncertain-IO faults.
7. Both SDK targets/CI/resource/security/regression, living traceability,
   read-only cleanup, exact evidence and both automatically updated handoffs.

## Compatibility and security boundary

An explicit request header opts an authenticated event into a small fixed receipt
representation. Requests without that header retain their existing response
shape. Invalid opt-in and outer-transaction contexts must fail closed before
issuing any receipt. Only committed new or exact identical-duplicate events may
receive a confirmation. Conflicting/invalid/unauthenticated requests never do.

The receipt binds the SHA256 of the complete raw request and its successful
HTTP status, using domain-separated HMAC-SHA256 with the original authenticated
bearer as the ephemeral signing input. Token digests stored in the database are
not signing keys. No secret is echoed, persisted in the journal, copied into
evidence or placed in argv. TLS chain/hostname/date verification remains required.
Exact implemented wire/crypto/owner policy is documented in
`docs/testing/event-receipt-retirement-plan.md`; actual gates and source hashes
are recorded in `evidence/test-results/event-receipt-summary-20261026.md`.

Durable confirmation may retire only an exact immutable event identity/body.
For current-boot facts, enforce the oldest outstanding prefix before advancing
a monotonic confirmed floor, preventing cumulative queued jobs from resurrecting
already retired facts. Ordinary writes cannot invent/advance a floor. Old-boot
retirement must preserve every other retained fact, including unsupported types.
RAM release follows durable worker confirmation, never an HTTP/queue flag.

No physical control, alarm-condition clear, manual DDL, main database, new
production key store, insecure TLS fallback or partition-limit relaxation.
New persistence bytes/allocations need explicit bounds and independent byte
oracles. Full native/SDK/local network PASS cannot establish physical NVS
power-loss/rollback resistance, heap/stack/timing, trusted clock or production
security. Formal SIM/SUP and hardware/hostedCI/deployed TLS remain NOT_RUN.

Do not commit this batch until all mandatory scoped tests, actual integration,
security/scope/diff and exact staged-byte gates PASS. Keep failed evidence and
document any independently testable work when a dependent scope is blocked.
