#!/usr/bin/env python3
"""C99 host-only independent-witness guard; no device or DB I/O."""
from pathlib import Path
import os,re,shutil,subprocess,tempfile
R=Path(__file__).resolve().parents[1]
compiler=os.getenv('VG_GCC') or shutil.which('gcc')
assert compiler,'GCC_NOT_FOUND'
with tempfile.TemporaryDirectory(prefix='vg_b22_guard_') as d:
    exe=Path(d)/('fixture.exe' if os.name=='nt' else 'fixture')
    p=subprocess.run([compiler,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
                      '-Ifirmware/src','scripts/phase9_b22_guarded_restore_fixture.c',
                      '-o',str(exe)],cwd=R,text=True,capture_output=True,timeout=90)
    assert p.returncode==0,(p.stdout,p.stderr)
    p=subprocess.run([str(exe)],cwd=R,text=True,capture_output=True,timeout=90)
    assert p.returncode==0,(p.returncode,p.stdout,p.stderr)
    assert re.search(r'^B22_GUARDED=PASS_14_HOST_SCENARIOS_FLOOR_ROLLBACK_SPLIT_BRAIN_ACK$',p.stdout,re.M),p.stdout
    assert 'B22_WITNESS=EXTERNAL_TRUSTED_INPUT_NOT_CRYPTOGRAPHICALLY_VERIFIED' in p.stdout
    assert 'B22_STORAGE_HARDWARE_NETWORK=NOT_VERIFIED' in p.stdout
    print('B22_HOST_GUARD=PASS_TRUSTED_FLOOR_SPLIT_BRAIN_AND_ACK_NO_DB')
