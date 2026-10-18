# Phase 9 P3 — Security Fix Feature Test Evidence

Status: **historical test execution verified, staging only**. No new tests executed by this package.

- Repository HEAD at execution and stage: `72f602c483987e5eebaa99137c34e03a7e935a5c` (`develop`).
- Security source changed: exactly `EventIngestRequest.php` and `EventIngestTest.php`.
- Source SHA-256 (EventIngestRequest): `0ab47bacd938ce262be181ed1a994f2a4783df377982f1b6944d76b28d9ca60c`.
- Source SHA-256 (EventIngestTest): `697ef08c3624fd6fbfec0123deec1ce2c9573a3dc545e8b8d3c8fda2bde2915d`.
- Authentic original external evidence ZIP SHA-256: `5df5d856c79fa1f4559596384763a37abe9ea6f2800a9e0c44ea473918130805`.
- Test console: **17 passed, 53 assertions**, process exit code **0**; DeviceRead 7 + EventIngest 10.
- Initial feature-gate summary has **`pass=false` and parsed count 0** due to the ANSI parsing false negative. It is included unchanged, not rewritten to PASS.
- Follow-up evidence verifier: **PASS_VERIFIED_HISTORICAL_EXECUTION** from unchanged original ZIP, with 17 named tests matched to source, source hashes, and snapshot checks.
- Raw console SHA-256: `408b0bd494ed1cbe7ba8b49c23d169547748f29546ac40172ba35cafcc32c61c`; staged ANSI/whitespace-normalized console SHA-256: `ce29e04244b997bc28d8e354a59663879bc660b18b52d7c5b56d445d4d6c2554`.
- Derived recovery audit JSON SHA-256: `6d8017762c6e30bb6b8af60f9b195dae93a18276e2fe71af35c866e7cc3152de`.
- MySQL snapshot reported app/test: 5 tables, 4 migrations, zero data rows, P3 migration batch 2; MySQL port 3307.
- Test DB restoration by Laravel migrations was observed in the source evidence. This package does not connect to either database.
- Evidence is a historical snapshot, not proof that live database state is unchanged at a later time.
- Formal `SUP014=NOT_RUN`; `FORMAL_SUP014_CLAIM=NO`. This is NOT a formal integration gate.
- `TOTAL_SYSTEM_STATUS=PARTIAL`; `PRODUCTION_READINESS=NOT_CLAIMED`.
- No stage of unrelated firmware files. **NO_COMMIT_NO_PUSH**.

## Evidence provenance

The five source records under this evidence basename are derived from the unchanged uploaded ZIP. JSON files are copied byte-for-byte. The console and migration restoration logs only remove ANSI control escapes (console) and trailing whitespace (both); content, counts, and results remain unchanged. The recovery audit JSON is derived from the strict verifier's parsed result; it reports the original gate failure explicitly.

The SHA manifest covers the 2 source files and the 7 non-manifest evidence files, based on **raw staged Git index blobs**.
