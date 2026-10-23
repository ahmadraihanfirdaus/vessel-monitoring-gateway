#!/usr/bin/env python3
"""B18 GitHub workflow policy: pure host fixture, no MySQL connections."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]
w=(r/'.github/workflows/phase9-multi-context-ci.yml').read_text()
step=w.split('B18 host restart snapshot',1)
assert len(step)==2
block=step[1].split('backend-mysql-isolated:',1)[0]
assert 'scripts/test_phase9_b18_checkpoint.py' in block
assert 'scripts/test_phase9_b18_contract.py' in block
assert 'scripts/test_phase9_b18_negative.py' in block
assert 'scripts/test_phase9_b18_tst002.py' not in block or block.count('scripts/test_phase9_b18_tst002.py')==1
assert not any(p in block for p in ('migrate','sqlite','mysql','git push','curl','php artisan'))
print('B18_TST002=PASS_HOST_ONLY_JOB_NO_DB_NO_PUSH')
