#!/usr/bin/env python3
"""B30 bounded exact checkpoint content binding across independent processes."""
import os,shutil,subprocess,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
cc=os.getenv('VG_GCC') or shutil.which('gcc')
assert cc,'B30_GCC_MISSING'
with tempfile.TemporaryDirectory(prefix='vg_b30_exact_') as tmp:
    exe=Path(tmp)/('b30.exe' if os.name=='nt' else 'b30')
    snapshot=Path(tmp)/'snapshot.bin'
    p=subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
        '-Ifirmware/src','scripts/phase9_b30_exact_readback_fixture.c','-o',str(exe)],
        cwd=R,capture_output=True,text=True,timeout=90)
    assert p.returncode==0,(p.stdout,p.stderr)
    def check(*args):
        run=subprocess.run([str(exe),*args],cwd=R,capture_output=True,text=True,timeout=90)
        assert run.returncode==0,(args,run.stdout,run.stderr)
        return run.stdout
    assert 'B28_STAGE=PASS_TWO_ROUND_CHECKPOINT_FIXTURE' in check('stage',str(snapshot))
    cases=('accept','prepare_old_rev','prepare_corrupt','prepare_bad_ticket',
      'prepare_split','prepare_bad_domain','prepare_old_epoch',
      'no_external_readback','no_external_cas','stale_verified_revision',
      'future_verified_revision','receipt_wrong_revision','receipt_wrong_ack',
      'receipt_wrong_device','receipt_wrong_domain','rb_wrong_device',
      'rb_wrong_revision','rb_wrong_slot','rb_wrong_length','rb_wrong_crc',
      'rb_short_actual','rb_long_actual','rb_changed_body','rb_changed_ack',
      'rb_wrong_generation','rb_wrong_journal',
      'rb_valid_alternate_telemetry','rb_valid_alternate_journal',
      'pending_changed_journal',
      'pending_changed_latest','pending_changed_store_count',
      'pending_wrong_slot','pending_changed_image','pending_not_ready',
      'pending_zero_image_len','pending_overlong_image_len',
      'pending_generation','null_pending','null_cas',
      'null_readback_receipt','null_image','null_output')
    for case in cases:
        assert 'B30_READBACK=PASS_'+case in check('verify',str(snapshot),case),case
print('B30_HOST_EXACT_READBACK=PASS_42_CROSS_PROCESS_CASES_1_ACCEPT_41_DENY_NO_DB')
print('B30_READBACK_AUTH_DURABILITY_ESP_NVS=NOT_VERIFIED')
