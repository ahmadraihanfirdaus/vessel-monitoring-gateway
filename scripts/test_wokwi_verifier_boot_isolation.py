#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]

CASES = [
    ("scripts/verify_phase6_f1_wokwi_log.py", "evidence/logs/phase6-f1-wokwi-serial-20261016.txt"),
    ("scripts/verify_phase6_f2_wokwi_log.py", "evidence/logs/phase6-f2-wokwi-serial-20261016.txt"),
    ("scripts/verify_phase7_g1_wokwi_log.py", "evidence/logs/phase7-g1-wokwi-serial-20261016.txt"),
    ("scripts/verify_phase7_g2_wokwi_log.py", "evidence/logs/phase7-g2-wokwi-serial-20261016.txt"),
    ("scripts/verify_phase8_h1_wokwi_log.py", "evidence/logs/phase8-h1-wokwi-serial-20261017.txt"),
]

def run(verifier: pathlib.Path, log: pathlib.Path):
    return subprocess.run(
        [sys.executable, str(verifier), str(log)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

passed = 0
total = 0

for verifier_rel, log_rel in CASES:
    verifier = ROOT / verifier_rel
    log = ROOT / log_rel
    raw = log.read_text(encoding="utf-8", errors="replace")

    total += 1
    p = run(verifier, log)
    ok = p.returncode == 0 and "_WOKWI_LOG_CHECK: PASS" in p.stdout
    passed += ok
    print(f"VERIFIER_BOOT_TEST ORIGINAL_{verifier.stem}: {'PASS' if ok else 'FAIL'}")

    with tempfile.TemporaryDirectory(prefix="vg_boot_mut_") as td:
        td = pathlib.Path(td)

        # A later partial boot with a different app version must become the
        # selected latest boot and therefore fail rather than borrowing markers.
        mut = td / "later_app.txt"
        mut.write_text(
            raw
            + "\nI (1) app_init: Project name:     vessel_gateway_firmware"
            + "\nI (2) app_init: App version:      unexpected-dirty\n",
            encoding="utf-8",
        )
        total += 1
        p = run(verifier, mut)
        ok = p.returncode != 0
        passed += ok
        print(f"VERIFIER_BOOT_TEST REJECT_LATER_APP_{verifier.stem}: {'PASS' if ok else 'FAIL'}")

        # A reset/reboot after a valid terminal return must not be ignored.
        mut = td / "post_return_reset.txt"
        mut.write_text(
            raw + "\nRebooting...\nrst:0xc (SW_CPU_RESET),boot:0x13\n",
            encoding="utf-8",
        )
        total += 1
        p = run(verifier, mut)
        ok = p.returncode != 0
        passed += ok
        print(f"VERIFIER_BOOT_TEST REJECT_POST_RETURN_RESET_{verifier.stem}: {'PASS' if ok else 'FAIL'}")

print(f"WOKWI_VERIFIER_BOOT_ISOLATION: {'PASS' if passed == total else 'FAIL'} ({passed}/{total})")
raise SystemExit(0 if passed == total else 1)
