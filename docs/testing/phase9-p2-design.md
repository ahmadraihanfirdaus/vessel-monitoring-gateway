# Phase 9 P2 — Minimum Backend Design

**Baseline:** `develop@fa72f40`
**Status:** DESIGN DEFINED — implementation NOT_STARTED

## 1. Purpose

P2 defines the smallest backend design that can implement the already-defined
Phase 8 telemetry contract without inventing event or device-health wire
contracts that do not yet exist.

Phase 9 as a whole still includes migrations, authenticated ingestion,
state/history/event persistence, device health, and API validation. P2 narrows
the first implementation slice to:

1. migration-controlled telemetry persistence;
2. device-scoped bearer authentication;
3. telemetry request validation;
4. stable-identity deduplication;
5. history persistence for telemetry samples and channels.

Event persistence, full device-health payloads, firmware network retry/offline
behavior, HTTPS deployment, dashboard work, and formal SIM/SUP execution remain
outside this first P2 implementation slice.

## 2. Existing contract that P2 must preserve

Telemetry schema version: `1.0`.

Required payload fields:

- `schema_version`
- `device_id`
- `firmware_version`
- `boot_id`
- `sequence`
- `uptime_ms`
- `source_mode`
- `channels`

Stable sample identity:

`(device_id, boot_id, sequence)`

Token-like identifier limits:

- `device_id`: maximum 48 characters;
- `firmware_version`: maximum 48 characters;
- `boot_id`: maximum 48 characters;
- channel name: maximum 32 characters;
- identifiers/channel names use only `[A-Za-z0-9._:-]`.

Maximum channels: 16.

Allowed source labels:

- `simulation`
- `bench_test`
- `physical`

The `physical` label remains a wire-contract label only and does not prove
physical acquisition or authorize vessel integration.

Allowed channel quality labels:

- `valid`
- `invalid`
- `missing`
- `stale`
- `unknown`

Value/quality rules:

- `valid` requires a finite numeric value;
- `invalid`, `missing`, and `unknown` require `value = null`;
- `stale` may retain a finite numeric value or use `null`;
- duplicate channel names in one payload are rejected;
- invalid or missing values are never silently converted to numeric zero.

Transport payload limit for this API design: at most 4096 bytes.

## 3. Device authentication design

P2 uses device-scoped bearer authentication and does not use the Laravel
`User` model for telemetry ingestion.

The planned API request uses:

`Authorization: Bearer <device-token>`

Rules:

1. The clear token is provisioned outside source control.
2. Only a deterministic one-way token digest is stored in the database.
3. A token maps to exactly one enabled device record.
4. The authenticated device record's `device_id` must exactly match the
   payload `device_id`.
5. Missing/malformed/unknown credentials are rejected.
6. Disabled devices are rejected.
7. No clear credential is committed to Git.

P2 does not claim HTTPS deployment merely because authentication exists.
HTTPS remains required by `SEC-002` and must be verified at the appropriate
deployment/integration gate.

## 4. Minimum migration-controlled schema

All schema changes must be Laravel migrations only.

### 4.1 `devices`

Purpose: authenticate and identify an ingesting device and retain minimum
communication-state metadata.

Columns:

- `id` — primary key;
- `device_id` — string(48), unique, non-null;
- `token_digest` — fixed-length digest field, unique, non-null;
- `enabled` — boolean, default false;
- `last_seen_at` — nullable timestamp;
- `last_boot_id` — nullable string(48);
- `last_sequence` — nullable unsigned big integer;
- Laravel timestamps.

`last_seen_at`, `last_boot_id`, and `last_sequence` are communication metadata,
not a claim of complete device-health coverage.

### 4.2 `telemetry_samples`

Purpose: one persistent historical row per accepted stable telemetry identity.

Columns:

- `id` — primary key;
- `device_id` — foreign key to `devices.id`;
- `schema_version` — string;
- `firmware_version` — string(48);
- `boot_id` — string(48);
- `sequence` — unsigned big integer;
- `uptime_ms` — unsigned big integer;
- `source_mode` — string;
- `received_at` — timestamp;
- Laravel timestamps.

