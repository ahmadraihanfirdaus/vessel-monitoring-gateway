#!/usr/bin/env python3
"""Compile the real firmware scaffold and validate Phase 5 Batch E3."""
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
    ("PHASE5_E1_SAFETY_POLICY_SELFTEST", 51),
    ("PHASE5_E2_FUEL_SAFETY_SELFTEST", 60),
)
E3_EXPECTED = 85
SUMMARY_RE = re.compile(
    r"^(?P<name>[A-Z0-9_]+): (?P<status>PASS|FAIL) "
    r"\((?P<passed>\d+)/(?P<total>\d+)\)$"
)
CASE_RE = re.compile(
    r"^E3_MONITOR_SAFETY_TEST (?P<name>\S+): (?P<status>PASS|FAIL)$"
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
            raise ValueError(
                f"legacy regression or missing suite: {name}={summaries.get(name)}"
            )
    for name, expected in PRIOR_SUITES:
        if summaries.get(name) != ("PASS", expected, expected):
            raise ValueError(
                f"prior regression or missing suite: {name}={summaries.get(name)}"
            )

    actual = summaries.get("PHASE5_E3_MONITOR_SAFETY_SELFTEST")
    if actual != ("PASS", E3_EXPECTED, E3_EXPECTED):
        raise ValueError(f"wrong E3 summary: {actual}")
    if len(cases) != E3_EXPECTED:
        raise ValueError(
            f"wrong E3 case count: {len(cases)}; expected {E3_EXPECTED}"
        )
    names = [name for name, _ in cases]
    if len(names) != len(set(names)):
        counts = Counter(names)
        duplicates = sorted(name for name, count in counts.items() if count > 1)
        raise ValueError(f"duplicate E3 cases: {duplicates}")
    failed = [name for name, status in cases if status != "PASS"]
    if failed:
        raise ValueError(f"failed E3 cases: {failed}")


def main() -> int:
    compiler = compiler_path()
    if compiler is None:
        print(
            "BLOCKED: no native GCC/Clang/C compiler on PATH; "
            "Phase 5 E3 host test NOT_RUN",
            file=sys.stderr,
        )
        return 3

    with tempfile.TemporaryDirectory(prefix="vg_phase5_e3_") as tmp:
        temp = Path(tmp)
        entry = temp / "entry.c"
        entry.write_text(
            "extern void app_main(void);\n"
            "int main(void) { app_main(); return 0; }\n",
            encoding="utf-8",
        )
        exe = temp / ("phase5_e3.exe" if sys.platform == "win32" else "phase5_e3")
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

        build = subprocess.run(
            command, capture_output=True, text=True, errors="replace"
        )
        if build.returncode != 0:
            print("FAIL: Phase 5 E3 native firmware build", file=sys.stderr)
            print(build.stdout + build.stderr, file=sys.stderr)
            return 1

        run = subprocess.run(
            [str(exe)], capture_output=True, text=True, errors="replace"
        )
        if run.returncode != 0:
            print("FAIL: Phase 5 E3 native execution", file=sys.stderr)
            print(run.stdout + run.stderr, file=sys.stderr)
            return 1

        try:
            verify_output(run.stdout)
        except ValueError as error:
            print(f"FAIL: Phase 5 E3 output: {error}", file=sys.stderr)
            print(run.stdout, file=sys.stderr)
            return 1

        print(f"E3_HOST_C_COMPILER: {compiler}")
        print(
            f"E3_LEGACY_SELFTESTS_PRESERVED: PASS "
            f"({LEGACY_TOTAL}/{LEGACY_TOTAL})"
        )
        for name, expected in PRIOR_SUITES:
            short = (
                name.replace("PHASE4_", "")
                .replace("PHASE5_", "")
                .replace("_PROVIDER_SELFTEST", "")
                .replace("_SELFTEST", "")
            )
            print(f"E3_{short}_PRESERVED: PASS ({expected}/{expected})")
        print(
            f"PHASE5_E3_HOST_SELFTEST: PASS "
            f"({E3_EXPECTED}/{E3_EXPECTED})"
        )
        print(
            "NOTE: Host-only development evidence. Formal SIM-005/SIM-006, "
            "physical engine/pump control, certified vessel rules, physical "
            "local outputs, bench hardware, physical integration and "
            "production readiness are not implied."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
