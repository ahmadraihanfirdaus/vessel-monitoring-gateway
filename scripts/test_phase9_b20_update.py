#!/usr/bin/env python3
"""Cross-process host-only two-slot update/failure injection evidence."""
from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[1]

def run(cmd, expected=0):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=70)
    assert r.returncode == expected, (r.returncode,r.stdout,r.stderr,cmd)
    return r.stdout

def main():
    compiler = os.getenv('VG_GCC') or shutil.which('gcc')
    assert compiler, 'GCC_NOT_FOUND'
    with tempfile.TemporaryDirectory(prefix='vg_b20_transaction_') as temp:
        directory = Path(temp)
        exe = directory/('fixture.exe' if os.name=='nt' else 'fixture')
        run([compiler,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
             '-Ifirmware/src','scripts/phase9_b20_slot_fixture.c','-o',str(exe)])
        assert 'B20_NEGATIVE=PASS_' in run([str(exe),'negative'])
        audit=[]
        for mode,generation,degraded in [('torn',11,1),('bitflip',11,1),('good',12,0)]:
            slot_a=directory/(mode+'-a.bin')
            slot_b=directory/(mode+'-b.bin')
            assert 'B20_BOOTSTRAP=PASS_10_11' in run([str(exe),'bootstrap',str(slot_a),str(slot_b)])
            older_before=slot_a.read_bytes()
            newest_before=slot_b.read_bytes()
            assert 40 <= len(older_before) <= 800 and 40 <= len(newest_before) <= 800
            update_output=run([str(exe),'update',str(slot_a),str(slot_b),mode])
            assert ('B20_UPDATE=PASS_' if mode=='good' else 'B20_UPDATE=INJECT_') in update_output
            # Newest committed slot must not have been touched by writer in all modes.
            assert slot_b.read_bytes()==newest_before, 'ACTIVE_SLOT_MODIFIED'
            # Across distinct processes, interrupted/corrupt candidate -> old safe generation.
            observed=run([str(exe),'recover',str(slot_a),str(slot_b),str(generation),str(degraded)])
            expected_line='B20_RESTART=PASS_GEN_{}_DEGRADED_{}_ACK_{}_PENDING_RESET'.format(
                generation,degraded,9 if mode=='good' else 8)
            assert expected_line in observed, (mode,observed)
            audit.append(mode+':'+hashlib.sha256(slot_a.read_bytes()+slot_b.read_bytes()).hexdigest())
        print('B20_HOST_TRANSACTIONS=PASS_3_SCENARIOS_TWO_PROCESSES')
        print('B20_RECOVERY=PASS_TORN_CORRUPT_FALLBACK_AND_SUCCESSFUL_UPDATE')
        print('B20_ACK=PASS_PENDING_RESET_AND_CONFIRMED_HIGHWATER_PRESERVED')
        print('B20_HASH_SHA256='+hashlib.sha256('\n'.join(audit).encode()).hexdigest())
        print('B20_DISK_ATOMICITY_ESP_NVS_POWERLOSS=NOT_VERIFIED')

if __name__=='__main__': main()
