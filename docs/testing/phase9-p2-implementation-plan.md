# Phase 9 P2 — MySQL Telemetry Ingestion Implementation

**Baseline:** `develop@2cd289d`
**Database policy:** MySQL only
**Status:** SOURCE APPLY PENDING — database execution NOT_ATTEMPTED

## Scope

This batch implements source code only for the first P2 backend slice defined
in `docs/testing/phase9-p2-design.md`:

- MySQL as the Laravel application database policy;
- migration-controlled `devices`, `telemetry_samples`, and
  `telemetry_channels`;
- device-scoped bearer authentication;
- maximum telemetry request body size of 4096 bytes;
- telemetry v1 request validation;
- stable-identity deduplication;
- atomic sample/channel persistence;
- isolated Laravel feature-test definitions.

The source-apply batch does not connect to MySQL, create a database, execute a
migration, install `vendor/`, create `.env`, stage, commit, or push.

## MySQL policy

Tracked example/default configuration is changed from SQLite to MySQL.

Local runtime values are external to source control:

- `DB_CONNECTION=mysql`
- `DB_HOST=127.0.0.1`
- `DB_PORT=3306`
- `DB_DATABASE` supplied by the explicit database gate
- `DB_USERNAME` supplied locally
- `DB_PASSWORD` supplied locally

No application use of `database.sqlite` is permitted.

The generic Laravel SQLite connection definition may remain present as
framework configuration, but it is not selected by the application or test
policy.

## Migration schema

Three Laravel migrations are introduced:

1. `devices`
2. `telemetry_samples`
3. `telemetry_channels`

Identifier columns used by stable identity or channel uniqueness use binary
collation so MySQL comparisons remain case-sensitive like the firmware
contract.

`telemetry_samples.device_id` stores the external telemetry `device_id` and
references `devices.device_id`; it does not store the internal numeric
`devices.id`.

The database unique constraint on `(device_id, boot_id, sequence)` therefore
matches the external stable telemetry identity literally and is the concurrency
backstop for telemetry deduplication.

## HTTP pipeline

`POST /api/v1/telemetry`

Middleware order:

1. telemetry payload-size guard;
2. device bearer-token authentication;
3. Laravel request validation;
4. authenticated device/payload identity match;
5. transactional deduplication/persistence service.

No clear device token is stored. The database stores only a SHA-256 token
digest, and real/local tokens remain outside Git.

## Source-only verification

This batch may run:

- static source-contract checks;
- PHP syntax lint;
- Composer metadata validation;
- existing scanner self-tests;
- the public generic scanner in review/report mode.

It must not run:

- `artisan migrate`;
- application database queries;
- Laravel feature tests that require a database;
- database creation;
- any manual schema statement.

## Deferred

Still deferred:

- event persistence schema;
- complete device-health schema;
- firmware reconnect/backoff/offline-buffer implementation;
- HTTPS deployment verification;
- dashboard work;
- formal SIM/SUP completion claims;
- physical bench work;
- production readiness.

Total system status remains `PARTIAL`.
