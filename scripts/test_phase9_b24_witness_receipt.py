#!/usr/bin/env python3
"""Native host process restart; external witness observation is simulated."""
from pathlib import Path
import os,shutil,subprocess,tempfile
R=Path(__file__).resolve().parents[1]
cc=os.getenv('VG_GCC') or shutil.which('gcc')
assert cc,'GCC_NOT_FOUND'
with tempfile.TemporaryDirectory(prefix='vg_b24_receipt_') as d:
    exe=Path(d)/('witness.exe' if os.name=='nt' else 'witness')
    fixture=Path(d)/'staged.bin'
    p=subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
       '-Ifirmware/src','scripts/phase9_b24_witness_receipt_fixture.c','-o',str(exe)],
       cwd=R,text=True,capture_output=True,timeout=90)
    assert p.returncode==0,(p.stdout,p.stderr)
    def run(*args):
        result=subprocess.run([str(exe),*args],cwd=R,capture_output=True,text=True,timeout=90)
        assert result.returncode==0,(args,result.stdout,result.stderr)
        return result.stdout
    assert 'B24_STAGE=PASS_TICKET_NOT_COMMITTED' in run('stage',str(fixture))
    assert fixture.is_file() and fixture.stat().st_size>0
    modes=['old','new','out_of_order','stale','future','tamper_target',
        'tamper_previous','tamper_expected','tamper_ticket','wrong_tag',
        'wrong_slot','partial','rollback_ack','wrap_gen']
    for scenario in modes:
        assert f'B24_RESOLVE=PASS_{scenario}' in run('verify',str(fixture),scenario)
print('B24_HOST_RECEIPT=PASS_14_CROSS_PROCESS_SCENARIOS_OLD_NEW_AND_12_FAIL_CLOSED_NO_DB')
print('B24_EXTERNAL_PERSISTENCE_AUTH_AND_NVS=NOT_VERIFIED')
