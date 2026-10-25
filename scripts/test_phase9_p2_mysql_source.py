#!/usr/bin/env python3
from pathlib import Path
import re
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def check(name, cond):
    print(f"PHASE9_P2_MYSQL_SOURCE {name}: {'PASS' if cond else 'FAIL'}")
    if not cond:
        raise SystemExit(5)

required_files = [
    "docs/testing/phase9-p2-implementation-plan.md",
    "backend/laravel/routes/api.php",
    "backend/laravel/app/Models/Device.php",
    "backend/laravel/app/Models/TelemetrySample.php",
    "backend/laravel/app/Models/TelemetryChannel.php",
    "backend/laravel/app/Services/DeviceTokenAuthenticator.php",
    "backend/laravel/app/Services/TelemetryIngestService.php",
    "backend/laravel/app/Http/Middleware/EnsureTelemetryPayloadSize.php",
    "backend/laravel/app/Http/Middleware/AuthenticateDeviceToken.php",
    "backend/laravel/app/Http/Requests/TelemetryIngestRequest.php",
    "backend/laravel/app/Http/Controllers/Api/TelemetryIngestController.php",
    "backend/laravel/database/migrations/2026_10_17_100001_create_devices_table.php",
    "backend/laravel/database/migrations/2026_10_17_100002_create_telemetry_samples_table.php",
    "backend/laravel/database/migrations/2026_10_17_100003_create_telemetry_channels_table.php",
    "backend/laravel/tests/Feature/TelemetryIngestTest.php",
]
for rel in required_files:
    check("FILE_" + Path(rel).name.upper(), (ROOT / rel).is_file())

env_example = read("backend/laravel/.env.example")
db_config = read("backend/laravel/config/database.php")
bootstrap = read("backend/laravel/bootstrap/app.php")
phpunit = read("backend/laravel/phpunit.xml")
composer = read("backend/laravel/composer.json")
api = read("backend/laravel/routes/api.php")
request = read("backend/laravel/app/Http/Requests/TelemetryIngestRequest.php")
service = read("backend/laravel/app/Services/TelemetryIngestService.php")
m1 = read("backend/laravel/database/migrations/2026_10_17_100001_create_devices_table.php")
m2 = read("backend/laravel/database/migrations/2026_10_17_100002_create_telemetry_samples_table.php")
m3 = read("backend/laravel/database/migrations/2026_10_17_100003_create_telemetry_channels_table.php")

request_model_device = read("backend/laravel/app/Models/Device.php")
request_model_sample = read("backend/laravel/app/Models/TelemetrySample.php")
feature_test = read("backend/laravel/tests/Feature/TelemetryIngestTest.php")

check("ENV_EXAMPLE_MYSQL", "DB_CONNECTION=mysql" in env_example and "DB_CONNECTION=sqlite" not in env_example)
check("ENV_EXAMPLE_HOST", "DB_HOST=127.0.0.1" in env_example)
check("ENV_EXAMPLE_PORT", "DB_PORT=3306" in env_example)
check("CONFIG_DEFAULT_MYSQL", "env('DB_CONNECTION', 'mysql')" in db_config)
check("CONFIG_MYSQL_DATABASE_EXTERNAL", "'database' => env('DB_DATABASE')," in db_config)
check("CONFIG_MYSQL_USERNAME_EXTERNAL", "'username' => env('DB_USERNAME')," in db_config)
check("CONFIG_MYSQL_PASSWORD_EXTERNAL", "'password' => env('DB_PASSWORD')," in db_config)
check("PHPUNIT_MYSQL", '<env name="DB_CONNECTION" value="mysql"/>' in phpunit)
check("PHPUNIT_NO_SQLITE_POLICY", 'DB_CONNECTION" value="sqlite' not in phpunit and 'DB_DATABASE" value=":memory:' not in phpunit)
check("COMPOSER_NO_SQLITE_CREATE", "database/database.sqlite" not in composer)
check("COMPOSER_NO_AUTO_MIGRATE", "artisan migrate" not in composer)

