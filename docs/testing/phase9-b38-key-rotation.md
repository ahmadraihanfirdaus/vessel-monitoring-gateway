# Phase 9 B38 — Host signing-key cutover policy (scope-limited)

Previous B37 covered HMAC-SHA256 for one receipt under one ephemeral signing key.
This batch adds an independent cutover policy for two ephemeral test keys:
pre-cutover key ID 101 and post-cutover key ID 202. After cutover, the old
key is retired and MUST NOT be attempted as a fallback. The simulated external
active ID, activation epoch, and exclusive epoch floor are verified before
HMAC authorization. CRC-rebuilt or MAC-tampered receipts cannot grant an ACK.

C99 precheck provides untrusted parsing/policy only. Its PASS_NO_AUTH result
**never** authorizes checkpoint publication; Python independently checks
HMAC-SHA256 with constant-time `compare_digest`. All secrets are created in
the test process, not stored as source or evidence, and leave with the
TemporaryDirectory. The fixtures exercise 47 cases (2 accept, 45 reject),
including old key replay after cutover, wrong signer/secret, epoch rewind,
incorrect identity, corrupt body, and structurally valid yet MAC-invalid bytes.

Traceability: SEC-001, SEC-002, NET-002, TEL-003, SYS-003, TST-001, TST-002.
These results do NOT demonstrate trustworthy provisioning, cryptographic
key erasure, persistent revocation storage, secure element, thread safety,
ESP32/NVS, power-loss survival or production readiness.
No database, networking, actuator or hardware access.
