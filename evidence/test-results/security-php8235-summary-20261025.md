# Security/runtime gate record — 2026-10-25 (Asia/Jakarta)

Baseline for this continuation: `develop` at `231cc2b2022223b47790347a5fecf71eb0ee2c44`, with the prior integration worktree preserved. No baseline implementation audit was repeated. Scope is the existing security/runtime/integration batch; no production service, firmware source, migration source or LOCKED requirement/mapping changes.

## Findings and fixes

The [36-occurrence triage](security-36-triage-20261025.csv) records path/layer/line, severity, evidence, impact, disposition and the source fingerprint without secret values. Severity totals are INFO 32, LOW 2, MEDIUM 2; index/working duplicates are retained explicitly. The set contains no identified critical/high vulnerability or actual credential disclosure. This does not claim a complete application/dependency security assessment.

Seventeen occurrences were PHP-arrow parser false positives; ten were unsupported text formats; four were CI boolean/synthetic-key occurrences; four were historical audit-result labels; one was a negative source assertion. Contextual hardening binds the ephemeral CI database port to loopback and replaces fixed test keys with runtime-generated keys. Literal PHP credentials, nonempty environment fallbacks, HTTP(S)/service URL credentials, binary/encoding/size failures and unreviewed privacy indicators remain blocking.

Thirteen exact non-secret assignment review records remain visible in scanner output. Full text coverage also uncovered 141 dependency-author email occurrences in the byte-pinned unchanged Composer lockfile, covered by 53 distinct line fingerprints plus structural JSON-pointer/source checks. Other contacts, changed bytes and malformed metadata remain rejected. No author addresses or user credentials were copied into evidence. See [review protocol](../../docs/testing/security-scanner-review.md) and `scripts/security-reviewed-findings.json`.

The P1 helper initially failed on a stale database configuration hash, then on its old empty-fallback expectation. Both differ from the authoritative B46 HEAD after the earlier P2 implementation, not from current user edits. Byte equality to HEAD and the current required environment lookup were confirmed; only review expectations were reconciled. Original failures remain in [attempt 1](security-php8235-final-review-attempt1-20261025.txt) and [attempt 2](security-php8235-final-review-attempt2-20261025.txt). Database configuration itself is unchanged.

## Actual runtime and test outcomes

Every PHP execution in this continuation uses `C:/tools/php-8.2.35/php.exe`, directly or via explicit `VG_PHP_CLI`. Reported runtime: PHP 8.2.35 CLI, required PDO/mysql/OpenSSL/mbstring/DOM/XML extensions available; Laravel locked/runtime source v12.70.0; PHPUnit 11.5.57; MariaDB 10.4.32. Global PATH and XAMPP are unchanged.

| Gate | Actual outcome | Evidence |
|---|---|---|
| Read-only effective Laravel/PHPUnit/server/grant inspection | PASS for approved catalog/account and empty application tables | [configuration](security-php8235-readonly-config-20261025.txt) |
| APP_KEY source check | File entry empty; controlled runner key generated in memory and cipher-compatible | Same configuration and integration logs; values omitted |
| Verified existing-schema migration roundtrip | PASS rollback/apply/reapply via four existing Laravel migrations | [integration](security-php8235-integration-20261025.txt) |
| Full actual Laravel/PHPUnit/MariaDB suite | PASS 215; zero failed/skipped | Integration log |
| Real wire-to-auth/services/database tests | Eight wire methods plus one populated-catalog rejection method PASS within 215 | Integration log and source test class |
| Laravel receipt/C99 crosscheck | PASS | Integration log |
| Security scanner regression | PASS 20 test methods, including tamper/strong-signature/privacy/boundary cases | Final focused checks |
| Runner/CI generator regression | PASS 20 methods | [focused run](security-php8235-focused-final-20261025.txt) |
| Policy/source/traceability/UI checks | PASS 43 scripts | [policy log](security-php8235-policy-20261025.txt) |
| Standalone PHP ingress/auth fixtures B4/B5/B6/B8 | PASS 3/4/2/2 test methods with PHP 8.2.35 | Focused log |
| B9 middleware CLI and source contract | Initial stub API error, then PASS 15 media/size cases and 3 source checks | [recheck](security-php8235-b9-recheck-20261025.txt) |
| Candidate scanner and pinned framework review | PASS; 0 unresolved secret findings, 0 privacy warnings; 13 reviewed assignments and 141 reviewed metadata occurrences | [final review](security-php8235-final-review-20261025.txt) |
| Final changed/untracked byte screening, traceability and doc status | PASS; zero findings/warnings; reviewed Git text normalization checked | [scope check](security-php8235-scope-check-20261025.txt) |
| Final DB/protected-file/secret-path/index check | PASS; zero application rows, protected hashes unchanged, ignored dotenv excluded, index empty before staging | [integrity](security-php8235-final-integrity-20261025.txt) |

The B9 stand-in lacked `Request::header()` after the existing middleware adopted strict MIME checking. Only the fixture/interface and its obsolete source expectation were corrected; production MIME/size rules were preserved. Cases include JSONP and non-application rejection, structured application JSON, case/parameter handling, exact 4096-byte acceptance and 4097-byte rejection even with a misleading header. The [initial focused failure](security-php8235-focused-final-20261025.txt) is retained; the explicit recheck supersedes it.

The original full candidate scan after text-format support discovered author metadata and later four literal synthetic test-email warnings; those intermediate [scanner](security-php8235-scanner-20261025.txt) and [reviewed scan](security-php8235-scanner-reviewed-20261025.txt) results remain recorded. Test contact values are now generated transiently in isolated fixtures; real unresolved contacts continue to fail. No scanner exception can waive credential tokens/private keys/URL credentials, and dependency author metadata cannot waive ordinary secret findings.

The scanner's last added structural regression rejects non-array author objects as well as root-field impersonation; all 20 current scanner test methods PASS. An intermediate documentation edit stopped on Windows default text decoding. The affected status-document punctuation and write path were corrected using explicit UTF-8; subsequent document/status and content checks PASS. Runtime configuration, ignored credential files and LOCKED documents were not modified by that correction.

The prior 83/53/57 B46/B45/B44 and 226 native-core results remain historical actual execution evidence from this same task. Firmware source did not change; they were not relabeled as freshly rerun on hardware. The eight wire cases are real in-process Laravel/database execution, not a TLS listener or physical bench test.

## Commit and external boundaries

Only exact scoped source/docs/evidence paths are eligible for a local commit after final security, scope, index and protected-file checks. Local HEAD is reported after any actual commit; no remote action or push is authorized. The [current file/hash manifest](mysql-integration-files-20261025.csv) excludes `AGENTS.md`, the two protected untracked firmware files, ignored dotenv files, credentials and temporary fixtures.

Mandatory local gates for this scoped batch are PASS after the documented rechecks. Historical failure logs remain evidence, not outstanding failures. Independent external gates below are unperformed and are not reported as passing this batch. The final staging/commit decision additionally requires manifest-byte equality and the same zero-unresolved screen against the actual index.

Direct MySQL 8 and hosted CI are NOT_RUN; CI key-generator source was executed locally but no hosted job was observed. TLS/deployment, ESP32 physical bench/NVS/crash durability and outstanding dedicated formal SIM/SUP remain NOT_RUN/BLOCKED as applicable. Online dependency-advisory lookup was not performed. The empty file-only testing key remains a direct interactive-startup configuration gap; the documented controlled test runner provides the valid ephemeral testing key. Overall system PARTIAL; final requirement approval NOT_APPROVED. No formal result CSV is promoted.
