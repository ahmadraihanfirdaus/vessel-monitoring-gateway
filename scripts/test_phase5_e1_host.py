#!/usr/bin/env python3
"""Compile the real firmware scaffold and validate Phase 5 Batch E1."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
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
)
E1_EXPECTED = 51

SUMMARY_RE = re.compile(
    r"^(?P<name>[A-Z0-9_]+): (?P<status>PASS|FAIL) "
    r"\((?P<passed>\d+)/(?P<total>\d+)\)$"
)
CASE_RE = re.compile(
    r"^E1_SAFETY_POLICY_TEST (?P<name>\S+): (?P<status>PASS|FAIL)$"
)


def compiler_path() -> str | None:
    for candidate in ("gcc", "clang", "cc"):
        found = shutil.which(candidate)
        if found:
            return found
    return None


def verify_output(output: str) -> None:
    summaries: dict[str, tuple[str, int, int]] = {}
    cases: list[tuple[str, str]] = []

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
        if match := CASE_RE.fullmatch(line):
            cases.append((match.group("name"), match.group("status")))

    for name, expected in LEGACY_SUITES.items():
        if summaries.get(name) != ("PASS", expected, expected):
            raise ValueError(f"legacy regression or missing suite: {name}={summaries.get(name)}")

    for name, expected in PRIOR_SUITES:
        if summaries.get(name) != ("PASS", expected, expected):
            raise ValueError(f"Phase 4 regression or missing suite: {name}={summaries.get(name)}")

    actual = summaries.get("PHASE5_E1_SAFETY_POLICY_SELFTEST")
    if actual != ("PASS", E1_EXPECTED, E1_EXPECTED):
        raise ValueError(f"wrong E1 summary: {actual}")

    if len(cases) != E1_EXPECTED:
        raise ValueError(f"wrong E1 case count: {len(cases)}; expected {E1_EXPECTED}")
    names = [name for name, _ in cases]
    if len(names) != len(set(names)):
        counts = Counter(names)
        duplicates = sorted(name for name, count in counts.items() if count > 1)
        raise ValueError(f"duplicate E1 cases: {duplicates}")
    failed = [name for name, status in cases if status != "PASS"]
    if failed:
        raise ValueError(f"failed E1 cases: {failed}")


def main() -> int:
    compiler = compiler_path()
    if compiler is None:
        print("BLOCKED: no native GCC/Clang/C compiler on PATH; Phase 5 E1 host test NOT_RUN", file=sys.stderr)
        return 3

    with tempfile.TemporaryDirectory(prefix="vg_phase5_e1_") as tmp:
        temp = Path(tmp)
        entry = temp / "entry.c"
        entry.write_text(
            "extern void app_main(void);\nint main(void) { app_main(); return 0; }\n",
            encoding="utf-8",
        )
        exe = temp / ("phase5_e1.exe" if sys.platform == "win32" else "phase5_e1")
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
            print("FAIL: Phase 5 E1 native firmware build", file=sys.stderr)
            print(build.stdout + build.stderr, file=sys.stderr)
            return 1
        run = subprocess.run([str(exe)], capture_output=True, text=True, errors="replace")
        if run.returncode != 0:
            print("FAIL: Phase 5 E1 native execution", file=sys.stderr)
            print(run.stdout + run.stderr, file=sys.stderr)
            return 1
        try:
            verify_output(run.stdout)
        except ValueError as error:
            print(f"FAIL: Phase 5 E1 output: {error}", file=sys.stderr)
            print(run.stdout, file=sys.stderr)
            return 1

        print(f"E1_HOST_C_COMPILER: {compiler}")
        print(f"E1_LEGACY_SELFTESTS_PRESERVED: PASS ({LEGACY_TOTAL}/{LEGACY_TOTAL})")
        for name, expected in PRIOR_SUITES:
            short = name.replace("PHASE4_", "").replace("_PROVIDER_SELFTEST", "")
            print(f"E1_{short}_PRESERVED: PASS ({expected}/{expected})")
        print(f"PHASE5_E1_HOST_SELFTEST: PASS ({E1_EXPECTED}/{E1_EXPECTED})")
        print("NOTE: Host-only development evidence. Formal SIM-001/SIM-002, Wokwi, bench hardware, physical integration and production readiness are not implied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