check("BOOTSTRAP_API_ROUTE", "api: __DIR__.'/../routes/api.php'" in bootstrap)
check("BOOTSTRAP_SIZE_ALIAS", "'telemetry.payload.size'" in bootstrap)
check("BOOTSTRAP_DEVICE_ALIAS", "'device.auth'" in bootstrap)
check("API_ENDPOINT", "Route::post('/v1/telemetry'" in api)
check("API_MIDDLEWARE_ORDER", api.find("'telemetry.payload.size'") < api.find("'device.auth'"))

check("REQUEST_SCHEMA_1_0_AND_OPTIONAL_1_1", "'in:1.0,1.1'" in request)
check("REQUEST_CHANNEL_LIMIT_VERSIONED_16_72", "'channels' => ['required', 'array', 'min:1', 'max:'.($this->input('schema_version') === '1.1' ? 72 : 16)]" in request)
legacy_schema = json.loads(read("docs/contracts/telemetry-schema-v1.json"))
extended_schema = json.loads(read("docs/contracts/telemetry-schema-v1.1.json"))
check("LEGACY_SCHEMA_RETAINS_1_0_16", legacy_schema['properties']['schema_version']['const'] == '1.0' and legacy_schema['properties']['channels']['maxProperties'] == 16)
check("OPTIONAL_SCHEMA_1_1_72", extended_schema['properties']['schema_version']['const'] == '1.1' and extended_schema['properties']['channels']['maxProperties'] == 72)
check("REAL_VERSION_BOUNDARY_TEST_DEFINED", "test_v10_stays_16_v11_accepts_72_and_73_rejects_atomically" in read("backend/laravel/tests/Feature/ContinuousSimulationIntegrationTest.php"))
check("REQUEST_SOURCE_MODES", all(x in request for x in ["'simulation'", "'bench_test'", "'physical'"]))
check("REQUEST_QUALITY_MODES", all(x in request for x in ["'valid'", "'invalid'", "'missing'", "'stale'", "'unknown'"]))
check("REQUEST_NULL_CONTRACT", "requires a null value" in request)
check("REQUEST_FINITE_CONTRACT", "is_finite" in request)

digest_name = "token" + "_digest"
check("DEVICE_DIGEST_COLUMN", digest_name in m1 and "char(" in m1)
check("DEVICE_DISABLED_DEFAULT", "->default(false)" in m1)
check("IDENTIFIER_BINARY_COLLATION", m1.count("utf8mb4_bin") >= 3 and "utf8mb4_bin" in m2 and "utf8mb4_bin" in m3)
check("SAMPLE_IDENTITY_UNIQUE", "telemetry_samples_identity_unique" in m2)

check("SAMPLE_DEVICE_EXTERNAL_STRING", "$table->string('device_id', 48)" in m2)
check("SAMPLE_DEVICE_NO_INTERNAL_FOREIGNID", "foreignId('device_id')" not in m2)
check(
    "SAMPLE_DEVICE_EXTERNAL_FK",
    "->references('device_id')" in m2
    and "->on('devices')" in m2,
)
check(
    "SERVICE_USES_EXTERNAL_DEVICE_ID",
    "'device_id' => $device->device_id" in service
    and "->where('device_id', $device->device_id)" in service,
)
check(
    "DEVICE_RELATION_USES_EXTERNAL_DEVICE_ID",
    "'device_id',\n            'device_id'" in request_model_device,
)
check(
    "SAMPLE_RELATION_USES_EXTERNAL_DEVICE_ID",
    "'device_id',\n            'device_id'" in request_model_sample,
)
check("CHANNEL_NAME_UNIQUE", "telemetry_channels_sample_name_unique" in m3)

check("DEDUP_TRANSACTION", "DB::transaction" in service)
check("DEDUP_IDENTITY_BOOT", "->where('boot_id'" in service)
check(
    "DEDUP_IDENTITY_SEQUENCE",
    re.search(
        r"->where\(\s*'sequence'\s*,\s*\$this->normalizeUnsignedInteger"
        r"\(\$payload\['sequence'\]\)\s*\)",
        service,
    ) is not None,
)
check("DEDUP_MYSQL_1062", "1062" in service and "'23000'" in service)
check("DEDUP_CONFLICT_STATUS", "conflicting_duplicate" in service)

