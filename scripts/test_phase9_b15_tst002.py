"""Check source-integrated CI coverage and disallow accidental DB writes in new job."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ci=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
for token in ['test_phase9_b15_contract.py','test_phase9_b15_tst002.py',
              'phase9_b15_event_bridge.py','Phase9B15JournalWireHttpTest']:
    assert token in ci,token
job=ci[ci.index('  backend-http-no-db-b9:'):]
assert 'VG_B15_EVENT_JSONL' in job and 'VG_B14_WIRE_JSONL' in job
assert 'artisan migrate' not in job and 'DB_PORT: \'1\'' in job
print('B15_TST002=PASS_CI_REAL_JOURNAL_NO_DB')
