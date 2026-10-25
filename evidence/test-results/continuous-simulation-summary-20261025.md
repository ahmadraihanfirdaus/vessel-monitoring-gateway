# Continuous all-domain simulation continuation, 2026-10-25

Baseline: local `develop` HEAD `054cfa5f7f00362e3246d46e9bf5dce9309f9059`.
The B46 reference `231cc2b2022223b47790347a5fecf71eb0ee2c44` is historical;
actual HEAD/worktree were used without reset or repeated baseline audit.
No remote action, physical control, main database access, new migration,
LOCKED requirement edit, firmware upload or repository cleanup occurred.

## Seven related scopes implemented

1. Additive strict telemetry 1.1 (72 channels, 4,096 bytes) with unchanged 1.0
   schema/type/16-channel bound and byte-identical six legacy native packets.
2. Typed existing-provider/engine/navigation composition: 44 domain channels
   for four engines, 68 for eight, explicit source/quality/null/zero/exactness.
3. Continuous simulation scheduler, existing virtual policies, independent local
   alarms/ACK, shared IDs and explicit full-journal loss diagnostics.
4. Opt-in continuous ESP-IDF entry beside retained complete self-test/Wokwi image;
   same partition/TLS/assertion/stack gates for both targets.
5. Independent read-only local policy NVS profile plus existing zero-wait storage/
   cloud workers, optional network identity match, no provisioning/erase/control.
6. Actual recovered full-domain C99 -> Laravel/MariaDB/read/UI/TCP/TLS integration,
   explicit demo enum/unit presentation, and confirmed binary64 persistence fix.
7. CI/source/security regression, failure history, living traceability, exact-scope
   review and metadata-only retained cleanup inventory.

## Executed gate matrix

| Gate | Actual result | Evidence in this directory |
|---|---|---|
| Legacy native core and reentry | PASS 226/226 per entry; two entries, not 452 unique cases | continuous-final-native-security-regression-20261025.txt |
| Strict C99 continuous/model contracts | PASS 13 methods; includes 2,000 cycles, full journal, ACK/reason, clock/sequence, source, null/zero, eight-engine mapping, channel/body limits and allocator exhaustion | same final native log |
| Canonical native packet recovery | PASS 24 actual full-domain packets, each merged/packed/unpacked before output; 48 channels, maximum 2,677 bytes | native fixture/bridge and MySQL log |
| Legacy wire compatibility | PASS unchanged SHA-256 21930ab910d66844d7903d2e726c3c5a8db9809018deacb0e26d93d61f88ee4a | same logs |
| Effective PHP/Laravel/PHPUnit/MySQL isolation | PASS PHP 8.2.35, MariaDB 10.4.32, 127.0.0.1:3307/vessel_gateway_codex_test, vgw_codex, all configured override checks, valid ephemeral process APP_KEY | continuous-mysql-run3-20261025.txt |
| Full actual backend regression | PASS 348 methods, zero failed, zero skipped; actual native wire fixtures, transaction rollback, receipt crosscheck | same MySQL log |
| Version/byte/auth/quality boundaries | PASS real MariaDB admission: 1.0 16/17, 1.1 72/73, 4096/4097, invalid versions/duplicates/uint64/auth; no partial rejected rows | same suite / ContinuousSimulationIntegrationTest |
| Confirmed decimal replay defect | Fixed; exact binary64 storage/replay under PHP precision/serialize_precision=2 in both versions; one-ULP differing values still conflict | same full suite; service diff |
| Real final loopback TCP/TLS/browser-style flow | PASS 94 distinct labeled assertions, original six plus 24 full-domain native packets; all auth/session/CSRF/rate/TLS negatives retained | continuous-http-final-20261025.txt |
| Native full-domain replay and UI | PASS actual TLS ingress/readback, domain enums/units, full-journal rejection count, identical replay and oversize denial | same network log |
| Guarded fixture cleanup | PASS exact lease/token/row ownership and zero application rows after network, including failed first network run | network logs |
| Broad existing CI/source/native/scanner regression | 206 commands executed: initially 203 PASS / 3 FAIL in stale source guards; all three corrected and rerun PASS with seven focused commands | continuous-scoped-regression-20261025.txt; continuous-corrected-regression-20261025.txt |
| Final changed native/security/source checks | PASS eight commands: final 13 C99 methods, 226 core/reentry, five SDK-build methods, eleven HTTP-runner methods, 23 scanner adversarial methods and corrected guards | final-native-security-regression log |
| MySQL-runner ordering/failure guards | PASS 22 methods, including fourth fixture failure before migration | corrected regression log |
| Continuous ESP-IDF candidate | PASS binary 969,632 / 1,048,576 bytes; static RAM 53,708; largest own frame 816 bytes | esp32-transport-sdk-build-continuous-final-20261025.txt |
| Retained full self-test ESP-IDF target | PASS binary 1,042,000 / 1,048,576 bytes; static RAM 66,436; largest own frame 1,616 bytes | esp32-transport-sdk-build-continuous-legacy-final-20261025.txt |
| SDK security/layout/source gates | PASS full TLS roots/chain/hostname/date, assertions, 1 MiB factory partition, blank-NVS offline merge, unchanged source during both builds | same SDK logs |
| Security triage | Five INFO false positives are unchanged previously reviewed CI/runtime-input lines with new exact whole-file pins; no blanket rule added. One separate MEDIUM data-integrity defect was found/fixed by real integration | continuous-security-triage-20261025.csv; security run1 log |
| Final content/security/protected/index/diff gate | PASS working and first exact staged index: zero findings/warnings; protected and diff checks PASS. Final enlarged evidence index is checked again immediately before commit | continuous-final-security-20261025.txt / integrity log / exact file manifest |
| Living traceability and LOCKED integrity | PASS 38/38 mapped, 34 planned tests; requirement assessments/formal results unchanged | final integrity log |
| Cleanup candidates | Seven categories inspected by metadata only; every dependency/artifact/evidence file retained | continuous-cleanup-inventory-20261025.csv |
| New migration roundtrip | NOT_RUN / not required: no schema change; previous guarded roundtrip evidence retained | existing mysql-integration/dashboard evidence |
| Physical ESP32/NVS/flash-cache timing/power loss/wear/full stack+heap, trusted device clock/Wi-Fi/TLS, graphical browser, deployed TLS, direct MySQL 8, hosted CI, new formal SIM/SUP execution | NOT_RUN; external gates remain open | no inference from native/SDK/local TCP gates |

