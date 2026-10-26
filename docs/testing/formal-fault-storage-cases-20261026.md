# Dedicated single-channel isolation, bounded storage and schema roundtrip

Parent develop777d762be36f9e778b9dd259476a28d42393e39f. Data/UI54file batch is
already committed with all mandatory local gates PASS; both handoffs saved and
updated after commit. Index empty; only both postcommit context files are owned
tracked WIP. Protected untracked/LOCKED/history/mainDB unchanged. No cleanup scope.

## Six related scopes

1. SIM011 dedicated actual simulator-host single-temperature-channel isolation,
   typed provider -> domain composition -> real C99 wire. One invalid sensor,
   other channels valid and advancing. This is NOT shared-bus loss or SDK/RTOS
   sampling fault injection. Existing baseline title/meaning is unchanged.
2. SUP013 dedicated actual C99 latest-state/bounded critical-journal integration
   with real host-file write/commit/readback/reopen. Retained original identities,
   full-journal refusal counters, latest replacement and bounded storage verified.
   Host file IO/commit never implies ESP32/NVS/power-loss durability.
3. Independent deterministic native/host-state oracles, source-bound execution,
   fail-closed prerequisite/partial-input/corruption/quality/count/identity tests.
4. Actual dedicated fault packets through PHP8.2.35/MariaDB validation/persistence/
   read/rendering; preserve unaffected valid values and invalid null quality,
   original zero/identity and exact transactional fixture cleanup. This supports
   development integration beyond the SIM011 NO_DB_WRITE host case.
5. SUP014 dedicated guarded Laravel migrations rollback/reapply on the exact
   approved EMPTY existing six-migration testing schema; preflight all effective
   overrides/cipher-compatible ephemeral key/ownership/catalog, actual full PHP
   suite after roundtrip. No manual DDL or main database/provisioning/real data.
6. Necessary existing/new integrated regression, CI source/security/manual scope,
   evidence, eligible formal/living38 only after actual PASS, both handoffs and
   exact local commit on develop; continue safe Goal work, NO PUSH.

## Pre-execution case review and explicit SUP014 target revision

| Case | Existing prescribed class | Dedicated expected observations |
|---|---|---|
| SIM-011 | SIMULATOR_HOST_PROTOCOL / CHANNEL_STATE_AND_FAULT_ISOLATION_LOG / NO_DB_WRITE | Actual synthetic provider failure is restricted to compartment temperature; invalid becomes null with quality,43other current domain channels remain valid and continue with advancing identity/selected engine values. Actual vg_domain_build emits44provider channels; four runtime-diagnostic counters of the separate continuous wrapper are not extra sensor providers. Valid input restores temperature value only after explicit valid provider sample. No complete shared-bus/network recovery claim. |
| SUP-013 | INTEGRATION_TEST_PROTOCOL / INTEGRATION_LOG_AND_STATE_SNAPSHOT / DEPENDS_ON_CASE | Actual native offline transaction retains latest wire and bounded original critical facts across real host file reopen; storage bounds asserted before/after saturation and failure/recovery; no HTTP success as authority to delete. Crypto-confirmed retirement is a separate committed receipt slice, not a shortcut here. |
| SUP-014 | INTEGRATION_TEST_PROTOCOL / INTEGRATION_LOG_AND_STATE_SNAPSHOT / isolated test DB writes | Exactly current Laravel6migration source inventory and approved empty10table catalog admitted; rollback leaves only empty migration table, reapply restores exact10tables/6records/0app rows; full actual PHP/native fixture tests PASS afterward. Missing tool, foreign objects/data, connection override, key/target/engine ambiguity => BLOCKED, never alternate/main database. |

Historical docs/testing/phase9-formal-verification-protocol-matrix.csv SUP014
names vessel_monitoring_gateway_test. It is a historical prepared target, NOT the
approved current database. Keep that matrix, preparation SHA and old evidence
unchanged. This dated execution protocol explicitly revises only operational test
target to user-approved127.0.0.1:3307/vessel_gateway_codex_test/vgw_codex,
driverMySQL/MariaDB10.4.32, testing file backend/laravel/.env.testing internally
guarded. Earlier vg_gateway_test account/old database are NOT admitted. This
implements the user's explicit target correction; no LOCKED requirement, case
stimulus/expected meaning, source migration or primary database is changed.

Use C:/tools/php-8.2.35/php.exe explicitly for every PHP child. Generate temporary
valid application key in process; never output password/key/env/SQL bindings/raw
HTML/session/cookies/private coordinates. Guarded existing-schema roundtrip is
explicitly within the user's authorized isolated migration verification, only
after read-only effective configuration/catalog admission. Preserve initial
failures; no skipping required tests or treating unavailable hardware as PASS.

Record exact command/tool/runtime/parent/tested source hashes, native assertion
and independently expected/actual fields, actual file bounds/digests and scoped
database postchecks. Default executors read-only until explicit execute. Artifact
parsers reject duplicates/nonfinite/type confusion/vacuous counters/fake status/
source drift. If missing prerequisites, retain BLOCKED/NOT_RUN and no batch commit.

No other formal case promoted: SIM010/012/013 still need their own prescribed
outage/multifault/recovery execution and hardware boundaries. SUP017 independent
traceability review and SUP018 hostedCI remain separate. Hardware/currentWokwi/
PSA/NVS/RTOS/powerloss/wear/rollback/fullheap/callstack/timing/clock/WiFi/TLS/OEM,
directMySQL8/POSIX/graphical/deployedTLS NOT_RUN. No requirementVERIFIED.

PROTOCOL_CASE_BY_CASE_REVIEW=PASS_FOR_SIM011_SUP013_SUP014_WITH_BOUNDARIES_ABOVE
EXECUTION=NOT_RUN_AT_PROTOCOL_CREATION
SUP014_TARGET_REVISION=EXPLICIT_USER_APPROVED_CURRENT_ISOLATED_PROFILE_ONLY
