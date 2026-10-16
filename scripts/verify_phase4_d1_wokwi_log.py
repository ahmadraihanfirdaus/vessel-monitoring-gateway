#!/usr/bin/env python3
"""Validate a saved Wokwi UART log for Phase 4 Batch D1.

The parser inspects only the latest self-test boot in the file. It verifies the
legacy 226/226 suite summaries, the D1 38/38 summary, the existing timed 6/6
demo, normal app_main return, and absence of selected fatal markers.

A parser PASS is evidence about the supplied log only. It is not bench,
calibration, formal SIM/SUP, physical-integration, or production verification.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BANNER = (
    "Development self-test scaffold only; "
    "operational monitoring and alarm outputs are not implemented."
)

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

SUMMARY_RE = re.compile(
    r"^(?P<name>[A-Z0-9_]+): (?P<status>PASS|FAIL) "
    r"\((?P<passed>\d+)/(?P<total>\d+)\)$"
)

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
        actual = summaries.get(name)
        if actual != ("PASS", expected, expected):
            raise ValueError(f"legacy suite mismatch: {name}={actual}")

    d1 = summaries.get("PHASE4_D1_DOOR_PROVIDER_SELFTEST")
    if d1 != ("PASS", 38, 38):
        raise ValueError(f"D1 suite mismatch: {d1}")

    timed = summaries.get("CORE_RUNTIME_TIMED_DEMO")
    if timed != ("PASS", 6, 6):
        raise ValueError(f"timed demo mismatch: {timed}")

    if "main_task: Returned from app_main()" not in segment:
        raise ValueError("normal app_main return marker missing")

    for marker in FATAL_MARKERS:
        if marker.lower() in segment.lower():
            raise ValueError(f"fatal marker found: {marker}")

    before = re.search(
        r"C4_MAIN_STACK_WATERMARK_RAW_BEFORE:\s*(\d+)",
        segment,
    )
    after = re.search(
        r"C4_MAIN_STACK_WATERMARK_RAW_AFTER:\s*(\d+)",
        segment,
    )

    before_value = int(before.group(1)) if before else None
    after_value = int(after.group(1)) if after else None

    return before_value, after_value


def parser_selftest() -> None:
    lines = [BANNER]
    for name, count in LEGACY_SUITES.items():
        lines.append(f"{name}: PASS ({count}/{count})")
    lines.extend(
        [
            "PHASE4_D1_DOOR_PROVIDER_SELFTEST: PASS (38/38)",
            "C4_MAIN_STACK_WATERMARK_RAW_BEFORE: 1234",
            "CORE_RUNTIME_TIMED_DEMO: PASS (6/6)",
            "C4_MAIN_STACK_WATERMARK_RAW_AFTER: 1200",
            "I (123) main_task: Returned from app_main()",
        ]
    )
    good = "\n".join(lines)
    validate(good)

    corruptions = [
        good.replace(
            "PHASE4_D1_DOOR_PROVIDER_SELFTEST: PASS (38/38)",
            "PHASE4_D1_DOOR_PROVIDER_SELFTEST: FAIL (37/38)",
        ),
        good.replace(
            "CORE_RUNTIME_TIMED_DEMO: PASS (6/6)",
            "CORE_RUNTIME_TIMED_DEMO: FAIL (5/6)",
        ),
        good.replace(
            "CORE_QUALITY_SELFTEST: PASS (7/7)",
            "CORE_QUALITY_SELFTEST: FAIL (6/7)",
        ),
        good.replace("I (123) main_task: Returned from app_main()", ""),
        good + "\nGuru Meditation Error",
    ]

    for index, bad in enumerate(corruptions, start=1):
        try:
            validate(bad)
        except ValueError:
            continue
        raise RuntimeError(f"parser accepted corrupt self-test fixture #{index}")

    print("D1_WOKWI_LOG_PARSER_SELFTEST: PASS (6/6)")


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

    path = Path(args.log)
    text = path.read_text(encoding="utf-8", errors="replace")

    try:
        before, after = validate(text)
    except ValueError as error:
        print(f"D1_WOKWI_LOG_CHECK: FAIL - {error}", file=sys.stderr)
        return 1

    print("D1_WOKWI_LEGACY_SELFTESTS: PASS (226/226)")
    print("D1_WOKWI_PROVIDER_SELFTEST: PASS (38/38)")
    print("D1_WOKWI_TIMED_DEMO: PASS (6/6)")
    if before is None or after is None:
        print("D1_WOKWI_STACK_WATERMARK: NOT_RECORDED")
    else:
        print(f"D1_WOKWI_STACK_WATERMARK_RAW_BEFORE: {before}")
        print(f"D1_WOKWI_STACK_WATERMARK_RAW_AFTER: {after}")
    print("D1_WOKWI_LOG_CHECK: PASS")
    print(
        "NOTE: Log-level development evidence only; bench hardware, calibration, "
        "formal SIM/SUP, physical integration and production readiness are not implied."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
