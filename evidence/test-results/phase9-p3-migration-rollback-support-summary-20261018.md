# Phase 9 P3 Migration Rollback Support Execution — 2026-10-18

- Source/evidence HEAD: `06bd49a0ce770aae4d3c690c140525f3adeb1c58`.
- Target database: isolated `vessel_monitoring_gateway_test` on MariaDB `127.0.0.1:3307`.
- Application DB was read-only throughout this support execution.
- Precondition: both application and test DBs were 5 tables / 4 migrations /
  zero data rows.
- Laravel `migrate:rollback --step=1` targeted only
  `2026_10_18_100004_create_monitoring_events_table`.
- After rollback, the test DB had 4 tables / 3 migrations:
  `monitoring_events` and only the P3 migration record were removed.
- P1/P2 tables and all three P1/P2 migration records remained present.
- Laravel `migrate` re-applied only the pending P3 migration.
- Final test DB returned to 5 tables / 4 migrations / zero data rows.
- Restored `monitoring_events` verification passed for 11 columns, the
  stable identity unique index, both planned read indexes, and the cascading
  device foreign key.
- Application DB remained 5 tables / 4 migrations / zero data rows.
- This is **supporting migration evidence only**.
- Formal SUP014 remains **NOT_RUN** until its dedicated formal verification
  gate is explicitly executed and recorded.
- Formal SIM010-SIM015 remain **NOT_RUN**.
- SUP013 remains **NOT_RUN**.
- Physical bench remains **NOT_RUN**.
- Production readiness is **not claimed**.
