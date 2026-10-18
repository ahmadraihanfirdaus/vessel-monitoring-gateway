# Phase 9 P3 Implementation Plan

**Checkpoint:** `b01d7bc0bd95937d2dcc169c541bdf78f170eb5a`

## Source batch

The P3 source batch defines, without executing database migrations:

- one `monitoring_events` migration;
- event model/request/controller/service;
- state/history/health read service and controllers;
- device-scoped P3 routes;
- feature-test definitions;
- static source regression;
- P3 design documentation.

## Database boundary

This source-apply batch must not run migrations, connect to MySQL for schema
changes, use `migrate:fresh`, manually create/alter tables, or modify the
ignored local `.env`.

The application remains MySQL-only.

## Authentication and payload boundary

P3 reuses existing device bearer authentication. Event ingestion also reuses
the existing 4096-byte payload-size middleware.

## Read boundary

State, history and health expose only the authenticated device. Dashboard or
operator authorization is deferred.

## Verification order

1. source apply, no DB execution;
2. PHP lint and static source contract;
3. security/source audit;
4. evidence and exact staging;
5. local commit;
6. explicit migration execution;
7. isolated feature tests;
8. runtime HTTP evidence;
9. scoped P3 completion audit.

Formal SIM/SUP execution remains separate.
