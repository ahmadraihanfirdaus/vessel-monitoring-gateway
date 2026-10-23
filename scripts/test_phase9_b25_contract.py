#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b25_observation_epoch_host.h').read_text()
c=(R/'scripts/phase9_b25_observation_epoch_fixture.c').read_text()
for marker in ('vg_b25_guard_seed','vg_b25_observe','verified_epoch',
               'guard->last_observation_epoch+UINT64_C(1)',
               'vg_b24_resolve_observation','last_witness.confirmed_ack',
               'candidate.ack.pending','*next=changed','*committed=candidate_committed',
               'EXTERNAL precondition','neither','authenticity'):
    assert marker.lower() in h.lower(),marker
for marker in ('B25_STAGE=PASS_HOST_ABI_UNTRUSTED_FIXTURE',
              'B25_OBSERVATION=PASS_', 'vg_b25_observe('):assert marker in c,marker
for forbidden in ('php artisan','SQLSTATE[','esp_partition_write(','fsync('):
    assert forbidden not in h,forbidden
print('B25_CONTRACT=PASS_EPOCH_BOUNDARY_OUTPUT_ATOMICITY_AND_TRUST_QUALIFICATION')