Required unique constraint:

`UNIQUE(device_id, boot_id, sequence)`

This database constraint is the concurrency backstop for `TEL-003`.

### 4.3 `telemetry_channels`

Purpose: preserve each channel's explicit value/quality semantics.

Columns:

- `id` — primary key;
- `telemetry_sample_id` — foreign key to `telemetry_samples.id`, cascade delete;
- `name` — string(32);
- `quality` — string;
- `value` — nullable double;
- Laravel timestamps.

Required unique constraint:

`UNIQUE(telemetry_sample_id, name)`

P2 intentionally does not create an event table or a full device-health table.
The audit contains no approved event/device-health wire schema from which those
columns can be derived safely.

## 5. API surface

First endpoint:

`POST /api/v1/telemetry`

No dashboard endpoint is part of P2.

Expected response classes:

- `201` — distinct valid sample accepted and persisted;
- `200` — identical duplicate accepted idempotently without a second sample row;
- `409` — same stable identity but conflicting semantic payload;
- `413` — payload exceeds the P2 transport size limit;
- `422` — schema/value/identity contract validation failure;
- `401` — missing, malformed, or unknown bearer credential;
- `403` — disabled authenticated device or payload `device_id` does not match
  the authenticated device.

## 6. Validation contract

Before persistence, the backend must validate:

1. body size;
2. JSON object shape;
3. `schema_version == "1.0"`;
4. identifier lengths and safe-token characters;
5. non-negative integer `sequence` and `uptime_ms`;
6. recognized `source_mode`;
7. channels object count is 1..16;
8. unique channel names;
9. recognized quality value;
10. value/quality consistency;
11. authenticated-device identity matches payload device identity.

Validation must fail before any accepted-sample persistence.

## 7. Deduplication behavior

Deduplication is defined by the stable tuple:

`(device_id, boot_id, sequence)`

For a request whose tuple does not yet exist:

- persist one telemetry sample and its channel rows atomically;
- update the authenticated device's minimum communication metadata;
- return `201`.

For a request whose tuple already exists:

- compare persisted semantic fields and channels with the normalized incoming
  payload;
- if semantically identical, create no new rows and return `200`;
- if any semantic field or channel differs, create no new rows and return `409`.

The implementation must still handle a concurrent insert race by relying on the
database unique constraint, reloading the existing row, and applying the same
identical-versus-conflicting decision.

## 8. Transaction boundary

One accepted distinct payload is one database transaction covering:

1. telemetry sample insert;
2. channel inserts;
3. minimum device communication metadata update.

A failed transaction must not leave a partial accepted sample.

## 9. Explicitly deferred from first P2 implementation slice

The following are not implemented or claimed by this design batch:

- event persistence schema;
- complete device-health schema;
- dashboard/UI;
- firmware network transport/reconnect/backoff;
- firmware offline-buffer behavior;
- HTTPS deployment configuration/verification;
- real-device provisioning workflow;
- formal `SIM-010` through `SIM-015`;
- `SUP-013`, `SUP-014`, or other open supplemental tests;
- physical bench execution;
- vessel integration;
- production readiness.

## 10. First P2 implementation gate

The next implementation batch may create only:

- the three migrations above;
- Eloquent models/relations required by those migrations;
- API route/controller/request validation;
- device bearer-auth middleware/service;
- deterministic deduplication service;
- isolated backend tests for new/identical/conflicting payloads and negative
  auth/validation cases.

Database creation or manual schema edits are prohibited. Test database use must
be isolated and migration-driven. MySQL/MariaDB production-like execution is a
later explicit gate; this design definition itself does not connect to or write
any database.

## 11. Status boundary

This document does not mark `API-001`, `DB-001`, `TEL-003`, `SEC-002`,
`SIM-014`, `SIM-015`, or any other open requirement/scenario as formally
verified.

System status remains `PARTIAL`.
