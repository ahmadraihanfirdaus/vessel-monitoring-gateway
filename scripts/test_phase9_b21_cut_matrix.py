#!/usr/bin/env python3
"""Run strict C99 exhaustive host fault matrix: no database, no hardware."""
from pathlib import Path
import os,re,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
def main():
    compiler=os.getenv('VG_GCC') or shutil.which('gcc')
    assert compiler,'GCC_NOT_FOUND'
    with tempfile.TemporaryDirectory(prefix='vg_b21_cut_') as td:
        exe=Path(td)/('matrix.exe' if os.name=='nt' else 'matrix')
        c=subprocess.run([compiler,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
           '-Ifirmware/src','scripts/phase9_b21_cut_matrix_fixture.c','-o',str(exe)],
           cwd=ROOT,text=True,capture_output=True,timeout=90)
        assert c.returncode==0,(c.stdout,c.stderr)
        r=subprocess.run([str(exe)],cwd=ROOT,text=True,capture_output=True,timeout=90)
        assert r.returncode==0,(r.stdout,r.stderr)
        m=re.search(r'^B21_MATRIX=PASS_TRUNC_(\d+)_STALE_TAIL_(\d+)_ONE_BIT_(\d+)$',r.stdout,re.M)
        assert m,(r.stdout,r.stderr)
        truncs,tails,flips=map(int,m.groups())
        assert 46<=truncs<=800 and truncs==tails and flips==8*truncs,m.groups()
        assert 'B21_BASELINE=PASS_OLD_GEN11_ACK8_ACTIVE_UNTOUCHED_CANDIDATE_GEN12_ACK9' in r.stdout
        assert 'B21_LIMIT=HOST_MEMORY_FAULT_MODEL_NOT_DISK_ATOMICITY_NVS_POWERLOSS' in r.stdout
        print('B21_HOST_MATRIX=PASS_EXHAUSTIVE_PREFIX_AND_BIT_FLIPS_NO_DB')
        print('B21_CUT_CASES='+str(truncs))
        print('B21_FAULT_CASES='+str(truncs+tails+flips))
        print('B21_FORMAL_DURABILITY=NOT_VERIFIED')
if __name__=='__main__':main()
