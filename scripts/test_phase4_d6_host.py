#!/usr/bin/env python3
"""Compile the real firmware scaffold and validate Phase 4 Batch D6.

Development-only host verification. It preserves legacy 226/226, D1 38/38,
D2 53/53, D3 47/47, D4 67/67, and D5 54/54 while validating IF-06
Vibration 61/61.
"""
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
D1_EXPECTED = 38
D2_EXPECTED = 53
D3_EXPECTED = 47
D4_EXPECTED = 67
D5_EXPECTED = 54
D6_EXPECTED = 61

SUMMARY_RE = re.compile(
    r"^(?P<name>[A-Z0-9_]+): (?P<status>PASS|FAIL) "
    r"\((?P<passed>\d+)/(?P<total>\d+)\)$"
)
CASE_RE = re.compile(r"^D6_VIBRATION_TEST (?P<name>\S+): (?P<status>PASS|FAIL)$")


def compiler_path() -> str | None:
    for candidate in ("gcc", "clang", "cc"):
        found = shutil.which(candidate)
        if found:
            return found
    return None


def verify_output(output: str) -> None:
    summaries: dict[str, tuple[str, int, int]] = {}
    d6_cases: list[tuple[str, str]] = []
    for raw in output.splitlines():
        line = raw.strip()
        if match := SUMMARY_RE.fullmatch(line):
            name = match.group("name")
            if name in summaries:
                raise ValueError(f"duplicate summary: {name}")
            summaries[name] = (
                match.group("status"), int(match.group("passed")), int(match.group("total"))
            )
        if match := CASE_RE.fullmatch(line):
            d6_cases.append((match.group("name"), match.group("status")))

    for name, expected in LEGACY_SUITES.items():
        actual = summaries.get(name)
        if actual != ("PASS", expected, expected):
            raise ValueError(f"legacy regression or missing suite: {name}={actual}")

    expected_prior = (
        ("PHASE4_D1_DOOR_PROVIDER_SELFTEST", D1_EXPECTED),
        ("PHASE4_D2_FUEL_VAPOR_PROVIDER_SELFTEST", D2_EXPECTED),
        ("PHASE4_D3_BILGE_PROVIDER_SELFTEST", D3_EXPECTED),
        ("PHASE4_D4_TEMPERATURE_PROVIDER_SELFTEST", D4_EXPECTED),
        ("PHASE4_D5_ATTITUDE_PROVIDER_SELFTEST", D5_EXPECTED),
    )
    for name, expected in expected_prior:
        actual = summaries.get(name)
        if actual != ("PASS", expected, expected):
            raise ValueError(f"prior phase regression: {name}={actual}")

    d6 = summaries.get("PHASE4_D6_VIBRATION_PROVIDER_SELFTEST")
    if d6 != ("PASS", D6_EXPECTED, D6_EXPECTED):
        raise ValueError(f"wrong D6 summary: {d6}")
    if len(d6_cases) != D6_EXPECTED:
        raise ValueError(f"wrong D6 case count: {len(d6_cases)}; expected {D6_EXPECTED}")
    names = [name for name, _ in d6_cases]
    if len(names) != len(set(names)):
        counts = Counter(names)
        duplicates = sorted(name for name, count in counts.items() if count > 1)
        raise ValueError(f"duplicate D6 cases: {duplicates}")
    failed = [name for name, status in d6_cases if status != "PASS"]
    if failed:
        raise ValueError(f"failed D6 cases: {failed}")


def main() -> int:
    compiler = compiler_path()
    if compiler is None:
        print("BLOCKED: no native GCC/Clang/C compiler on PATH; Phase 4 D6 host test NOT_RUN", file=sys.stderr)
        return 3

    with tempfile.TemporaryDirectory(prefix="vg_phase4_d6_") as tmp:
        temp = Path(tmp)
        entry = temp / "entry.c"
        entry.write_text("extern void app_main(void);\nint main(void) { app_main(); return 0; }\n", encoding="utf-8")
        exe = temp / ("phase4_d6.exe" if sys.platform == "win32" else "phase4_d6")
        command = [compiler, "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic", "-O1", "-g", str(ROOT / "firmware/src/main.c"), str(entry), "-o", str(exe)]
        if sys.platform != "win32":
            command.append("-lm")
        build = subprocess.run(command, capture_output=True, text=True, errors="replace")
        if build.returncode != 0:
            print("FAIL: Phase 4 D6 native firmware build", file=sys.stderr)
            print(build.stdout + build.stderr, file=sys.stderr)
            return 1
        run = subprocess.run([str(exe)], capture_output=True, text=True, errors="replace")
        if run.returncode != 0:
            print("FAIL: Phase 4 D6 native execution", file=sys.stderr)
            print(run.stdout + run.stderr, file=sys.stderr)
            return 1
        try:
            verify_output(run.stdout)
        except ValueError as error:
            print(f"FAIL: Phase 4 D6 output: {error}", file=sys.stderr)
            print(run.stdout, file=sys.stderr)
            return 1

        print(f"D6_HOST_C_COMPILER: {compiler}")
        print(f"D6_LEGACY_SELFTESTS_PRESERVED: PASS ({LEGACY_TOTAL}/{LEGACY_TOTAL})")
        print(f"D6_D1_SELFTEST_PRESERVED: PASS ({D1_EXPECTED}/{D1_EXPECTED})")
        print(f"D6_D2_SELFTEST_PRESERVED: PASS ({D2_EXPECTED}/{D2_EXPECTED})")
        print(f"D6_D3_SELFTEST_PRESERVED: PASS ({D3_EXPECTED}/{D3_EXPECTED})")
        print(f"D6_D4_SELFTEST_PRESERVED: PASS ({D4_EXPECTED}/{D4_EXPECTED})")
        print(f"D6_D5_SELFTEST_PRESERVED: PASS ({D5_EXPECTED}/{D5_EXPECTED})")
        print(f"PHASE4_D6_HOST_SELFTEST: PASS ({D6_EXPECTED}/{D6_EXPECTED})")
        print("NOTE: Host-only development evidence. ESP-IDF/Wokwi/bench/SIM/SUP/physical verification is not implied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
