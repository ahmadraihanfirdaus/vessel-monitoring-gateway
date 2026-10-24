#!/usr/bin/env python3
"""B33 host-only C99 two-revision-probe cross-process matrix."""
import os,shutil,subprocess,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
cc=os.getenv('VG_GCC') or shutil.which('gcc')
assert cc,'B33_GCC_MISSING'
cases=(
    'accept',
    'probe_first_fail',
    'probe_second_fail',
    'probe_first_wrong_revision',
    'probe_second_wrong_revision',
    'probe_first_mutate_pending',
    'probe_second_mutate_pending',
    'probe_first_mutate_cas',
    'probe_second_mutate_cas',
    'probe_first_mutate_rr',
    'probe_second_mutate_rr',
    'probe_first_mutate_readback',
    'probe_second_mutate_readback',
    'null_probe',
    'null_context',
    'wrong_revision',
    'wrong_readback',
    'wrong_ack',
    'alias_cas_pending',
    'alias_rr_pending',
    'alias_rr_cas',
    'alias_readback_pending_image',
    'alias_guard_pending_guard',
    'alias_guard_fence',
    'null_pending',
    'null_cas',
    'null_rr',
    'null_readback',
    'no_external_cas',
    'no_external_readback',
)
assert len(cases)==30 and len(set(cases))==30
with tempfile.TemporaryDirectory(prefix='vg_b33_revision_') as td:
    exe=Path(td)/('b33.exe' if os.name=='nt' else 'b33')
    snap=Path(td)/'checkpoint.bin'
    comp=subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
        '-Ifirmware/src','scripts/phase9_b33_stable_revision_fixture.c','-o',str(exe)],
        cwd=R,capture_output=True,text=True,timeout=90)
    assert comp.returncode==0,(comp.stdout,comp.stderr)
    def run(*args):
        p=subprocess.run([str(exe),*args],cwd=R,capture_output=True,text=True,timeout=90)
        assert p.returncode==0,(args,p.stdout,p.stderr)
        return p.stdout
    assert 'B28_STAGE=PASS_TWO_ROUND_CHECKPOINT_FIXTURE' in run('stage',str(snap))
    for case in cases:
        assert 'B33_REVISION=PASS_'+case in run('verify',str(snap),case),case
print('B33_HOST_REVISION_STABILITY=PASS_30_CROSS_PROCESS_CASES_1_ACCEPT_29_DENY_NO_DB')
print('B33_EXTERNAL_CAS_ATOMICITY_AUTH_ESP_NVS=NOT_VERIFIED')
