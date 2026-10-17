# Phase 9 P2 Raw JSON / Value-Presence Hotfix Summary — 2026-10-17

## Scope

This checkpoint hardens only the already-committed P2 telemetry-ingestion
source.

The hotfix:

- replaces the previous global raw-body UInt64 identity-field search with a
  structural top-level JSON member check;
- rejects duplicate JSON keys at the telemetry top level, inside `channels`,
  and inside each channel object;
- adds regression-test definitions for nested `sequence` bypass, duplicate
  object keys, and omitted channel `value`;
- reconciles the P2 design with the Phase 8 wire contract:
  every channel carries `value` and `quality`, and firmware
  `has_value = false` serializes as explicit JSON `null`;
- clarifies dedup semantics as `null` versus finite numeric wire value state,
  with no separate backend value-presence column required for telemetry v1.

## Verification

- P2 design regression: PASS.
- P2 MySQL source-contract regression: PASS.
- Raw UInt64 top-level structural guard: PASS.
- Raw JSON duplicate-key guard: PASS.
- Phase 8 wire-value reconciliation: PASS.
- PHP lint: PASS.
- Composer metadata validation: PASS.
- Semantic security review: PASS.
- LOCKED requirement files remain unchanged.

## Runtime boundary

This is still source/static verification only.

- Laravel feature tests are DEFINED_NOT_RUN.
- MySQL server connection: NOT_ATTEMPTED.
- Database connection/write: NOT_ATTEMPTED.
- Migrations: DEFINED, NOT EXECUTED.
- `vendor/`: ABSENT.
- `.env`: ABSENT.

No formal SIM/SUP completion, physical bench validation, or production
readiness is claimed.

## Gate

PHASE9_P2_RAWJSON_HOTFIX_SOURCE_GATE: PASS
PHASE9_P2_VALUE_PRESENCE_CONTRACT: RECONCILED
BACKEND_VALUE_PRESENCE_MODEL_CHANGE: NOT_REQUIRED
MIGRATIONS_EXECUTED: NO
MYSQL_SERVER_CONNECTION: NOT_ATTEMPTED
DATABASE_CONNECTION: NOT_ATTEMPTED
DATABASE_WRITE: NOT_ATTEMPTED
LARAVEL_FEATURE_TESTS: DEFINED_NOT_RUN
PHASE9_OVERALL_STATUS: IN_PROGRESS
TOTAL_SYSTEM_STATUS: PARTIAL
PHYSICAL_BENCH: NOT_RUN
PRODUCTION_READINESS: NOT_CLAIMED
