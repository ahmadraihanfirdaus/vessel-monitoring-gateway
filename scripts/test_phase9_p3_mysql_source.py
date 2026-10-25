#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def require(path: str) -> str:
    p = ROOT / path
    if not p.is_file():
        raise AssertionError(f"missing file: {path}")
    return p.read_text(encoding="utf-8")

def has(text: str, token: str, label: str) -> None:
    if token not in text:
        raise AssertionError(f"{label}: missing token: {token}")
    print(f"PHASE9_P3_SOURCE {label}: PASS")

migration = require("backend/laravel/database/migrations/2026_10_18_100004_create_monitoring_events_table.php")
request = require("backend/laravel/app/Http/Requests/EventIngestRequest.php")
service = require("backend/laravel/app/Services/EventIngestService.php")
controller = require("backend/laravel/app/Http/Controllers/Api/EventIngestController.php")
read_service = require("backend/laravel/app/Services/DeviceReadService.php")
routes = require("backend/laravel/routes/api.php")
design = require("docs/testing/phase9-p3-design.md")
plan = require("docs/testing/phase9-p3-implementation-plan.md")

for token in [
    "monitoring_events",
    "device_id",
    "boot_id",
    "event_id",
    "linked_alarm_id",
    "source_id",
    "source_mode",
    "event_type",
    "occurred_at_ms",
    "received_at",
    "monitoring_events_identity_unique",
]:
    has(migration, token, f"MIGRATION_{token.upper()}")

has(request, "18446744073709551615", "UINT64_MAX")
has(request, "4294967295", "UINT32_MAX")
has(request, "simulation,bench_test", "EVENT_SOURCE_MODES")
has(request, "alarm_raised,alarm_ack,alarm_cleared,fault", "EVENT_TYPES")
has(service, "identical_event_duplicate", "EVENT_IDEMPOTENT")
has(service, "conflicting_event_duplicate", "EVENT_CONFLICT")
has(controller, "device_identity_mismatch", "EVENT_IDENTITY_MISMATCH")

for token in [
    "/v1/events",
    "/v1/device/state",
    "/v1/device/history",
    "/v1/device/health",
    "telemetry.payload.size",
    "device.auth",
]:
    label = re.sub(r"[^A-Za-z0-9]+", "_", token).strip("_").upper()
    has(routes, token, f"ROUTE_{label}")

has(read_service, "cursorPaginate", "HISTORY_CURSOR")
has(read_service, "age_seconds", "HEALTH_AGE")
has(design, "(device_id, boot_id, event_id)", "DESIGN_EVENT_IDENTITY")
has(design, "No separate `device_health` table", "DESIGN_NO_HEALTH_TABLE")
has(plan, "must not", "PLAN_NO_DB_EXECUTION")

migrations = sorted((ROOT / "backend/laravel/database/migrations").glob("*.php"))
expected_migrations = [
    '2026_10_17_100001_create_devices_table.php',
    '2026_10_17_100002_create_telemetry_samples_table.php',
    '2026_10_17_100003_create_telemetry_channels_table.php',
    '2026_10_18_100004_create_monitoring_events_table.php',
    '2026_10_25_100005_create_monitoring_access_tables.php',
]
if [p.name for p in migrations] != expected_migrations:
    raise AssertionError('expected exact four original plus additive monitoring-access migration')
print('PHASE9_P3_SOURCE FOUR_ORIGINAL_PLUS_MONITORING_ACCESS_MIGRATION: PASS')

for path in [
    ROOT / "backend/laravel/.env.example",
    ROOT / "backend/laravel/phpunit.xml",
]:
    if "sqlite" in path.read_text(encoding="utf-8").lower():
        raise AssertionError("SQLite application/test policy unexpectedly present")

print("PHASE9_P3_SOURCE MYSQL_ONLY_POLICY: PASS")
print("PHASE9_P3_MYSQL_SOURCE_TEST: PASS")
