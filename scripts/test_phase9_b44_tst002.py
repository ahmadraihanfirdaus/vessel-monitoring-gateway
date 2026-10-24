#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
y=(r/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert y.count('backend-mysql-isolated:')==1
assert y.count('B44 host authenticated nonce ledger snapshot restore')==1
assert y.index('B43 host-only bounded nonce replay denial')<y.index('B44 host authenticated nonce ledger snapshot restore')<y.index('backend-mysql-isolated:')
for name in ('nonce_snapshot','contract','negative','tst002'):
    assert y.count('python3 -B scripts/test_phase9_b44_'+name+'.py')==1,name
assert y.count('mysql:8.0')==1
print('B44_TST002=PASS_HOST_SIGNED_RESTART_SNAPSHOT_MYSQL_CI_SEPARATION')
