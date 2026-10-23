#!/usr/bin/env python3
"""Host C99 test using strict warnings; never accesses DB or hardware."""
from pathlib import Path
import os,shutil,subprocess,tempfile
R=Path(__file__).resolve().parents[1]
cc=os.getenv('VG_GCC') or shutil.which('gcc')
assert cc,'GCC_NOT_FOUND'
with tempfile.TemporaryDirectory(prefix='vg_b23_witness_') as d:
    exe=Path(d)/('fixture.exe' if os.name=='nt' else 'fixture')
    p=subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
        '-Ifirmware/src','scripts/phase9_b23_witness_fixture.c','-o',str(exe)],
        cwd=R,text=True,capture_output=True,timeout=90)
    assert p.returncode==0,(p.stdout,p.stderr)
    p=subprocess.run([str(exe)],cwd=R,text=True,capture_output=True,timeout=90)
    assert p.returncode==0,(p.stdout,p.stderr)
    assert 'B23_WITNESS_COMMIT=PASS_HOST_STAGE_READBACK_EXACT_WITNESS_INTERRUPTED_UPDATE' in p.stdout
    assert 'B23_EXTERNAL_WITNESS=CALLER_MUST_AUTHENTICATE_AND_PERSIST_INDEPENDENTLY' in p.stdout
    assert 'B23_ESP_NVS_POWERLOSS_NETWORK_DB=NOT_VERIFIED' in p.stdout
print('B23_HOST_WITNESS=PASS_STAGE_CANDIDATE_OLD_WITNESS_RESTORE_READBACK_NO_DB')
