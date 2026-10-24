#!/usr/bin/env python3
"""B32 C99 separate-process four-input full independence test."""
import os,shutil,subprocess,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
cc=os.getenv('VG_GCC') or shutil.which('gcc')
assert cc,'B32_GCC_MISSING'
cases=(
    'accept',
    'alias_cas_pending',
    'alias_rr_pending',
    'alias_rr_cas',
    'alias_cas_rr',
    'alias_pending_cas',
    'alias_pending_rr',
    'alias_readback_pending_image',
    'alias_readback_pending_prefix',
    'alias_readback_cas',
    'alias_readback_rr',
    'alias_guard_pending_guard',
    'alias_state_pending_state',
    'alias_guard_fence',
    'alias_committed_state',
    'no_external_cas',
    'no_external_readback',
    'wrong_revision',
    'wrong_readback',
    'wrong_ack',
    'null_pending',
    'null_cas',
    'null_rr',
    'null_readback',
)
assert len(cases)==24 and len(set(cases))==24
with tempfile.TemporaryDirectory(prefix='vg_b32_input_independent_') as tmp:
    exe=Path(tmp)/('b32.exe' if os.name=='nt' else 'b32')
    snap=Path(tmp)/'snapshot.bin'
    comp=subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
        '-Ifirmware/src','scripts/phase9_b32_input_provenance_fixture.c','-o',str(exe)],
        cwd=R,capture_output=True,text=True,timeout=90)
    assert comp.returncode==0,(comp.stdout,comp.stderr)
    def run(*args):
        p=subprocess.run([str(exe),*args],cwd=R,capture_output=True,text=True,timeout=90)
        assert p.returncode==0,(args,p.stdout,p.stderr)
        return p.stdout
    assert 'B28_STAGE=PASS_TWO_ROUND_CHECKPOINT_FIXTURE' in run('stage',str(snap))
    for case in cases:
        assert 'B32_INPUTS=PASS_'+case in run('verify',str(snap),case),case
print('B32_HOST_INPUT_SEPARATION=PASS_24_CROSS_PROCESS_CASES_1_ACCEPT_23_DENY_NO_DB')
print('B32_INPUT_ADDRESS_INDEPENDENCE_NOT_SOURCE_AUTH_OR_ESP_NVS=NOT_VERIFIED')
