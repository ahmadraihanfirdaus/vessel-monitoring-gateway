# Hardware-free local demonstration

This guide demonstrates actual native firmware code with synthetic data. It does
not connect to an ESP32, application database, vessel, or external service. Run
commands from the root of a reviewed checkout. Python 3, Git and a native C
compiler are prerequisites; missing tools are BLOCKED, not successful execution.

## Native core

```bash
python -B scripts/test_firmware_core_host.py --repeat 2
```

Expected markers include `HOST_FIRMWARE_CORE_SELFTEST: PASS (226/226)` and
`HOST_BOOT_ENTRY_REPETITIONS: PASS (2; same 226 cases per entry)`. These are the
same 226 cases executed twice, not 452 distinct cases. The runner compiles the
actual firmware entry with strict compiler warnings and validates the emitted
suite/case structure. It returns a nonzero status for compile/run/oracle failures.

The runner locates GCC, Clang or `cc` on the child process PATH. On the audited
Windows machine, the child PATH prefix was `C:/msys64/ucrt64/bin`; no global PATH
or XAMPP PHP was changed. Other machines must provide their own compatible tools.

## Four-engine, 48-channel wire fixture

```bash
python -B scripts/continuous_simulation_wire_bridge.py --output demo-frames.jsonl
```

Choose a filename that does not exist. The command refuses an existing artifact.
GCC is the default; a compatible compiler can be selected through the process
variable `VG_HOST_CC`. Compilation and execution are local and finite.

Open the JSONL output in an editor. It contains 24 recovered frames with schema
1.1, 48 channels per frame, simulation source mode, ordered sequence numbers and
200 ms synthetic uptime increments. Values and quality are separate. Invalid,
missing and unknown channels have `null` values; a valid zero remains zero.

The fixture covers safety, propulsion, navigation and power/motion presentation
inputs. Its output is a demonstration artifact, not a physical measurement,
live dashboard, hardware durability experiment or accepted vessel record.

## Traceability

```bash
python -B scripts/check_living_traceability.py
```

The current editable SEC-002 implementation reference points to
`backend/laravel/config/app.php`, which actually loads the application key from
external configuration. It no longer requires a dotenv template to be shipped.
The LOCKED requirement text, mappings, implementation assessments and formal
execution statuses are unchanged. The validator itself was not relaxed.

Historical commits retain their original references and may require their
historical setup. In the sanitized candidate, environment files are deliberately
absent from every tree. An initial candidate traceability failure caused by that
omission is retained as evidence; use the final prepared candidate for review.

## Backend and dashboard: separate advanced workflow

The native demo above is the supported quick start without a database. A full
Laravel dashboard demonstration additionally requires PHP 8.2, Composer
dependencies, an isolated MySQL/MariaDB database, fresh local runtime secrets,
explicit device/session/grant configuration, and the guarded integration tools.
No production or normal application database may be used.

Follow [the MySQL safety protocol](../testing/mysql-integration-gate.md) and
[dashboard integration](../testing/connected-monitoring-dashboard.md) if those
prerequisites are available. Stop if effective Laravel/PHPUnit isolation cannot
be proven. Schema changes must use Laravel migrations; never run manual DDL,
unverified `migrate:fresh`, or ordinary seeders against an application database.

On the audited Windows setup, all PHP verification used the explicit executable
`C:/tools/php-8.2.35/php.exe`. The portfolio preparation does not rerun PHP/DB/TLS
suites because their runtime source/dependencies are unchanged. The README links
the actual recorded runs and their source-bound limitations. No credentials,
APP_KEY value, dotenv template or ready-made operator account is distributed.

Public omission of environment files is intentional. Create any required local
configuration privately according to the existing fail-closed protocols; never
copy an existing application environment into a review checkout. Public CI
configuration contains only reviewed synthetic ephemeral test fixtures and is
not a deployment security profile. Hosted CI remains NOT_RUN.

## Honest demonstration boundaries

- No screenshot is supplied or synthesized as evidence.
- Native PASS does not imply ESP-IDF execution, physical ESP32 verification,
  RTOS timing, persistent NVS behavior or power-loss recovery.
- Local strict TLS/browser records do not prove deployed or physical-device TLS.
- The overall engineering system remains PARTIAL / NOT_APPROVED.
- Do not publish generated artifacts or the original object database without
  completing the separate publication review.
