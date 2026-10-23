#!/usr/bin/env python3
"""Two-round host-only quorum, each mode in a new process, fail-closed."""
import os,shutil,subprocess,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
cc=os.getenv('VG_GCC') or shutil.which('gcc')
assert cc,'GCC_NOT_FOUND'
with tempfile.TemporaryDirectory(prefix='vg_b27_seq_') as d:
    exe=Path(d)/('sequence.exe' if os.name=='nt' else 'sequence')
    f=Path(d)/'checkpoint.bin'
    p=subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
        '-Ifirmware/src','scripts/phase9_b27_quorum_sequence_fixture.c','-o',str(exe)],
        cwd=R,capture_output=True,text=True,timeout=90)
    assert p.returncode==0,(p.stdout,p.stderr)
    def call(*args):
        res=subprocess.run([str(exe),*args],cwd=R,capture_output=True,text=True,timeout=90)
        assert res.returncode==0,(args,res.stdout,res.stderr)
        return res.stdout
    assert 'B27_STAGE=PASS_TWO_SEQUENTIAL_PROPOSALS_NO_TRUST' in call('stage',str(f))
    assert f.stat().st_size>0
    modes=('both_rounds_new','first_old','first_split','first_ack_mismatch',
         'first_gen_mismatch','first_primary_replay','first_secondary_replay',
         'first_primary_skip','first_secondary_skip','first_corrupt_middle',
         'first_corrupt_old','first_bad_ticket','second_old','second_split',
         'second_ack_mismatch','second_gen_mismatch','second_primary_replay',
         'second_secondary_replay','second_primary_skip','second_secondary_skip',
         'second_corrupt_after','second_bad_ticket','second_bad_link',
         'second_bad_expected','wrong_domain','swapped_domains','wrong_tag',
         'round_overflow','first_epoch_overflow','domain_dup')
    for name in modes:
        assert 'B27_SEQUENCE=PASS_'+name in call('verify',str(f),name)
print('B27_HOST_SEQUENCE=PASS_30_CROSS_PROCESS_CASES_1_ACCEPT_29_DENY_NO_DB')
print('B27_EXTERNAL_SOURCE_AUTH_DURABILITY_ESP_NVS=NOT_VERIFIED')
