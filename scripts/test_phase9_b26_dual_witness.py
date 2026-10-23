#!/usr/bin/env python3
"""Cross-process host fixtures; two sources are synthetic and NOT trusted."""
from pathlib import Path
import os,shutil,subprocess,tempfile
R=Path(__file__).resolve().parents[1]
cc=os.getenv('VG_GCC') or shutil.which('gcc')
assert cc,'GCC_NOT_FOUND'
with tempfile.TemporaryDirectory(prefix='vg_b26_quorum_') as d:
    exe=Path(d)/('quorum.exe' if os.name=='nt' else 'quorum')
    f=Path(d)/'snapshot.bin'
    p=subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
        '-Ifirmware/src','scripts/phase9_b26_dual_witness_fixture.c','-o',str(exe)],
        cwd=R,capture_output=True,text=True,timeout=90)
    assert p.returncode==0,(p.stdout,p.stderr)
    def call(*args):
        p=subprocess.run([str(exe),*args],cwd=R,capture_output=True,text=True,timeout=90)
        assert p.returncode==0,(args,p.stdout,p.stderr)
        return p.stdout
    assert 'B26_STAGE=PASS_HOST_ABI_UNTRUSTED_TWO_SOURCES' in call('stage',str(f))
    assert f.is_file() and f.stat().st_size>0
    cases=('both_old','both_new','disagree_new_old','disagree_old_new',
       'different_ack','different_generation','epoch_a_replay','epoch_b_replay',
       'epoch_a_gap','epoch_b_gap','epoch_a_zero','epoch_b_zero',
       'duplicate_domain','swapped_domains','wrong_domain_a','wrong_domain_b',
       'wrong_tag','bad_candidate','bad_old','bad_receipt','diverged_guard',
       'round_overflow','epoch_overflow','missing_source')
    for name in cases:
        assert 'B26_QUORUM=PASS_'+name in call('verify',str(f),name)
    seed_cases=('seed_same_domain','seed_zero_domain','seed_zero_tag',
        'seed_zero_epoch','seed_overflow_epoch')
    for name in seed_cases:
        s=call('seed',name)
        assert 'B26_QUORUM=PASS_'+name in s
print('B26_HOST_QUORUM=PASS_29_SCENARIOS_2_ACCEPT_27_DENY_CROSS_PROCESS_NO_DB')
print('B26_INDEPENDENT_AUTHENTICATION_DURABILITY_ESP_NVS=NOT_VERIFIED')