## Source and packet proofs

Both final SDK builds use source digest
`40b451bba4916f48d5b49fb3ed48231eb6a65b1922adebbca877e7877a54c51e`.
Merged candidate hash:
`b40d7a96615e8ace415c119126e8865cad0d43beab1ab1aa2be33765aeb7a289`.
Merged retained self-test hash:
`6627d91657a6e07393691ea2622febc9c2ce07be7f269686df6ab59b000ae80b`.
Their 2 MiB merge size comes from SDK configuration, not physical flash proof.

Full-domain default C99 fixture hash:
`ceda0c0794257456cdaace3d1fb001c6ae430ead882acc693fa36069c1521920`.
Same native coordinator with the loopback lease's fixed owned synthetic identity:
`860d35ecdec8bb5437b20954b7aee1c12988b2ba5bbecb62088297d95e9da875`.
This identity override adds no ownership exemption or third test device.
Final network source digest:
`45a4e09cfa51463811bafe13c8350beb938f55aedc428f3b35b7eca0c033a99c`.

## Failures, review and safety boundaries

Initial failures are retained, not rewritten as PASS: a long native fixture name
failed -Werror compilation; a new test used the wrong existing read-response
wrapper; a mock retained an old fixture call index; real decimal replay conflicted;
three broad regression source guards were stale. The detailed observation record
and original fail logs identify corrections. Old UI placeholder/cursor guards
were replaced by stronger checks for current connected/empty data bindings and
strict-cursor/dependency exception separation. Actual HTTP tests remain mandatory.

The precision issue was actual application logic: ordinary PDO float binding
used PHP's ambient precision and could lose bits before DOUBLE storage. A
locale-independent 17-digit string binding fixes persistence. No epsilon or
conflict-tolerance shortcut was added. Both contract versions are covered.

No passwords, APP_KEY, session IDs, cookies, bearer tokens, TLS private keys or
ordinary dotenv contents are in evidence. Approved test inputs are used internally;
process-only keys are generated, never printed. Final cleanup is ownership-guarded.
SDK log whitespace normalization has before/after hashes and retains diagnostics.
Original 36-scanner-item review stays in its historical evidence unchanged.

The continuous target has no physical acquisition, GPIO, hardware interlock or
approved field engineering defaults. Its four-engine stimuli repeat existing
synthetic providers; synthetic navigation origin is public test input. The
optional UI vocabulary is enabled only explicitly for simulation schema 1.1.
Engine demo alarm flag, coordinator logical indication and journal lifecycle
facts remain distinct. Invalid/missing numeric data never become implicit zero.

Journal capacity eight intentionally refuses additional events while observations
advance. This is not lossless retention or crash-durability proof. Latest-state
queues may coalesce; queued does not mean durable. HTTP completion never deletes
stored data. Complete alarm-metadata wire composition, durable replay/receipt
ACK/deletion, cross-boot ordering and physical drivers remain substantive gaps.
These are not silently marked complete by this vertical slice.

Formal status remains SIM-001..009 PASS, SIM-010..015 NOT_RUN, five SUP PASS and
fourteen PLANNED. All 38 requirements retain their previous assessment/formal
status. Overall system PARTIAL; final approval NOT_APPROVED. See
`docs/testing/continuous-simulation-integration.md` and ADR-0007 for contract,
configuration, capacity and lifecycle details. Exact source/evidence files and
hashes are in the accompanying file manifest. No push is authorized or performed.
