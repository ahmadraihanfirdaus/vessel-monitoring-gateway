#!/usr/bin/env python3
"""B31 C99 separate-process publication isolation and mutation regression."""
import os,shutil,subprocess,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
cc=os.getenv('VG_GCC') or shutil.which('gcc')
assert cc,'B31_GCC_MISSING'
cases=('accept',
  'alias_readback_pending_image','alias_readback_pending_prefix',
  'alias_readback_cas','alias_readback_rr',
  'alias_guard_pending_guard','alias_fence_pending_fence',
  'alias_state_pending_state','alias_committed_cas',
  'alias_committed_receipt','alias_guard_fence','alias_state_guard',
  'alias_state_fence','alias_committed_state','alias_state_actual',
  'alias_fence_actual','no_external_cas','no_external_readback',
  'wrong_revision','wrong_readback','wrong_ack','zero_readback_len',
  'overlong_readback_len','null_out_guard','null_out_fence',
  'null_out_state','null_out_committed','null_pending','null_cas',
  'null_rr','null_readback')
assert len(cases)==31 and len(set(cases))==31
with tempfile.TemporaryDirectory(prefix='vg_b31_publish_') as tmp:
    exe=Path(tmp)/('b31.exe' if os.name=='nt' else 'b31')
    snapshot=Path(tmp)/'snapshot.bin'
    comp=subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
        '-Ifirmware/src','scripts/phase9_b31_publish_isolation_fixture.c','-o',str(exe)],
        cwd=R,capture_output=True,text=True,timeout=90)
    assert comp.returncode==0,(comp.stdout,comp.stderr)
    def verify(*args):
        run=subprocess.run([str(exe),*args],cwd=R,capture_output=True,text=True,timeout=90)
        assert run.returncode==0,(args,run.stdout,run.stderr)
        return run.stdout
    assert 'B28_STAGE=PASS_TWO_ROUND_CHECKPOINT_FIXTURE' in verify('stage',str(snapshot))
    for mode in cases:
        assert 'B31_ISOLATION=PASS_'+mode in verify('verify',str(snapshot),mode),mode
print('B31_HOST_PUBLISH_ISOLATION=PASS_31_CROSS_PROCESS_CASES_1_ACCEPT_30_DENY_NO_DB')
print('B31_ADDRESS_SPACE_ISOLATION_NOT_AUTHENTICATION_ESP_NVS=NOT_VERIFIED')