check("UINT64_BIGINT_PRESERVATION", "JSON_BIGINT_AS_STRING" in request)
check("UINT64_MAX_BOUND", "18446744073709551615" in request)
check(
    "UINT64_RAW_JSON_NUMBER_GUARD",
    "must be encoded exactly once as an unsigned JSON integer" in request,
)
check("UINT64_NO_GLOBAL_FIELD_OCCURRENCE_COUNT", "preg_match_all" not in request)
check("UINT64_SEQUENCE_CHANNEL_REGRESSION_TEST_DEFINED", "test_channel_named_sequence_does_not_conflict_with_identity_validation" in feature_test)
check("UINT64_SERVICE_NORMALIZATION", "normalizeUnsignedInteger" in service)
check("UINT64_DEVICE_NO_INTEGER_CAST", "'last_sequence' => 'integer'" not in request_model_device)
check("UINT64_SAMPLE_NO_INTEGER_CAST", "'sequence' => 'integer'" not in request_model_sample and "'uptime_ms' => 'integer'" not in request_model_sample)
check("UINT64_FEATURE_TEST_DEFINED", "test_uint64_max_sequence_and_uptime_are_preserved" in feature_test)
check("UINT64_QUOTED_REJECTION_TEST_DEFINED", "test_quoted_uint64_identity_is_rejected" in feature_test)

# Installed local dependencies and ignored dotenv files are not public source.
# Inspect index paths only: never open local secrets or delete user dependencies.
index = subprocess.run(['git', 'ls-files', '--cached', '-z'], cwd=ROOT,
                       capture_output=True, check=True).stdout.decode('utf-8').split('\0')
check("NO_ENV_IN_INDEX", not any(Path(p).name.startswith('.env')
      and Path(p).name not in {'.env.example', '.env.testing.example'} for p in index))
check("NO_SQLITE_IN_INDEX", not any(Path(p).suffix.lower() in {'.sqlite', '.sqlite3', '.db'} for p in index))
check("NO_VENDOR_IN_INDEX", not any('vendor' in Path(p).parts for p in index))

migration_files = sorted((ROOT / "backend/laravel/database/migrations").glob("*.php"))
check("P2_APPLICATION_MIGRATIONS_PRESERVED", {
    '2026_10_17_100001_create_devices_table.php',
    '2026_10_17_100002_create_telemetry_samples_table.php',
    '2026_10_17_100003_create_telemetry_channels_table.php',
} <= {p.name for p in migration_files})
# P3 owns the current complete inventory (four), including monitoring_events.

check("RAW_JSON_STRUCTURAL_MEMBER_PARSER", "parseRawObjectMembers" in request)
check("RAW_JSON_TOP_LEVEL_UNIQUE_GUARD", "validateRawObjectKeyUniqueness" in request)
check("RAW_JSON_DUPLICATE_KEY_HELPER", "duplicateRawKeys" in request)
check(
    "RAW_UINT64_STRUCTURAL_TOP_LEVEL_LOOKUP",
    "matchingMembers" in request
    and "must be encoded exactly once as an unsigned JSON integer" in request,
)
check(
    "RAW_UINT64_NO_GLOBAL_SEQUENCE_REGEX",
    'preg_quote($field' not in request,
)
check(
    "RAW_UINT64_NESTED_SEQUENCE_BYPASS_TEST_DEFINED",
    "test_quoted_top_level_sequence_with_sequence_channel_is_rejected"
    in feature_test,
)
check(
    "RAW_DUPLICATE_TOP_LEVEL_TEST_DEFINED",
    "test_duplicate_top_level_identity_key_is_rejected" in feature_test,
)
check(
    "RAW_DUPLICATE_CHANNEL_TEST_DEFINED",
    "test_duplicate_channel_key_is_rejected" in feature_test,
)

check(
    "WIRE_CHANNEL_EXACT_VALUE_QUALITY_MEMBERS",
    "'channels.*' => ['required', 'array:value,quality']" in request,
)
check(
    "WIRE_VALUE_MEMBER_EXPLICITLY_PRESENT",
    "'channels.*.value' => ['present', 'nullable', 'numeric']" in request,
)
check(
    "WIRE_ABSENT_VALUE_MEMBER_REJECTION_TEST_DEFINED",
    "test_channel_value_member_must_be_explicit_even_when_null" in feature_test,
)

print("PHASE9_P2_MYSQL_SOURCE_TEST: PASS")
