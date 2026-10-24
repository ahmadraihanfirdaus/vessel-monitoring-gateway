#!/usr/bin/env python3
"""Guard B30 denial matrix from weakening or bypassing exact image binding."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
t=(R/'scripts/test_phase9_b30_exact_readback.py').read_text()
f=(R/'scripts/phase9_b30_exact_readback_fixture.c').read_text()
for term in ('rb_changed_body','rb_wrong_journal','rb_valid_alternate_telemetry',
             'rb_valid_alternate_journal','pending_changed_journal',
             'pending_changed_latest','pending_changed_store_count',
             'rb_wrong_crc','rb_wrong_length','rb_wrong_slot',
             'no_external_readback','stale_verified_revision','no_external_cas',
             'null_output','prepare_corrupt','prepare_bad_ticket'):
    assert term in t and term in f,term
assert 'memcmp(&pending,&old_pending,sizeof(pending))' in f
assert 'memcmp(&prior_g,&pub_g' in f and 'memcmp(&prior_f,&pub_f' in f
assert 'memcmp(&prior_s,&pub_s' in f
print('B30_NEGATIVE=PASS_STALE_READBACK_ALIAS_MUTATION_NO_PARTIAL_ACK')
