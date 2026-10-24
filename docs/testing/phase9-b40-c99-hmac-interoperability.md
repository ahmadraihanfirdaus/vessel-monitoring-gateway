# Phase 9 B40 — Independent C99 HMAC-SHA256 host receipt verification

**Baseline:** B39 local commit `f4ddf2328f5cc4906edd36063beafa654023b8e0`.
**Scoped contexts:** SEC-001, SEC-002, NET-002, TEL-003, SYS-003, TST-001, TST-002.
**Requirements and hardware:** LOCKED. No database reads/writes/migrations, push, or flashing.

## Motivation

B37–B39 introduced independent HMAC-SHA256 receipt validation through Python,
but C99 verified structural fields only. A C99 structural PASS cannot authorize
an ACK; this batch adds a standalone, **test-only** C99 HMAC-SHA256 checker and
compares it against Python `hmac`/`hashlib` for the B39 128-byte receipt format.

The verifier checks the canonical B35 72-byte inner wire, B37 prelude, B38
active/retired key and epoch, B39 purpose and device-domain binding, and HMAC.
It derives a scoped 32-byte key from an ephemeral 32-byte master using the
same domain-separated KDF and authenticates the 96-byte prelude+inner wire.
MAC comparison examines all 32 bytes before branching. C99 selftests include
SHA-256 `abc` and two RFC 4231 HMAC test vectors; integration checks 46 cases
(three accept and 43 deny) from fresh Python ephemeral secrets.

Inputs are distinct non-overlapping memory regions, including master key.
A failed verification leaves the caller's output epoch unchanged. Key bytes
and transient digests are zeroed before return; temporary test files holding
random keys are removed when the test process exits normally. **This is a
host-only test/reference implementation, not a validated cryptographic
library, and should not be incorporated into the ESP32 production build.**

## Validation and boundaries

- C99 strict compile: `-std=c99 -Wall -Wextra -Werror -pedantic`.
- Three independent fixed SHA/HMAC vectors, with Python oracle checking B39
  envelope interoperability for both RESTORE and PUBLISH.
- Explicit rejection: MAC tamper, wrong key, retired key, stale epoch, incorrect
  purpose/device, malformed lengths and changed snapshot despite valid CRC.
- Structural precheck passes for at least eight unauthenticated invalid
  receipts: demonstrates why structural validation alone is insufficient.
- 49 legacy host suites, 16 recent B10–B17 source contracts, B18–B40 regressions,
  9 Laravel PHPUnit classes with 82 cases, bridge fixtures and lint are
  independently required by the fail-closed Windows runner.

**NOT VERIFIED:** production crypto review and side-channel assurance;
trusted master-key provisioning and secure erase across hardware resets;
ESP32 integration, secure persistent revocation/epoch, atomic CAS and power-loss
behavior, genuine vessel/hardware or formal certification. Total system remains
`PARTIAL_NOT_PRODUCTION_READY`.
