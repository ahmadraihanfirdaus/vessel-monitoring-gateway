# Phase 9 P1 — Laravel Foundation

**Baseline:** `develop@33bee83`
**Status:** BATCH COMPLETE — Laravel foundation gate PASS; database NOT_ATTEMPTED

## Scope

Create the initial Laravel 12 backend foundation under `backend/laravel/`
without connecting to or modifying any database.

This batch is intentionally limited to:

- Laravel 12 application skeleton;
- dependency resolution lock file without installing `vendor/`;
- standard application/configuration structure;
- repository-local foundation validation;
- no API ingestion implementation yet;
- no authentication implementation yet;
- no application migrations yet;
- no database connection or database write.

## Boundaries

- LOCKED requirements and traceability files are not modified.
- No `.env` file is tracked.
- No `vendor/` directory is tracked.
- No SQLite database file is tracked.
- Default Laravel migration files are removed from this P1 batch.
- MySQL/MariaDB is not contacted.
- `DB-001`, `API-001`, `TEL-003`, `NET-001`, `NET-002`, `SEC-002`, and
  formal SIM/SUP verification remain open.
- System status remains PARTIAL.
- Physical bench remains NOT_RUN.
- Production readiness is not claimed.

## P1 exit check

P1 source is ready for evidence/staging only when:

1. Laravel foundation test passes.
2. `composer validate --strict` passes.
3. all backend PHP files pass `php -l`.
4. security regression passes.
5. no database connection/write occurs.
6. LOCKED SHA values remain exact.
7. only the known local firmware configuration paths remain unrelated
   untracked files.

## P1 security semantic classification — 2026-10-17

The generic repository security scanner correctly requested manual review for
stock Laravel framework files. The findings were classified before any staging
or commit.

Unneeded stock development/upstream artifacts were removed:

- `database/factories/UserFactory.php` (contained a stock literal test password);
- `database/seeders/DatabaseSeeder.php` (depended on the removed stock factory);
- `public/favicon.ico` (empty stock file);
- Laravel upstream `README.md` (contained upstream public contact metadata).

The remaining scanner review items are accepted only through
`scripts/audit_phase9_p1_security_review.py`, which pins exact SHA-256 values
and exact semantic lines. It does not weaken or modify the baseline security
scanner. Any changed file or any additional finding/warning blocks the P1
security gate.

Database connection/write remains NOT_ATTEMPTED. No application migration is
introduced in P1.

## P1 verification result — 2026-10-17

- Laravel application skeleton: PRESENT.
- Locked Laravel framework package: `v12.70.0`.
- Composer validation: PASS.
- PHP lint: PASS.
- Generic security scanner findings were manually classified by an exact,
  hash-pinned semantic review gate: 12/12 reviewed, 0 warnings.
- The baseline security scanner itself was not weakened or modified.
- `.env`: ABSENT.
- `vendor/`: ABSENT.
- application migrations: ABSENT.
- database connection: NOT_ATTEMPTED.
- database write: NOT_ATTEMPTED.
- LOCKED requirement files: unchanged.
- total system status: PARTIAL.
- physical bench: NOT_RUN.
- production readiness: NOT_CLAIMED.

This P1 gate establishes the Laravel foundation only. It does not claim
`API-001`, `DB-001`, `TEL-003`, `NET-001`, `NET-002`, `SEC-002`, or any
remaining SIM/SUP item as formally verified.
