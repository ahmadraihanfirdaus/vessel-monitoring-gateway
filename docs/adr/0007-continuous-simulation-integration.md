# ADR-0007 — Continuous simulation integration

Status: implemented for local development; scoped gate evidence recorded in the continuous simulation summary. No physical integration,
production approval or change to LOCKED requirements is granted by this record.

## Problem and compatibility

The existing finite six-step demonstration and its transactional failure guard
are useful test scaffolds. They do not continuously integrate the existing
domain models. Four engines alone require 24 scalar fields; telemetry v1.0 has
a 16-channel development bound. Its payload type, schema, identity semantics,
limits and existing wire bytes must remain compatible.

Introduce optional telemetry schema 1.1 with the same identity/metadata/quality
rules and 4,096-byte body bound, and a separate type holding at most 72 channels (68 domain fields for eight engines plus four diagnostics).
Version 1.0 remains limited to 16. Both versions use the same channel validation
and serialization primitives. Increasing the channel count does not guarantee
that an arbitrary packet fits the byte bound; oversized encoding must fail
explicitly without publishing a partial or truncated latest state. Existing
1.0 schema/document snapshots are retained.

## Seven related scopes

1. Additive versioned full-domain telemetry, strict native/PHP contracts and old
   wire compatibility; no database schema change is needed.
2. Reuse existing simulated providers, engine model and NMEA development parser
   in one typed SIMULATION-only snapshot, preserving invalid/null/zero semantics.
3. Continuous local scheduling/policy/alarm evaluation independent of network or
   storage acceptance, with explicit bounded-journal loss diagnostics.
4. Opt-in ESP-IDF runtime candidate alongside the retained full self-test image;
   both targets keep mandatory build/testing gates and no upload command.
5. Compose existing Wi-Fi/NVS workers through zero-wait submission APIs and
   externally supplied runtime policy/identity. Missing network configuration
   must not prevent a configured local simulation.
6. Explicit demo channel presentation and actual C99/Laravel/MariaDB/HTTP/browser
   integration, with readable source/quality and no invented OEM units or rules.
7. Negative/boundary/security/regression/resource gates and scoped evidence,
   traceability and read-only cleanup inventory.

## Safety and lifecycle

All acquisition in this slice is simulation. Existing physical providers remain
placeholders. Local LED/buzzer requests are logical values, never GPIO actions.
Pre-start decisions remain virtual, configuration-driven and unverified for a
real vessel. Existing hatch/vapor policy and ALERT_ONLY bilge/temperature policy
must be reused, including rejection of invented monitor BLOCK interlocks.

The new continuous composition does not change core_flow rollback or the old
finite guard. Instead it owns observation/alarm progression independently of
journal admission. A full journal retains old critical entries, refuses new ones
explicitly and increments bounded diagnostics; it must not freeze sampling or
local indications. No silent eviction, automatic ACK, physical safe-state claim
or claim of lossless retention is permitted. Future durable replay/deletion
requires its own receipt/order contract.

Runtime sampling/age/threshold policy must be explicit. No operational defaults,
field-verified rules or clock accuracy are invented. Demonstration inputs remain
clearly synthetic. Numeric channel encoding must not silently round a uint64
runtime outside the exact numeric range; invalid/unrepresentable values require
explicit null/quality. Boot-relative clocks are not UTC.

## Evidence boundary

Retain legacy native/self-test/SDK gates and add continuous-coordinator, full-domain
wire, new-version admission and real isolated backend/UI regression. Compile both
SDK targets, preserving the application/stack/TLS gates. Host simulation, SDK
compilation and actual ESP32/NVS/power-loss/timing remain separate claims. Formal
SIM/SUP execution, hosted CI, physical acquisition and production readiness are
not inferred from this implementation.
