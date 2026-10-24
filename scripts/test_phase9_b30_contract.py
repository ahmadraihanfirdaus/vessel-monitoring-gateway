#!/usr/bin/env python3
"""B30 C99 exact snapshot content semantics, no persistence claims."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b30_exact_readback_host.h').read_text()
c=(R/'scripts/phase9_b30_exact_readback_fixture.c').read_text()
for term in ('vg_b30_prepare_exact(', 'vg_b30_finalize_exact(',
             'vg_b29_prepare(', 'vg_b29_finalize(',
             'vg_b19_wrap(', 'vg_b19_decode(',
             'memcmp(encoded,candidate,n)', 'memcmp(readback,pending->image,readback_len)',
             'readback_receipt->image_crc32', 'external_readback_verified',
             'pending->base.next_state', '*published_state=tmp_state',
             'NOT authenticate','ESP32 NVS'):
    assert term in h,term
for term in ('B30_READBACK=PASS_', 'memcmp(&prior_g,&pub_g',
             'memcmp(&prior_f,&pub_f','memcmp(&prior_s,&pub_s',
             'vg_b30_finalize_exact('):
    assert term in c,term
for banned in ('fopen(', 'fsync(', 'mysql', 'PDO', 'esp_partition_write',
               'system(', 'sqlite'):
    assert banned not in h,banned
print('B30_CONTRACT=PASS_EXACT_CANONICAL_IMAGE_READBACK_NO_PARTIAL_PUBLISH')
