#!/usr/bin/env python3
"""Compile and execute the *real* ESP-IDF-independent firmware self-tests natively.

Only the development self-tests in firmware/src/main.c are covered.
This does not replace target ESP-IDF, Wokwi, SIM/SUP, or physical verification.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SUITES = {
    "CORE_QUALITY_SELFTEST": ("QUALITY_TEST", 7),
    "SOURCE_MODE_SELFTEST": ("SOURCE_MODE_TEST", 5),
    "CORE_MEASUREMENT_SELFTEST": ("MEASUREMENT_TEST", 16),
    "CORE_RANGE_SELFTEST": ("RANGE_TEST", 21),
    "CORE_ALARM_SELFTEST": ("ALARM_TEST", 30),
    "CORE_SCHEDULER_SELFTEST": ("SCHED_TEST", 16),
    "CORE_DIAGNOSTICS_SELFTEST": ("DIAG_TEST", 19),
    "CORE_JOURNAL_SELFTEST": ("JOURNAL_TEST", 19),
    "CORE_FLOW_SELFTEST": ("FLOW_TEST", 36),
}
SUMMARY_RE = re.compile(r"^(CORE_QUALITY_SELFTEST|SOURCE_MODE_SELFTEST|CORE_MEASUREMENT_SELFTEST|CORE_RANGE_SELFTEST|CORE_ALARM_SELFTEST|CORE_SCHEDULER_SELFTEST|CORE_DIAGNOSTICS_SELFTEST|CORE_JOURNAL_SELFTEST|CORE_FLOW_SELFTEST): (PASS|FAIL) \((\d+)/(\d+)\)$")
CASE_RE = re.compile(r"^(QUALITY_TEST|SOURCE_MODE_TEST|MEASUREMENT_TEST|RANGE_TEST|ALARM_TEST|SCHED_TEST|DIAG_TEST|JOURNAL_TEST|FLOW_TEST) (\S+): (PASS|FAIL)$")


def verify_log(log: str) -> None:
    summaries = {}
    cases = Counter()
    case_ids = set()
    for line in log.splitlines():
        line = line.strip()
        m = SUMMARY_RE.fullmatch(line)
        if m:
            name, status, passed, total = m.groups()
            if name in summaries:
                raise ValueError(f"Duplicate suite summary: {name}")
            summaries[name] = (status, int(passed), int(total))
        elif (m := CASE_RE.fullmatch(line)):
            prefix, case_name, state = m.groups()
            if (prefix, case_name) in case_ids:
                raise ValueError(f"Duplicate case: {prefix}/{case_name}")
            case_ids.add((prefix, case_name))
            if state != "PASS":
                raise ValueError(f"Failed case: {prefix}/{case_name}")
            cases[prefix] += 1
        elif line.startswith(tuple(SUITES)) or line.startswith(tuple(value[0] for value in SUITES.values())):
            raise ValueError(f"Malformed test output: {line}")
    if set(summaries) != set(SUITES):
        raise ValueError(f"Wrong suites: {list(summaries)}")
    for suite, (prefix, expected) in SUITES.items():
        status, passed, total = summaries[suite]
        if status != "PASS" or passed != expected or total != expected:
            raise ValueError(f"Wrong suite result: {suite}={summaries[suite]}")
        if cases[prefix] != expected:
            raise ValueError(f"Wrong executed case count: {prefix}={cases[prefix]}; expected {expected}")
    if sum(cases.values()) != sum(count for _, count in SUITES.values()):
        raise ValueError(f"Wrong overall case count: {sum(cases.values())}")


def verify_parser_selftest() -> None:
    good = []
    for suite, (prefix, count) in SUITES.items():
        good.extend(f"{prefix} CASE_{i}: PASS" for i in range(count))
        good.append(f"{suite}: PASS ({count}/{count})")
    good = "\n".join(good)
    verify_log(good)
    bad = {
        "failed_case": good.replace("CASE_0: PASS", "CASE_0: FAIL", 1),
        "missing_case": good.replace("QUALITY_TEST CASE_0: PASS\n", "", 1),
        "false_summary": good.replace("CORE_RANGE_SELFTEST: PASS", "CORE_RANGE_SELFTEST: FAIL"),
        "duplicate_case": good + "\nRANGE_TEST CASE_0: PASS",
    }
    for name, output in bad.items():
        try:
            verify_log(output)
        except ValueError:
            continue
        raise RuntimeError(f"Parser accepted corrupt log: {name}")
    print("HOST_CORE_PARSER_REGRESSION: PASS (5/5)")


def find_compiler():
    for candidate in ("gcc", "clang", "cc"):
        compiler = shutil.which(candidate)
        if compiler:
            return compiler
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parser-only", action="store_true", help="run self-test of log validator only")
    args = parser.parse_args()
    verify_parser_selftest()
    if args.parser_only:
        return 0
    compiler = find_compiler()
    if compiler is None:
        print("BLOCKED: no native GCC/Clang/C compiler on PATH; host C test NOT_RUN", file=sys.stderr)
        return 3
    with tempfile.TemporaryDirectory(prefix="vg_host_core_") as tmp:
        temp = Path(tmp)
        entry = temp / "entry.c"
        entry.write_text("extern void app_main(void);\nint main(void) { app_main(); return 0; }\n", encoding="utf-8")
        exe = temp / ("core_test.exe" if sys.platform == "win32" else "core_test")
        command = [compiler, "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic", "-O1", "-g",
                   str(ROOT / "firmware/src/main.c"), str(entry), "-o", str(exe)]
        if sys.platform != "win32":
            command.append("-lm")
        result = subprocess.run(command, capture_output=True, text=True, errors="replace")
        if result.returncode:
            print("FAIL: native firmware build", file=sys.stderr)
            print(result.stdout + result.stderr, file=sys.stderr)
            return 1
        test = subprocess.run([str(exe)], capture_output=True, text=True, errors="replace")
        if test.returncode:
            print("FAIL: native firmware execution", file=sys.stderr)
            print(test.stdout + test.stderr, file=sys.stderr)
            return 1
        try:
            verify_log(test.stdout)
        except ValueError as e:
            print(f"FAIL: native firmware self-test: {e}", file=sys.stderr)
            print(test.stdout, file=sys.stderr)
            return 1
        print(f"HOST_C_COMPILER: {compiler}")
        total = sum(count for _, count in SUITES.values())
        print(f"HOST_FIRMWARE_CORE_SELFTEST: PASS ({total}/{total})")
        print("NOTE: Native behavior only. Wokwi/ESP-IDF/SIM/SUP/bench verification not implied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
