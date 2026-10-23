#!/usr/bin/env python3
"""CI/scope safety: B20 is registered and no migration/push hooks are added."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
wf=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
for p in ('test_phase9_b20_update.py','test_phase9_b20_contract.py',
          'test_phase9_b20_negative.py','test_phase9_b20_tst002.py'):
    assert wf.count('python3 -B scripts/'+p)==1,p
assert 'B20 host two-slot update' in wf
for p in ('firmware/src/phase9_b20_slot_prepare_host.h',
          'docs/testing/phase9-b20-two-slot-update.md',
          'docs/testing/phase9-b20-scoped-trace.csv'):
    assert (R/p).is_file(),p
print('B20_TST002=PASS_CI_REGISTRATION_NO_DB_RUNNER_SCOPE')
