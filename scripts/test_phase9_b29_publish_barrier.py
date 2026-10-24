#!/usr/bin/env python3
"""Cross-process host CAS receipt publication barrier, no DB."""
import os,shutil,subprocess,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
cc=os.getenv('VG_GCC') or shutil.which('gcc')
assert cc,'B29_GCC_MISSING'
with tempfile.TemporaryDirectory(prefix='vg_b29_publish_') as temp:
    exe=Path(temp)/('b29.exe' if os.name=='nt' else 'b29')
    snapshot=Path(temp)/'snapshot.bin'
    cmd=[cc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
         '-Ifirmware/src','scripts/phase9_b29_publish_barrier_fixture.c','-o',str(exe)]
    p=subprocess.run(cmd,cwd=R,capture_output=True,text=True,timeout=90)
    assert p.returncode==0,(p.stdout,p.stderr)
    def check(*args):
        p=subprocess.run([str(exe),*args],cwd=R,capture_output=True,text=True,timeout=90)
        assert p.returncode==0,(args,p.stdout,p.stderr)
        return p.stdout
    assert 'B28_STAGE=PASS_TWO_ROUND_CHECKPOINT_FIXTURE' in check('stage',str(snapshot))
    cases=('accept','prepare_stale','prepare_future','prepare_corrupt',
      'prepare_split','prepare_replay','prepare_overflow','missing_cas',
      'stale_after','advanced_after','receipt_old_rev','receipt_future_rev',
      'receipt_wrong_tag','receipt_wrong_primary','receipt_wrong_secondary',
      'receipt_wrong_round','receipt_primary_epoch','receipt_secondary_epoch',
      'receipt_generation','receipt_ack','pending_not_ready','pending_wrong_tag',
      'pending_wrong_domain','pending_next_rev','pending_next_round',
      'pending_next_witness','pending_pending_ack','pending_generation',
      'pending_overflow','duplicate_receipt','null_receipt')
    for case in cases:
        assert 'B29_BARRIER=PASS_'+case in check('verify',str(snapshot),case),case
print('B29_HOST_PUBLISH_BARRIER=PASS_31_CROSS_PROCESS_CASES_1_COMMIT_30_DENY_NO_DB')
print('B29_EXTERNAL_RECEIPT_AUTH_CAS_DURABILITY_ESP_NVS=NOT_VERIFIED')
