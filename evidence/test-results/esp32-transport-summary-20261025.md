# ESP32 transport continuation, 2026-10-25

Baseline: local `develop` HEAD `bd34639940fff98461cf0e12cbf7e2e76c6664ce`.
This follows the committed connected dashboard; the old B46 reference remains
historical. No repeat of the full baseline audit, no remote interaction, no
LOCKED requirement change, no primary database access and no hardware upload.

## Seven related scopes

1. External bounded read-only NVS network profile and failure-atomic admission.
2. Actual ESP-IDF Wi-Fi ownership, event handling and reconnect driver binding.
3. Dedicated asynchronous HTTPS worker, zero-wait foreground queues, bounded
   retries/deadlines/replies and observable halt/manual reset behavior.
4. TLS chain/hostname/date verification, fail-closed build/start configuration,
   credential lifetime reduction and no secret-bearing application logs.
5. Actual six-step core measurement to telemetry v1 bytes, RAM latest retention,
   real Laravel/MariaDB ingestion and grant-scoped browser rendering; colon ID fix.
6. SDK resource budget, reset static test scratch, reproducible boot reentry,
   source-stability proof and offline simulator-image assembly.
7. Exact PHP patch CI configuration, host/adversarial/integrated regression,
   security review, living traceability and read-only cleanup inventory.

## Executed gate matrix

| Gate | Actual result | Evidence file in this directory |
|---|---|---|
| Approved Laravel/PHPUnit/DB preflight | PASS: PHP 8.2.35, MariaDB 10.4.32, approved loopback catalog/account, override audit | `esp32-transport-backend-run1-20261025.txt` |
| Full real backend suite | PASS: 326 tests, zero failures/skips; actual core/C99 packets, database and granted Blade rendering | same backend log |
| C99 wire prerequisites and receipt crosscheck | PASS: original 2/4 packets plus 6 real core packets; HTTP receipt reconciliation | same backend log; runtime-wire log |
| Database final read-only postcheck | PASS: exact ten tables/five migrations, zero application rows | `esp32-transport-db-postcheck-20261025.txt` |
| Port pure C99/security/source admission | PASS: five methods, including actual strict C99 binaries and negative/boundary assertions | final-local and final-regression logs |
| Build evidence adversarial checks | PASS: three methods; reject changing source, evidence overwrite and each weakened TLS option | same final logs |
| Integration-runner isolation/order checks | PASS: 21 methods; third fixture must succeed before migrations | final-local log |
| Native core and boot reentry | PASS: 226/226 core cases per execution; two entries in one process, no emitted phase failure markers | final-regression log; boot-reentry log |
| Source/CI/shared-helper regressions | PASS across original 53 scoped commands and added NET/no-control/build checks after correction described below | scoped-gates and final-regression logs |
| Scanner adversarial regression | PASS: 23 methods; SDK defaults retain all secret/binary checks | final-regression log |
| Current content and pinned framework security review | PASS: zero findings/privacy warnings; exact renewed CI non-secret line pins | final-regression log; final-security log |
| Changed PHP syntax | PASS: explicit PHP 8.2.35 for route and new integration test | final-regression log |
| Final actual SDK build/partition/source stability | PASS: app 1,034,608 bytes, limit 1,048,576; 66,428 bytes static RAM; largest own compiler stack frame 1,616 bytes | `esp32-transport-sdk-build-run8-20261025.txt` |
| Offline simulator merge | PASS: actual bootloader/partition/app bytes, app slice matched, NVS blank; SDK-configured 2 MiB layout only | same run8 log |
| Cleanup inspection | Metadata only, six categories retained; no deletion | cleanup-inventory CSV |
| Exact manifest, protected bytes, diff/index review | Required PASS before local commit; final index scanner repeated after exact staging | files CSV and integrity log |
| Physical ESP32, Wi-Fi/TLS handshake, trusted clock, NVS confidentiality/power loss, stack/heap watermarks, current Wokwi image | NOT_RUN | No promotion from compilation/host results |
| Hosted CI, direct MySQL 8, deployed TLS, remaining formal SIM/SUP | NOT_RUN | Existing formal registries unchanged |

The test file APP_KEY is empty; direct read-only postcheck reports it as absent.
The actual full test run used a fresh cipher-compatible process-only key, and
reports only its validity/source. No APP_KEY/password was printed or copied.
No migration changed in this slice; existing-schema mode was used. The preceding
dashboard migration roundtrip remains separate historical evidence.

Final merged image SHA-256:
`312195cf75cfbd28615edfe7560fd4d01e535f37b853dd9b550379d7abae4bcb`.
Final source-stability digest:
`b7559931fb4e4f01b4c0dde46ef801724d01f5d1ab77c33ddb6f234668eacc3c`.
Ignored build binaries/generated SDK configuration are not commit candidates.

## Failures retained and corrected

- SDK run1 hit the sandbox's external PlatformIO cache lock. The approved narrow
  local build command was then used; no sandbox restriction was bypassed.
- Runs2/3 exceeded the existing 1 MiB partition. Application/networking code
  optimization brought the image within the same budget. Assertions and full
  certificate roots remained enabled; flash/partition size was not enlarged.
- Moving large test-only objects out of the 3,584-byte main stack exposed static
  fixture state on the second boot entry. The reset defect was fixed. The first
  diagnostic also lacked the compiler DLL path; both failures remain recorded.
  Duplicate resets found in diff review were removed before the final run8 build.
- SDK default certificate-date checking was disabled. It is now enabled through
  tracked defaults and the local generated configuration. Build/start guards
  prevent insecure fallback. A trustworthy clock is required, not fabricated.
- Initial scoped P1 security gate rejected the new SDK defaults as unsupported
  format. The exact filename now passes through existing UTF-8/size/secret/privacy
  screening, with adversarial rejection tests. The P1 rerun passes. The earlier
  failure remains in the scoped-gates log; no commit occurred while it failed.
- Runs4–6 were intermediate images, before final date validation and/or final
  fixture edits. Only run8 certifies the final firmware source in this batch.

The first staged diff check rejected trailing spaces emitted by PlatformIO in
package-list lines. Only this batch was unstaged and no commit occurred.
Whitespace-only normalization retains all diagnostic text; before/after hashes
are recorded in the integrity log.

## Remaining boundaries

HTTP completion is not application ACK and never deletes pending state/journal.
Latest frame and critical journal remain RAM-only. NET-002 durable ESP32 storage,
continuous all-domain sampling, alarm metadata composition, trusted clock and
physical confidential credential provisioning remain substantive work. The
candidate has no flash encryption enabled and no provisioned secret in its
blank-NVS simulator image. Server Retry-After interpretation and hard DNS-call
latency guarantees are not implemented. The finite simulation is not an
operational monitoring task or a demonstration of physical I/O.

SIM-001..009 retain their existing formal PASS records; SIM-010..015 remain
NOT_RUN. Five SUP records remain PASS and fourteen remain PLANNED. Overall system
status remains PARTIAL, final approval NOT_APPROVED. See
`docs/testing/esp32-transport-integration.md` and the exact manifest for scope.
