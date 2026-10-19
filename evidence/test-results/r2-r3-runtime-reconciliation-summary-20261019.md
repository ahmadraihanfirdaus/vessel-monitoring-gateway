# R2/R3 Qualified Runtime Evidence Record — Unstaged

**Evidence class:** scoped R2/R3 reconciliation, not final Phase 9 closure or production acceptance.
**Git HEAD:** `37204913b99a6db1b5c0dab9292187ec3025d4b9` (`develop`); two R2 source/test files modified but UNSTAGED.
**Captured canonical preflight:** `R2_R3_QUALIFIED_EVIDENCE_RECORD_PREFLIGHT: PASS_READY_TO_RECORD_WITH_INDETERMINATE_SERVER_TRACE`.

## R2 regression evidence

- Historical defect independently reproduced at R1: sequence `10 -> 11 -> identical duplicate 10` lowered `last_sequence` from 11 to 10.
- Patched R2 feature class: **18/18 tests, 60 assertions, exit code 0**, recovered from original Laravel PHPUnit console; it is not a new test execution in this record gate.
- Original PHPUnit log SHA-256: `dd706e543da2bb11db1aca7183634681f06c73e3951d084eb4f9e4d7991a62af`; verified by canonical R2 read-only recovery.
- Original test database was restored with Laravel migrations to 4 migrations/P3 batch 2 and zero data rows, per previous gate and read-only checks.

## R3 runtime evidence and limitation

- Original R3 HTTP harness internally recorded **18/18 scenarios PASS**, including 16 post-P3-security-fix cases, a Unicode-escaped duplicate event JSON key rejection and R2 high-watermark behavior.
- R3 original JSON SHA-256: `2bfb408c13f49cbd4e4e8f924e81c03b12fd08ff75ad0f54614fa8417bf1c85d`.
- R3 PHP loopback server log SHA-256: `753fbdd57cb462dac15a7455d39072fe3f343967a6f8426f27d970c02e704d18`.
- **Independent server log HTTP-status trace: INDETERMINATE, 0 parseable events.** Internal R3 result JSON/terminal reporting is not independent corroboration of each HTTP status code. Do NOT relabel this as server-status PASS.
- `R3_INDEPENDENT_SERVER_HTTP_TRACE=INDETERMINATE_ZERO_STATUS_EVENTS`
- `R3_SECURITY_AND_CURSOR=PASS_AS_RECORDED_BY_ORIGINAL_RUNTIME_ONLY`

## Explicit boundary and source-provenance controls

`CROSS_BOOT_DISTINCT_OUT_OF_ORDER=UNRESOLVED`
`PHASE9_SCOPED_CLOSURE=NOT_YET_RECORDED`
`SUP014=NOT_RUN`
`TOTAL_SYSTEM_STATUS=PARTIAL_NOT_PRODUCTION_READY`
`PRODUCTION_READINESS=NOT_CLAIMED`
`TESTS_REEXECUTED=NO`
`DATABASE_WRITE=NO`
`NO_STAGE_NO_COMMIT_NO_PUSH`

The read-only canonical R2/R3 preflight checks the isolated MySQL application and test databases on **port 3307**, not XAMPP 3306. This record gate makes no repository source/roadmap edits, no database changes, no feature or HTTP test reruns and no Git staging/commit/push.

Only these three files are generated under `evidence/test-results/`: the captured canonical audit, this conservative summary, and a two-entry SHA-256 manifest over exact audit + summary bytes. Original off-repository R2 console and R3 server logs are not copied into Git. A future separate diff-audit and explicit exact-stage gate are required before any commit.
