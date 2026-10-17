#!/usr/bin/env python3
from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
FW = ROOT / "firmware" / "src"


def fail(msg: str, output: str = "") -> None:
    if output:
        print(output, end="" if output.endswith("\n") else "\n")
    print(f"PRE_PHASE9_R1_HOST: FAIL - {msg}")
    raise SystemExit(1)


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


gcc = shutil.which("gcc")
if not gcc:
    fail("gcc not found")

source = r"""
#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#include "navigation_nmea.h"
#include "telemetry_contract.h"
#include "provider_contract.h"

static bool close_enough(double a, double b)
{
    return fabs(a - b) <= 0.0001;
}

int main(void)
{
    const double coords[][2] = {
        {12.999999999, 106.8272},
        {-12.999999999, 106.8272},
        {89.999999999, 179.999999999},
        {-89.999999999, -179.999999999},
    };

    for (size_t i = 0u; i < sizeof(coords) / sizeof(coords[0]); ++i) {
        vg_nav_rmc_data_t in = {
            .latitude_deg = coords[i][0],
            .longitude_deg = coords[i][1],
            .sog_knots = 1.0f,
            .cog_deg = 2.0f,
            .fix_valid = true,
        };
        char sentence[VG_NAV_SENTENCE_MAX] = {0};
        vg_nav_rmc_data_t out = {0};

        if (!vg_nav_format_rmc_development(&in, sentence, sizeof(sentence))) return 10 + (int)i;
        if (strstr(sentence, "60.0000") != NULL) return 20 + (int)i;
        if (!vg_nav_parse_rmc_development(sentence, &out)) return 30 + (int)i;
        if (!close_enough(in.latitude_deg, out.latitude_deg) ||
            !close_enough(in.longitude_deg, out.longitude_deg)) return 40 + (int)i;
    }

    vg_telemetry_payload_t malformed = {0};
    malformed.channel_count = VG_TELEMETRY_MAX_CHANNELS + 1u;
    if (vg_tel_find_channel(&malformed, "temperature_c") != NULL) return 50;

    printf("PRE_PHASE9_R1_CODE_REGRESSION: PASS (5/5)\n");
    return 0;
}
"""

with tempfile.TemporaryDirectory(prefix="vg_pre9_r1_") as td:
    td = pathlib.Path(td)
    c = td / "repair_runner.c"
    exe = td / ("repair_runner.exe" if os.name == "nt" else "repair_runner")
    c.write_text(source, encoding="utf-8")
    p = run([
        gcc, "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
        "-I", str(FW), str(c), "-lm", "-o", str(exe)
    ])
    if p.returncode != 0:
        fail("focused repair regression compile failed", p.stdout)
    p = run([str(exe)])
    if p.returncode != 0 or "PRE_PHASE9_R1_CODE_REGRESSION: PASS (5/5)" not in p.stdout:
        fail("focused repair regression failed", p.stdout)

headers = sorted(FW.glob("*.h"))
for h in headers:
    with tempfile.TemporaryDirectory(prefix="vg_header_") as td:
        td = pathlib.Path(td)
        c = td / "header.c"
        obj = td / "header.o"
        c.write_text(
            f'#include "{h.name}"\nint main(void) {{ return 0; }}\n',
            encoding="utf-8",
        )
        p = run([
            gcc, "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
            "-I", str(FW), "-c", str(c), "-o", str(obj)
        ])
        if p.returncode != 0:
            fail(f"standalone header compile failed: {h.name}", p.stdout)

print(f"PRE_PHASE9_R1_C_COMPILER: {gcc}")
print("PRE_PHASE9_R1_CODE_REGRESSION: PASS (5/5)")
print(f"PRE_PHASE9_R1_HEADER_STANDALONE: PASS ({len(headers)}/{len(headers)})")
print("PRE_PHASE9_R1_FOCUSED_HOST_GATE: PASS")
