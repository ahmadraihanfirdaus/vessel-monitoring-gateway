#!/usr/bin/env python3
"""Validate a saved Wokwi UART log for Phase 5 Batch E1."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BANNER = "Development self-test scaffold only; operational monitoring and alarm outputs are not implemented."
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
    r"^(?P<name>[A-Z0-9_]+): (?P<status>PASS|FAIL) \((?P<passed>\d+)/(?P<total>\d+)\)$"
)
CASE_RE = re.compile(r"^E1_SAFETY_POLICY_TEST (?P<name>\S+): (?P<status>PASS|FAIL)$")
FATAL_MARKERS = (
    "Guru Meditation Error",
    "assert failed:",
    "abort() was called",
    "Stack smashing",
    "stack overflow",
    "Task watchdog got triggered",
    "panic'ed",
)


def latest_boot(text: str) -> str:
    index = text.rfind(BANNER)
    if index < 0:
        raise ValueError("self-test boot banner not found")
    return text[index:]


def parse_summary(segment: str) -> dict[str, tuple[str, int, int]]:
    summaries: dict[str, tuple[str, int, int]] = {}
    for raw in segment.splitlines():
        line = raw.strip()
        match = SUMMARY_RE.fullmatch(line)
        if not match:
            continue
        name = match.group("name")
        if name in summaries:
            raise ValueError(f"duplicate summary in latest boot: {name}")
        summaries[name] = (
            match.group("status"),
            int(match.group("passed")),
            int(match.group("total")),
        )
    return summaries


def validate(text: str) -> tuple[int | None, int | None]:
    segment = latest_boot(text)
    summaries = parse_summary(segment)

    for name, expected in LEGACY_SUITES.items():
        if summaries.get(name) != ("PASS", expected, expected):
            raise ValueError(f"legacy suite mismatch: {name}={summaries.get(name)}")

    for name, expected in PRIOR_SUITES:
        if summaries.get(name) != ("PASS", expected, expected):
            raise ValueError(f"Phase 4 suite mismatch: {name}={summaries.get(name)}")

    actual = summaries.get("PHASE5_E1_SAFETY_POLICY_SELFTEST")
    if actual != ("PASS", E1_EXPECTED, E1_EXPECTED):
        raise ValueError(f"E1 suite mismatch: {actual}")

    cases: list[tuple[str, str]] = []
    for raw in segment.splitlines():
        if match := CASE_RE.fullmatch(raw.strip()):
            cases.append((match.group("name"), match.group("status")))
    if len(cases) != E1_EXPECTED:
        raise ValueError(f"E1 case count mismatch: {len(cases)}")
    if len({name for name, _ in cases}) != E1_EXPECTED:
        raise ValueError("duplicate E1 case name")
    if any(status != "PASS" for _, status in cases):
        raise ValueError("one or more E1 cases failed")

    timed = summaries.get("CORE_RUNTIME_TIMED_DEMO")
    if timed != ("PASS", 6, 6):
        raise ValueError(f"timed demo mismatch: {timed}")
    if "main_task: Returned from app_main()" not in segment:
        raise ValueError("normal app_main return marker missing")

    lower_segment = segment.lower()
    for marker in FATAL_MARKERS:
        if marker.lower() in lower_segment:
            raise ValueError(f"fatal marker found: {marker}")

    before = re.search(r"C4_MAIN_STACK_WATERMARK_RAW_BEFORE:\s*(\d+)", segment)
    after = re.search(r"C4_MAIN_STACK_WATERMARK_RAW_AFTER:\s*(\d+)", segment)
    return (
        int(before.group(1)) if before else None,
        int(after.group(1)) if after else None,
    )


def parser_selftest() -> None:
    lines = [BANNER]
    for name, count in LEGACY_SUITES.items():
        lines.append(f"{name}: PASS ({count}/{count})")
    for name, count in PRIOR_SUITES:
        lines.append(f"{name}: PASS ({count}/{count})")
    for index in range(E1_EXPECTED):
        lines.append(f"E1_SAFETY_POLICY_TEST CASE_{index:02d}: PASS")
    lines.extend([
        f"PHASE5_E1_SAFETY_POLICY_SELFTEST: PASS ({E1_EXPECTED}/{E1_EXPECTED})",
        "C4_MAIN_STACK_WATERMARK_RAW_BEFORE: 1234",
        "CORE_RUNTIME_TIMED_DEMO: PASS (6/6)",
        "C4_MAIN_STACK_WATERMARK_RAW_AFTER: 1200",
        "I (123) main_task: Returned from app_main()",
    ])
    good = "\n".join(lines)
    validate(good)

    corruptions = [
        good.replace("PHASE5_E1_SAFETY_POLICY_SELFTEST: PASS (51/51)", "PHASE5_E1_SAFETY_POLICY_SELFTEST: FAIL (50/51)"),
        good.replace("E1_SAFETY_POLICY_TEST CASE_00: PASS", "E1_SAFETY_POLICY_TEST CASE_00: FAIL"),
        good.replace("E1_SAFETY_POLICY_TEST CASE_50: PASS\n", ""),
        good.replace("PHASE4_D7_POWER_PROVIDER_SELFTEST: PASS (61/61)", "PHASE4_D7_POWER_PROVIDER_SELFTEST: FAIL (60/61)"),
        good.replace("PHASE4_D1_DOOR_PROVIDER_SELFTEST: PASS (38/38)", "PHASE4_D1_DOOR_PROVIDER_SELFTEST: FAIL (37/38)"),
        good.replace("CORE_QUALITY_SELFTEST: PASS (7/7)", "CORE_QUALITY_SELFTEST: FAIL (6/7)"),
        good.replace("CORE_RUNTIME_TIMED_DEMO: PASS (6/6)", "CORE_RUNTIME_TIMED_DEMO: FAIL (5/6)"),
        good.replace("I (123) main_task: Returned from app_main()", ""),
        good + "\nGuru Meditation Error",
        good.replace(BANNER, "wrong banner", 1),
        good + "\nPHASE5_E1_SAFETY_POLICY_SELFTEST: PASS (51/51)",
        good.replace("E1_SAFETY_POLICY_TEST CASE_50: PASS", "E1_SAFETY_POLICY_TEST CASE_00: PASS"),
    ]
    for index, bad in enumerate(corruptions, start=1):
        try:
            validate(bad)
        except ValueError:
            continue
        raise RuntimeError(f"parser accepted corrupt fixture #{index}")
    print("E1_WOKWI_LOG_PARSER_SELFTEST: PASS (13/13)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", nargs="?")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    parser_selftest()
    if args.selftest:
        return 0
    if not args.log:
        parser.error("UART log path is required unless --selftest is used")

    text = Path(args.log).read_text(encoding="utf-8", errors="replace")
    try:
        before, after = validate(text)
    except ValueError as error:
        print(f"E1_WOKWI_LOG_CHECK: FAIL - {error}", file=sys.stderr)
        return 1

    print("E1_WOKWI_LEGACY_SELFTESTS: PASS (226/226)")
    for name, count in PRIOR_SUITES:
        short = name.replace("PHASE4_", "").replace("_PROVIDER_SELFTEST", "")
        print(f"E1_WOKWI_{short}: PASS ({count}/{count})")
    print(f"E1_WOKWI_SAFETY_POLICY_SELFTEST: PASS ({E1_EXPECTED}/{E1_EXPECTED})")
    print("E1_WOKWI_TIMED_DEMO: PASS (6/6)")
    if before is None or after is None:
        print("E1_WOKWI_STACK_WATERMARK: NOT_RECORDED")
    else:
        print(f"E1_WOKWI_STACK_WATERMARK_RAW_BEFORE: {before}")
        print(f"E1_WOKWI_STACK_WATERMARK_RAW_AFTER: {after}")
    print("E1_WOKWI_LOG_CHECK: PASS")
    print("NOTE: Development log evidence only. Formal SIM-001/SIM-002, physical starter control, certified vessel rules, bench hardware, physical integration and production readiness are not implied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
