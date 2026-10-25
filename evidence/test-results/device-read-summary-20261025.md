# Device event and telemetry read integration, 2026-10-25

Baseline: local `develop`, HEAD `b999492c7f12d4e19cc6270983e4390122455e81`.
This is newer than ZIP reference B46 `231cc2b2022223b47790347a5fecf71eb0ee2c44`.
Tracked worktree/index were initially clean. The three preexisting untracked
paths (AGENTS.md and the two protected firmware files) are excluded from scope.
The earlier one-time baseline and 36-finding security triage remain recorded;
this batch does not repeat their implementation or reinterpret historical PASS.

## Six related scopes

1. Real authenticated, own-device event history from existing persisted rows.
2. Exact event-type/source filters, rejecting unsupported device selectors.
3. Deterministic bounded receipt-order cursor pagination, reusing strict cursor
   validation already present; no duplicate cursor implementation.
4. Decimal-string integer read contract and faithful ACK/clear/source facts.
5. Telemetry page channel hydration reduced from N queries to one (zero for an
   empty page), preserving null/zero/quality and device/sample boundaries.
6. Actual C99 JSON -> Laravel kernel/auth/validation -> MariaDB -> event reads,
   plus security, boundary, dependency-failure and integration regression.

These close a missing data-access prerequisite for Phase 10. The dashboard
itself still has eight placeholders; user/device authorization and configured
freshness policy remain open. No control endpoint, schema change, locked
requirement change, or formal verification promotion is included.

## Actual execution matrix

| Gate | Outcome | Evidence |
|---|---|---|
| Effective PHP/Laravel/PHPUnit/DB admission | PASS: PHP 8.2.35 explicit executable; testing mode; approved loopback target/account; MariaDB 10.4.32; overrides audited | `device-read-integration-final-20261025.txt` |
| Test APP_KEY | PASS for runner: ephemeral cipher-compatible process key, no value emitted; file-only key remains unconfigured | same; `device-read-db-postcheck-20261025.txt` |
| Existing exact schema migration rollback/apply/reapply | PASS: Laravel migrations only, admitted empty test catalog | integration-final log |
| First integrated run | PASS: 246 cases, zero failed/skipped, before final extra tests | `device-read-integration-run1-20261025.txt` |
| Final complete Laravel/MySQL regression | PASS: 251 cases, zero failed/skipped (36 more than baseline 215) | integration-final log |
| Actual C99 fixture generation | PASS: 2 telemetry and 4 event wire fixtures compiled from existing C99 code | integration-final log |
| HTTP receipt C99 crosscheck | PASS | integration-final log |
| Post-suite database inventory | PASS: five exact tables, four migration records, zero application rows | `device-read-db-postcheck-20261025.txt` |
| P3 source contract | PASS: all 31 checks | `device-read-p3-regression-20261025.txt` |
| Scanner adversarial tests | PASS: 20 methods | `device-read-scanner-regression-20261025.txt` |
| Isolation/runner regression | PASS: 20 methods | `device-read-isolation-regression-20261025.txt` |
| Content security initial scan | PASS: zero findings/warnings; existing hash-pinned reviews unchanged | `device-read-security-run1-20261025.txt` |
| PHP lint, cursor/CI/traceability regressions | PASS: all 16 commands, including eight PHP files | `device-read-scoped-gates-20261025.txt` |
| First supplemental security/framework gate | FAIL: seven UTF-16 logs rejected as binary; corrected losslessly to UTF-8 and rerun, no scanner exception | `device-read-scoped-gates-run1-20261025.txt`; `device-read-evidence-encoding-20261025.txt` |
| First staged diff review | FAIL: one blank-line space in each of two evidence logs; staging restored, no commit. Whitespace corrected, hashes recorded; repeat staged review required | `device-read-stage-review-run1-20261025.txt`; encoding record |
| Final content scan and exact scope/integrity review | PASS required before exact staging; index is scanned again before commit | `device-read-security-final-20261025.txt`; `device-read-integrity-20261025.txt` |
| Cleanup candidate audit | READ-ONLY, retained everything; metadata only | `device-read-cleanup-inventory-20261025.csv` |
| ESP32 bench/NVS/power-loss, hosted CI, direct MySQL 8, deployed TLS | NOT_RUN; external verification remains open | No claim from these local results |
| SIM-010..015 and remaining SUP protocols | NOT_RUN in this batch; existing formal registry unchanged | No formal promotion |

PowerShell renders unittest progress written to stderr as NativeCommandError
text in two logs. Both processes exited 0 and report 20 tests / OK; no test
failure was hidden. The first successful suite was followed by one full rerun
after adding boundary and wire readback tests. The supplemental security gate
then rejected the seven new logs written as UTF-16 by PowerShell Tee-Object.
Only their encoding was converted to UTF-8, with exact text equality and
before/after hashes recorded. The failed review is retained and the security
gate is rerun without adding exemptions.
The first staged whitespace check then rejected one blank-line space per
unittest log. The commit script restored its exact staging set and made no
commit. Only those two spaces were removed, with hashes recorded; all test and
diagnostic text remains. The staged diff gate must pass on retry.

## Reproduction

Use `C:/tools/php-8.2.35/php.exe` explicitly and process-only `VG_PHP_CLI`.
The local GCC child search path includes `C:/msys64/ucrt64/bin`; global PATH and
XAMPP are unchanged. The guarded command was:

```text
python -u -B scripts/run_mysql_integration.py --php-binary C:/tools/php-8.2.35/php.exe --testing-env --execute --existing-schema --migration-roundtrip
```

Preflight reads only the explicitly approved ignored backend testing file,
rejects unsafe effective overrides and validates actual server grants/catalog
before migrations/transactional fixtures. Ordinary `.env` is not loaded.
Post-suite `--inspect` independently confirms no fixture rows remain. Its
file-only APP_KEY false flags are expected; the integration runner key is true.

All new test data are synthetic. No secrets are copied, no database main-target
operations, manual DDL, deletion, remote action, or publication occurred.
The exact changed-file manifest accompanies this report. Overall system PARTIAL,
final approval NOT_APPROVED. Local gates do not prove TLS/hardware/production
readiness, operator authorization, current alarm reconstruction, high-volume
query performance, or cross-boot chronological truth.
