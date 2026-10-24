#!/usr/bin/env python3
"""Only explicit compare-and-swap host contract, fail closed on drift."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b28_revision_fence_host.h').read_text()
c=(R/'scripts/phase9_b28_revision_fence_fixture.c').read_text()
for fragment in ('vg_b28_seed_fence','vg_b28_confirm_with_fence',
        'externally_verified_revision!=fence->revision',
        'guard->accepted_round!=fence->accepted_round',
        'guard->primary.last_observation_epoch!=fence->primary_epoch',
        'guard->secondary.last_observation_epoch!=fence->secondary_epoch',
        'vg_b27_confirm_sequence(', 'vg_b28_seed_fence(&proposed_guard,',
        '*next_guard=proposed_guard','*next_fence=proposed_fence',
        '*restored=proposed_state','*committed=true',
        'An adversary able to roll back BOTH guard and trusted_revision',
        'No ESP32/NVS claim'):
    assert fragment in h,fragment
for fragment in ('B28_FENCE=PASS_','committed=true;',
        'memcmp(&next_guard,&old_guard,sizeof(old_guard))',
        'memcmp(&next_fence,&old_fence,sizeof(old_fence))',
        'vg_b28_confirm_with_fence('):
    assert fragment in c,fragment
for forbidden in ('sqlite3','PDO','mysql_query','esp_partition_write',
                  'fopen(', 'system(', 'fsync('):
    assert forbidden not in h,forbidden
print('B28_CONTRACT=PASS_EXTERNAL_CAS_FENCE_ATOMIC_OUTPUT_NO_DEVICE_TRUST_CLAIM')
