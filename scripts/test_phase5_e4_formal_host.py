#!/usr/bin/env python3
"""Compile the real firmware scaffold and execute formal Phase 5 SIM-001..SIM-006 harness."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LEGACY_SUITES = {
    "CORE_QUALITY_SELFTEST": 7,
    "SOURCE_MODE_SELFTEST": 5,
    "CORE_MEASUREMENT_SELFTEST": 16,
    "CORE_RANGE_SELFTEST": 21,
    "CORE_ALARM_SELFTEST": 30,
    "CORE_SCHEDULER_SELFTEST": 16,
    "CORE_DIAGNOSTICS_SELFTEST": 19,
    "CORE_JOURNAL_SELFTEST": 19,
    "CORE_FLOW_SELFTEST": 36,
    "CORE_RUNTIME_SIM_SELFTEST": 32,
    "CORE_RUNTIME_GUARD_SELFTEST": 25,
}
LEGACY_TOTAL = sum(LEGACY_SUITES.values())
PRIOR_SUITES = (
    ("PHASE4_D1_DOOR_PROVIDER_SELFTEST", 38),
    ("PHASE4_D2_FUEL_VAPOR_PROVIDER_SELFTEST", 53),
    ("PHASE4_D3_BILGE_PROVIDER_SELFTEST", 47),
    ("PHASE4_D4_TEMPERATURE_PROVIDER_SELFTEST", 67),
    ("PHASE4_D5_ATTITUDE_PROVIDER_SELFTEST", 54),
    ("PHASE4_D6_VIBRATION_PROVIDER_SELFTEST", 61),
    ("PHASE4_D7_POWER_PROVIDER_SELFTEST", 61),
    ("PHASE5_E1_SAFETY_POLICY_SELFTEST", 51),
    ("PHASE5_E2_FUEL_SAFETY_SELFTEST", 60),
    ("PHASE5_E3_MONITOR_SAFETY_SELFTEST", 85),
)
FORMAL_IDS = tuple(f"SIM-{index:03d}" for index in range(1, 7))
SUMMARY_RE = re.compile(
    r"^(?P<name>[A-Z0-9_]+): (?P<status>PASS|FAIL) "
    r"\((?P<passed>\d+)/(?P<total>\d+)\)$"
)
SCENARIO_RE = re.compile(
    r"^E4_FORMAL_SCENARIO (?P<id>SIM-00[1-6]): (?P<status>PASS|FAIL)$"
)


def compiler_path() -> str | None:
    for candidate in ("gcc", "clang", "cc"):
        found = shutil.which(candidate)
        if found:
            return found
    return None


def verify_output(output: str) -> None:
    summaries: dict[str, tuple[str, int, int]] = {}
    scenarios: list[tuple[str, str]] = []
    for raw in output.splitlines():
        line = raw.strip()
        if match := SUMMARY_RE.fullmatch(line):
            name = match.group("name")
            if name in summaries:
                raise ValueError(f"duplicate summary: {name}")
            summaries[name] = (
                match.group("status"),
                int(match.group("passed")),
                int(match.group("total")),
            )
        if match := SCENARIO_RE.fullmatch(line):
            scenarios.append((match.group("id"), match.group("status")))

    for name, expected in LEGACY_SUITES.items():
        if summaries.get(name) != ("PASS", expected, expected):
            raise ValueError(f"legacy regression: {name}={summaries.get(name)}")
    for name, expected in PRIOR_SUITES:
        if summaries.get(name) != ("PASS", expected, expected):
            raise ValueError(f"prior regression: {name}={summaries.get(name)}")

    if summaries.get("PHASE5_E4_FORMAL_SCENARIOS") != ("PASS", 6, 6):
        raise ValueError(
            f"formal scenario summary mismatch: {summaries.get('PHASE5_E4_FORMAL_SCENARIOS')}"
        )
    if tuple(item[0] for item in scenarios) != FORMAL_IDS:
        raise ValueError(f"formal scenario IDs/order mismatch: {scenarios}")
    if any(status != "PASS" for _, status in scenarios):
        raise ValueError(f"formal scenario failure: {scenarios}")


def main() -> int:
    compiler = compiler_path()
    if compiler is None:
        print(
            "BLOCKED: no native GCC/Clang/C compiler on PATH; "
            "Phase 5 E4 formal host gate NOT_RUN",
            file=sys.stderr,
        )
        return 3

    with tempfile.TemporaryDirectory(prefix="vg_phase5_e4_") as tmp:
        temp = Path(tmp)
        entry = temp / "entry.c"
        entry.write_text(
            "extern void app_main(void);\n"
            "int main(void) { app_main(); return 0; }\n",
            encoding="utf-8",
        )
        exe = temp / ("phase5_e4.exe" if sys.platform == "win32" else "phase5_e4")
        command = [
            compiler,
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            "-O1",
            "-g",
            str(ROOT / "firmware/src/main.c"),
            str(entry),
            "-o",
            str(exe),
        ]
        if sys.platform != "win32":
            command.append("-lm")

        build = subprocess.run(command, capture_output=True, text=True, errors="replace")
        if build.returncode != 0:
            print("FAIL: Phase 5 E4 native firmware build", file=sys.stderr)
            print(build.stdout + build.stderr, file=sys.stderr)
            return 1

        run = subprocess.run([str(exe)], capture_output=True, text=True, errors="replace")
        if run.returncode != 0:
            print("FAIL: Phase 5 E4 native execution", file=sys.stderr)
            print(run.stdout + run.stderr, file=sys.stderr)
            return 1

        try:
            verify_output(run.stdout)
        except ValueError as error:
            print(f"FAIL: Phase 5 E4 formal output: {error}", file=sys.stderr)
            print(run.stdout, file=sys.stderr)
            return 1

        print(f"E4_HOST_C_COMPILER: {compiler}")
        print(f"E4_LEGACY_SELFTESTS_PRESERVED: PASS ({LEGACY_TOTAL}/{LEGACY_TOTAL})")
        for name, expected in PRIOR_SUITES:
            short = (
                name.replace("PHASE4_", "")
                .replace("PHASE5_", "")
                .replace("_PROVIDER_SELFTEST", "")
                .replace("_SAFETY_POLICY_SELFTEST", "")
                .replace("_FUEL_SAFETY_SELFTEST", "")
                .replace("_MONITOR_SAFETY_SELFTEST", "")
                .replace("_SELFTEST", "")
            )
            print(f"E4_{short}_PRESERVED: PASS ({expected}/{expected})")
        print("PHASE5_E4_HOST_FORMAL_SCENARIOS: PASS (6/6)")
        print(
            "NOTE: Dedicated formal scenario harness executed on the native host. "
            "Phase 5 formal scenario gate is not closed until fresh target/Wokwi "
            "execution, log verification, and evidence finalization also pass."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
