# Dedicated host verification: alarm and simulated provider contracts

Source baseline: develop5727969e1f04f49cd26def184e0ab594a6acba6e. Receipt
seven-scope batch is already committed; this is the NEXT substantive verification
slice. Requirements LOCKED and their mapping are unchanged. No existing passing
test is silently relabelled as a dedicated formal execution.

## Seven related scopes and protocol review before execution

1. SUP-004 / ALM-002: actual core alarm lifecycle, operator ACK while condition
   remains active, immutable journal facts and independent delivery semantics.
2. SUP-005 / ENG-002: actual four-engine demonstration and configurable model,
   all required fields, identity/source/invalid/lost-communication boundaries.
3. SUP-007 / NAV-002: actual navigation parser/state, independently constructed
   synthetic RMC/checksum, all fields, age thresholds and malformed/time guards.
4. SUP-008 / MOT-001: actual attitude simulator/decoded-bench constructor,
   roll/pitch/quality and explicit prototype/non-certification labels.
5. SUP-009 / VIB-001: actual vibration simulator/constructor, indicator/fault
   distinction, invalid values and non-diagnostic/non-certification boundary.
6. SUP-010 / PWR-001: actual low-power simulator/constructor, valid zero versus
   missing/invalid/stale, signed current/power and explicit scope labels.
7. Dedicated bounded native runner/oracles/lifecycle negatives, integration and
   regression, CI/security/read-only cleanup/evidence and both handoffs; update
   only eligible formal records after actual case execution/review PASS.

The existing protocol matrix classifies these six as UNIT_TEST_PROTOCOL or
SIMULATOR_TEST_PROTOCOL with console/host evidence and NO_DB_WRITE. Case-by-case
review here admits that exact execution class. No fresh Wokwi or physical bench
is substituted or claimed. This engineering review is performed within the
user-authorized local Goal; it is not independent final system/risk approval.

## Inputs and independent expected results

| Case | Dedicated stimulus and oracle | Mandatory negative/boundary observations |
|---|---|---|
| SUP-004 | Raise actual simulated alarm at0 with explicit source/priority/reason; ACK at0 must retain condition_active, state ACTIVE_ACK, raised0/ACK0 and no cleared time; stored raised transition stays ACTIVE_UNACK. Only explicit later valid clear changes condition. | Early ACK before raised time, duplicate ACK, ACK after clear refuse without mutation; allocator/next event identities remain monotonic. Delivery is never used as operator ACK. |
| SUP-005 | Four demo engines have unique IDs1..4/sourceSIMULATION/RUNNING, RPM2000/2020/2010/1990, temperature82/83/84/82.5, runtime3600/3660/3720/3780, alarmfalse/commGOOD. These are documented synthetic profile values, not engineering limits. | N1/N8 valid, N0/N9 invalid; foreign identity/source, NaN/negative RPM, lost comm with active/known state refuse without overwriting other engines; valid lost state is UNKNOWN/RPM0/alarmfalse. |
| SUP-007 | Python independently builds/checksums a public synthetic RMC for latitude0.5,longitude1.5,SOG5,COG90,fixtrue; actual parser/ingest must expose exact corresponding fields/source/quality/age. Explicit test-only stale100/offline300ms has VALID at99,STALE100,OFFLINE300. | Corrupt checksum, malformed coordinates/nonfinite/invalid course, stale-time inputs must not refresh valid state; check no-fix as an explicit invalid position in existing domain contract. No real route/GP39 or NMEA conformity claim. |
| SUP-008 | Actual eight-step simulator emits the specified motion profile; sourceSIMULATION and quality/has-value/current classification are checked independently. Label must identify attitude/motion prototype and state no vessel-stability certification. | Valid zero remains present, signed angles valid, stale retained but not current, invalid/missing/unknown unavailable, nonfinite/contradictory valid input refused with output unchanged. BENCH_TEST constructor only accepts already-decoded synthetic inputs; no I2C/MPU6050 physical execution. |
| SUP-009 | Actual eight-step indicator profile spans valid0.02/0.35/0.80, stale0.80, missing/invalid/unknown unavailable, recovery0.05; explicit vibration/acceleration prototype/no machinery certification label. | Negative or nonfinite indicator and contradictory has-value/quality refuse unchanged; stale is not current, invalid/missing never safe/zero current. Synthetic decoded bench values are not ADXL345 acquisition or machinery diagnosis. |
| SUP-010 | Actual simulator emits synthetic voltage5/12 and current/power0.10/0.50,0.25/3.00,-0.05/-0.60 with quality. Signed current/power are allowed data, not silently clamped. Explicit low-power bench scope/hazard label. | Valid all-zero is present; invalid/missing/unknown absent, stale not current, negative voltage/nonfinite/contradictory valid input refuse unchanged. No propulsion-current circuit, INA219 driver, wiring/electrical safety or calibration claim. |

Every case must produce dedicated actual observations, explicit expected/actual
comparison and positive/negative/boundary assertion counts. Missing/duplicate
case, field, invalid output, unexpected process exit, source drift or compiler
failure is FAIL/BLOCKED, never an inferred PASS. Native compile keeps C99,
Wall/Wextra/Werror/pedantic and no relaxed production guard. Time/source/counter
defects discovered by execution are fixed only after reproduction and focused
regression; source changes invalidate related SDK/integration proofs.

## Evidence and promotion rule

Before execution capture actual HEAD/branch, source/test/protocol SHA set, compiler
version and test-only inputs. Capture expected results/actual output/case status,
full exit and failures, then inspect case evidence against this protocol. Failed
or unavailable cases retain their old PLANNED status. Only actual dedicated
case PASS with reviewed complete evidence can update its SUP execution row;
no requirement implementation is marked VERIFIED. Preserve all earlier evidence
and append qualified new evidence. Existing SIM and unrelated SUP are untouched.

Run applicable existing/new native regression, real guarded PHP8.2.35/MariaDB and
local TLS integration, security/adversarial/manual and exact-scope commit gates.
Do not access main DB or expose .env/APP_KEY/token/password. No schema change is
planned. Any relevant runtime source edit requires both SDK targets again.
Both handoffs update automatically at safe checkpoints and after local commit.
Cleanup inventory is read-only; protected files/LOCKED/NO PUSH rules persist.

Hardware ESP32/RTOS/PSA/NVS/power-loss/timing, actual sensor/OEM interfaces,
trusted clock/WiFi/deployed TLS, hosted CI, direct MySQL8/POSIX and graphical
browser remain NOT_RUN. Formal records for other cases are not closed by this
slice, and a host SUP PASS does not establish system readiness or risk approval.

PROTOCOL_CASE_BY_CASE_REVIEW=PASS_FOR_THE_SIX_SPECIFIED_HOST_EXECUTION_CLASSES
EXECUTION=NOT_RUN_AT_PROTOCOL_CREATION
