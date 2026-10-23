#!/usr/bin/env python3
"""Independent host processes emulate verified external epoch; no DB/hardware."""
from pathlib import Path
import os,shutil,subprocess,tempfile
R=Path(__file__).resolve().parents[1]
cc=os.getenv('VG_GCC') or shutil.which('gcc')
assert cc,'GCC_NOT_FOUND'
with tempfile.TemporaryDirectory(prefix='vg_b25_epoch_') as d:
    exe=Path(d)/('epoch.exe' if os.name=='nt' else 'epoch')
    f=Path(d)/'checkpoint.bin'
    p=subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
        '-Ifirmware/src','scripts/phase9_b25_observation_epoch_fixture.c','-o',str(exe)],
        cwd=R,text=True,capture_output=True,timeout=90)
    assert p.returncode==0,(p.stdout,p.stderr)
    def run(*args):
        r=subprocess.run([str(exe),*args],cwd=R,capture_output=True,text=True,timeout=90)
        assert r.returncode==0,(args,r.stdout,r.stderr)
        return r.stdout
    assert 'B25_STAGE=PASS_HOST_ABI_UNTRUSTED_FIXTURE' in run('stage',str(f))
    assert f.is_file() and f.stat().st_size>0
    modes=('old','new','repeat_new','repeat_old','epoch_replay','epoch_gap',
      'epoch_zero','wrong_domain','wrong_tag','guard_witness','bad_receipt',
      'bad_slot','bad_previous','out_of_order','future','overflow',
      'zero_device','zero_domain')
    for mode in modes:
        assert 'B25_OBSERVATION=PASS_'+mode in run('verify',str(f),mode)
print('B25_HOST_OBSERVATION=PASS_18_CROSS_PROCESS_CASES_2_ACCEPT_16_DENY_NO_DB')
print('B25_EXTERNAL_EPOCH_AUTH_DURABILITY_NVS=NOT_VERIFIED')
