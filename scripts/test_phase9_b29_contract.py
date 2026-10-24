#!/usr/bin/env python3
"""Host-only staged ACK publication guard and exact external receipt API."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b29_publish_barrier_host.h').read_text()
c=(R/'scripts/phase9_b29_publish_barrier_fixture.c').read_text()
for s in ('vg_b29_prepare(', 'vg_b29_finalize(', 'external_cas_confirmed',
          'vg_b28_confirm_with_fence(', 'receipt->after_revision!=pending->next_fence.revision',
          'externally_verified_after_revision!=pending->next_fence.revision',
          'receipt->witness.confirmed_ack!=pending->next_fence.last_witness.confirmed_ack',
          'pending->next_state.ack.pending', '*published_guard=pending->next_guard',
          '*published_fence=pending->next_fence','*published_state=pending->next_state',
          '*committed=true','Neither authenticates the receipt','ESP32/NVS'):
    assert s in h,s
for s in ('B29_BARRIER=PASS_','memcmp(&published_guard,&guard_original',
          'memcmp(&published_fence,&fence_original',
          'memcmp(&published_state,&state_original','vg_b29_finalize('):
    assert s in c,s
for banned in ('fopen(', 'fsync(', 'mysql', 'PDO', 'esp_partition_write',
               'system(', 'sqlite'):
    assert banned not in h,banned
print('B29_CONTRACT=PASS_PREPARE_UNPUBLISHED_EXTERNAL_CAS_RECEIPT_BOUND_FINALIZE')
