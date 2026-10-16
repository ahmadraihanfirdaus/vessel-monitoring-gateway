#!/usr/bin/env python3
"""Compile the real firmware scaffold and validate Phase 4 Batch D4.

Development-only host verification. It preserves legacy 226/226, D1 38/38,
D2 53/53, and D3 47/47 while validating IF-04 Temperature 67/67.
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

SUMMARY_RE = re.compile(
    r"^(?P<name>[A-Z0-9_]+): (?P<status>PASS|FAIL) "
    r"\((?P<passed>\d+)/(?P<total>\d+)\)$"
)
CASE_RE = re.compile(r"^D4_TEMPERATURE_TEST (?P<name>\S+): (?P<status>PASS|FAIL)$")


def compiler_path() -> str | None:
    for candidate in ("gcc", "clang", "cc"):
        found = shutil.which(candidate)
        if found:
            return found
    return None


def verify_output(output: str) -> None:
    summaries: dict[str, tuple[str, int, int]] = {}
    d4_cases: list[tuple[str, str]] = []

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
            d4_cases.append((match.group("name"), match.group("status")))

    for name, expected in LEGACY_SUITES.items():
        value = summaries.get(name)
        if value != ("PASS", expected, expected):
            raise ValueError(f"legacy regression or missing suite: {name}={value}")

    expected_prior = (
        ("PHASE4_D1_DOOR_PROVIDER_SELFTEST", D1_EXPECTED),
        ("PHASE4_D2_FUEL_VAPOR_PROVIDER_SELFTEST", D2_EXPECTED),
        ("PHASE4_D3_BILGE_PROVIDER_SELFTEST", D3_EXPECTED),
    )
    for name, expected in expected_prior:
        actual = summaries.get(name)
        if actual != ("PASS", expected, expected):
            raise ValueError(f"prior phase regression: {name}={actual}")

    d4 = summaries.get("PHASE4_D4_TEMPERATURE_PROVIDER_SELFTEST")
    if d4 != ("PASS", D4_EXPECTED, D4_EXPECTED):
        raise ValueError(f"wrong D4 summary: {d4}")

    if len(d4_cases) != D4_EXPECTED:
        raise ValueError(
            f"wrong D4 case count: {len(d4_cases)}; expected {D4_EXPECTED}"
        )

    names = [name for name, _ in d4_cases]
    if len(names) != len(set(names)):
        counts = Counter(names)
        duplicates = sorted(name for name, count in counts.items() if count > 1)
        raise ValueError(f"duplicate D4 cases: {duplicates}")

    failed = [name for name, status in d4_cases if status != "PASS"]
    if failed:
        raise ValueError(f"failed D4 cases: {failed}")


def main() -> int:
    compiler = compiler_path()
    if compiler is None:
        print(
            "BLOCKED: no native GCC/Clang/C compiler on PATH; "
            "Phase 4 D4 host test NOT_RUN",
            file=sys.stderr,
        )
        return 3

    with tempfile.TemporaryDirectory(prefix="vg_phase4_d4_") as tmp:
        temp = Path(tmp)
        entry = temp / "entry.c"
        entry.write_text(
            "extern void app_main(void);\n"
            "int main(void) { app_main(); return 0; }\n",
            encoding="utf-8",
        )
        exe = temp / ("phase4_d4.exe" if sys.platform == "win32" else "phase4_d4")

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
            print("FAIL: Phase 4 D4 native firmware build", file=sys.stderr)
            print(build.stdout + build.stderr, file=sys.stderr)
            return 1

        run = subprocess.run([str(exe)], capture_output=True, text=True, errors="replace")
        if run.returncode != 0:
            print("FAIL: Phase 4 D4 native execution", file=sys.stderr)
            print(run.stdout + run.stderr, file=sys.stderr)
            return 1

        try:
            verify_output(run.stdout)
        except ValueError as error:
            print(f"FAIL: Phase 4 D4 output: {error}", file=sys.stderr)
            print(run.stdout, file=sys.stderr)
            return 1

        print(f"D4_HOST_C_COMPILER: {compiler}")
        print(f"D4_LEGACY_SELFTESTS_PRESERVED: PASS ({LEGACY_TOTAL}/{LEGACY_TOTAL})")
        print(f"D4_D1_SELFTEST_PRESERVED: PASS ({D1_EXPECTED}/{D1_EXPECTED})")
        print(f"D4_D2_SELFTEST_PRESERVED: PASS ({D2_EXPECTED}/{D2_EXPECTED})")
        print(f"D4_D3_SELFTEST_PRESERVED: PASS ({D3_EXPECTED}/{D3_EXPECTED})")
        print(f"PHASE4_D4_HOST_SELFTEST: PASS ({D4_EXPECTED}/{D4_EXPECTED})")
        print(
            "NOTE: Host-only development evidence. ESP-IDF/Wokwi/bench/SIM/SUP/"
            "physical verification is not implied."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
