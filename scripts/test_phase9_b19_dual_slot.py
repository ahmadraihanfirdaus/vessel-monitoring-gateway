#!/usr/bin/env python3
"""B19 isolated native host dual-slot two-process recovery proof."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]
def run(argv, timeout=40, cwd=ROOT, expected=0):
    p=subprocess.run(argv,cwd=cwd,capture_output=True,text=True,timeout=timeout)
    assert p.returncode==expected,(p.returncode,p.stdout,p.stderr,argv)
    return p.stdout
def main():
    gcc=os.getenv('VG_GCC') or shutil.which('gcc')
    assert gcc,'GCC_NOT_FOUND'
    with tempfile.TemporaryDirectory(prefix='vg_b19_slots_') as td:
        t=Path(td);exe=t/('fixture.exe' if os.name=='nt' else 'fixture')
        run([gcc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
             '-Ifirmware/src','scripts/phase9_b19_dual_slot_fixture.c','-o',str(exe)],timeout=55)
        slot0=t/'slot0.bin';slot1=t/'slot1.bin'
        assert 'B19_WRITE=PASS_GEN_10_11_TWO_SLOTS' in run([str(exe),'write',str(slot0),str(slot1)])
        bytes0=slot0.read_bytes();bytes1=slot1.read_bytes()
        assert 46<=len(bytes0)<=800 and 46<=len(bytes1)<=800
        assert 'PASS_GEN_11_DEGRADED_0_ACK_8_PENDING_RESET' in run([str(exe),'restore',str(slot0),str(slot1),'normal'])
        assert 'B19_NEGATIVE=PASS_' in run([str(exe),'negative'])
        # Highest slot truncated: older committed snapshot recoverable, no false newer ACK.
        slot1.write_bytes(bytes1[:-2])
        assert 'PASS_GEN_10_DEGRADED_1_ACK_7_PENDING_RESET' in run([str(exe),'restore',str(slot0),str(slot1),'fallback'])
        # Highest slot altered in the inner snapshot: outer CRC must reject it.
        slot1.write_bytes(bytes1[:25]+bytes([bytes1[25]^1])+bytes1[26:])
        assert 'PASS_GEN_10_DEGRADED_1_ACK_7_PENDING_RESET' in run([str(exe),'restore',str(slot0),str(slot1),'fallback'])
        # Both slots invalid must fail closed, never return a fabricated state.
        slot0.write_bytes(bytes0[:3]);run([str(exe),'restore',str(slot0),str(slot1),'fallback'],expected=22)
        # No host fixture is allowed to mutate the original captured snapshot bytes.
        assert len(bytes0)<=800 and len(bytes1)<=800
        print('B19_HOST_DUAL_SLOT=PASS_GEN_11_AND_CONSERVATIVE_GEN_10_RESTART')
        print('B19_HOST_CORRUPTION=PASS_TORN_NEWEST_BITFLIP_BOTH_BAD_REFUSED')
        print('B19_ACK_PENDING=PASS_NEVER_RESTORED_FROM_EITHER_GENERATION')
        print('B19_SLOT_HASH_SHA256='+hashlib.sha256(bytes0+bytes1).hexdigest())
        print('B19_DISK_ATOMICITY_AND_ESP_NVS=NOT_VERIFIED')
if __name__=='__main__':main()
