#!/usr/bin/env python3
"""B34 host-only envelope publication denial and acknowledgement coherence."""
import os,shutil,subprocess,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
cc=os.getenv('VG_GCC') or shutil.which('gcc')
assert cc,'B34_GCC_MISSING'
cases=(
    'accept',
    'wrong_revision',
    'wrong_ack',
    'wrong_readback',
    'wrong_readback_crc',
    'wrong_readback_len',
    'wrong_device',
    'wrong_domain',
    'wrong_epoch',
    'wrong_slot',
    'no_external_cas',
    'no_external_readback',
    'null_pending',
    'null_cas',
    'null_rr',
    'null_readback',
    'null_probe',
    'null_context',
    'null_output',
    'alias_output_pending',
    'alias_output_cas',
    'alias_output_rr',
    'alias_output_readback',
    'alias_pending_cas',
    'alias_rr_pending',
    'alias_readback_pending',
    'zero_len',
    'overlong_len',
    'probe_first_fail',
    'probe_second_fail',
    'probe_first_wrong_revision',
    'probe_second_wrong_revision',
    'probe_first_mutate_pending',
    'probe_second_mutate_cas',
    'probe_second_mutate_readback',
)
assert len(cases)==35 and len(set(cases))==35
with tempfile.TemporaryDirectory(prefix='vg_b34_envelope_') as td:
    exe=Path(td)/('b34.exe' if os.name=='nt' else 'b34')
    snap=Path(td)/'checkpoint.bin'
    comp=subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
        '-Ifirmware/src','-Iscripts','scripts/phase9_b34_publish_envelope_fixture.c','-o',str(exe)],
        cwd=R,capture_output=True,text=True,timeout=90)
    assert comp.returncode==0,(comp.stdout,comp.stderr)
    def run(*args):
        p=subprocess.run([str(exe),*args],cwd=R,capture_output=True,text=True,timeout=90)
        assert p.returncode==0,(args,p.stdout,p.stderr)
        return p.stdout
    assert 'B28_STAGE=PASS_TWO_ROUND_CHECKPOINT_FIXTURE' in run('stage',str(snap))
    for case in cases:
        assert 'B34_ENVELOPE=PASS_'+case in run('verify',str(snap),case),case
print('B34_HOST_ENVELOPE=PASS_35_CROSS_PROCESS_CASES_1_ACCEPT_34_DENY_NO_DB')
print('B34_ATOMIC_VISIBILITY_AUTHENTICATION_NVS=NOT_VERIFIED')
