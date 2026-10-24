#!/usr/bin/env python3
"""CAS-fence host C99 tests: cross-process checkpoint, positive + denials."""
import os,shutil,subprocess,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
cc=os.getenv('VG_GCC') or shutil.which('gcc')
assert cc,'B28_GCC_NOT_FOUND'
with tempfile.TemporaryDirectory(prefix='vg_b28_fence_') as tmp:
    exe=Path(tmp)/('fence.exe' if os.name=='nt' else 'fence')
    checkpoint=Path(tmp)/'checkpoint.bin'
    result=subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror',
        '-pedantic','-Ifirmware/src','scripts/phase9_b28_revision_fence_fixture.c',
        '-o',str(exe)],cwd=R,capture_output=True,text=True,timeout=90)
    assert result.returncode==0,(result.stdout,result.stderr)
    def run(*args):
        r=subprocess.run([str(exe),*args],cwd=R,capture_output=True,text=True,timeout=90)
        assert r.returncode==0,(args,r.stdout,r.stderr)
        return r.stdout
    assert 'B28_STAGE=PASS_TWO_ROUND_CHECKPOINT_FIXTURE' in run('stage',str(checkpoint))
    assert checkpoint.stat().st_size>0
    cases=('accept','stale_observed','future_observed','fence_revision_zero',
        'fence_revision_overflow','fence_wrong_tag','fence_wrong_primary',
        'fence_wrong_secondary','fence_round_ahead','fence_primary_epoch',
        'fence_secondary_epoch','fence_generation','fence_ack',
        'guard_primary_epoch','guard_secondary_epoch','guard_primary_witness',
        'guard_secondary_witness','guard_round','guard_round_overflow',
        'first_primary_replay','second_secondary_replay','first_split',
        'second_split','corrupt_after','corrupt_expected','wrong_ticket',
        'domain_collision','swap_domains','wrong_device','alias_fence',
        'alias_guard')
    for case in cases:
        assert 'B28_FENCE=PASS_'+case in run('verify',str(checkpoint),case),case
print('B28_HOST_REVISION_FENCE=PASS_31_CROSS_PROCESS_CASES_1_ACCEPT_30_DENY_NO_DB')
print('B28_EXTERNAL_CAS_AUTH_PERSISTENCE_ESP_NVS=NOT_VERIFIED')
