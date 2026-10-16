#!/usr/bin/env python3
from __future__ import annotations
import pathlib, re, sys

def die(msg):
    print(f"F1_WOKWI_LOG_CHECK: FAIL - {msg}")
    raise SystemExit(1)

if len(sys.argv) != 2:
    die("usage: verify_phase6_f1_wokwi_log.py <full-uart.txt>")

p = pathlib.Path(sys.argv[1])
if not p.is_file():
    die(f"log not found: {p}")

text = p.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")

required = [
    "Project name:     vessel_gateway_firmware",
    "App version:      a008e39-dirty",
    "PHASE4_D1_DOOR_PROVIDER_SELFTEST: PASS (38/38)",
    "PHASE4_D2_FUEL_VAPOR_PROVIDER_SELFTEST: PASS (53/53)",
    "PHASE4_D3_BILGE_PROVIDER_SELFTEST: PASS (47/47)",
    "PHASE4_D4_TEMPERATURE_PROVIDER_SELFTEST: PASS (67/67)",
    "PHASE4_D5_ATTITUDE_PROVIDER_SELFTEST: PASS (54/54)",
    "PHASE4_D6_VIBRATION_PROVIDER_SELFTEST: PASS (61/61)",
    "PHASE4_D7_POWER_PROVIDER_SELFTEST: PASS (61/61)",
    "PHASE5_E1_SAFETY_POLICY_SELFTEST: PASS (51/51)",
    "PHASE5_E2_FUEL_SAFETY_SELFTEST: PASS (60/60)",
    "PHASE5_E3_MONITOR_SAFETY_SELFTEST: PASS (85/85)",
    "PHASE5_E4_FORMAL_SCENARIOS: PASS (6/6)",
    "CORE_RUNTIME_TIMED_DEMO: PASS (6/6)",
    "main_task: Returned from app_main()"
]
parser_total = len(required) + 2
parser_pass = sum(1 for x in required if x in text)
parser_pass += bool(re.search(r"ELF file SHA256:\s+[0-9a-f]{9,}", text))
m = re.search(r"PHASE6_F1_ENGINE_MODEL_SELFTEST: PASS \((\d+)/(\d+)\)", text)
parser_pass += bool(m and m.group(1) == m.group(2) and int(m.group(2)) >= 50)

print(f"F1_WOKWI_LOG_PARSER_SELFTEST: {'PASS' if parser_pass == parser_total else 'FAIL'} ({parser_pass}/{parser_total})")
if parser_pass != parser_total:
    die("required regression/F1 markers missing")

before = re.search(r"C4_MAIN_STACK_WATERMARK_RAW_BEFORE:\s*(\d+)", text)
after = re.search(r"C4_MAIN_STACK_WATERMARK_RAW_AFTER:\s*(\d+)", text)
if not before or not after:
    die("stack watermark markers missing")
if before.group(1) != after.group(1):
    die("stack watermark changed during timed demo")

if re.search(r"\b(FATAL|Guru Meditation|assert failed|panic'ed)\b", text, re.I):
    die("fatal marker found")

print(f"F1_WOKWI_ENGINE_MODEL_SELFTEST: PASS ({m.group(1)}/{m.group(2)})")
print("F1_WOKWI_TIMED_DEMO: PASS (6/6)")
print(f"F1_WOKWI_STACK_WATERMARK_RAW_BEFORE: {before.group(1)}")
print(f"F1_WOKWI_STACK_WATERMARK_RAW_AFTER: {after.group(1)}")
print("F1_WOKWI_LOG_CHECK: PASS")
print("NOTE: Target-side development check only; formal SIM-007 remains NOT_RUN until dedicated scenario evidence is executed.")
