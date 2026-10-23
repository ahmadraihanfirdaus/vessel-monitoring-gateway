#!/usr/bin/env python3
"""Check regression fixture contains all fail-closed injected conditions."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
t=(R/'scripts/test_phase9_b20_update.py').read_text()
c=(R/'scripts/phase9_b20_slot_fixture.c').read_text()
for text in ("('torn',11,1)","('bitflip',11,1)","('good',12,0)",
             'ACTIVE_SLOT_MODIFIED','B20_DISK_ATOMICITY_ESP_NVS_POWERLOSS=NOT_VERIFIED'):
    assert text in t,text
for text in ('UINT32_MAX','ack.last_accepted_sequence=7u','vg_b20_verify_readback',
             'B20_NEGATIVE=PASS_','different','vg_b20_prepare'):
    assert text in c,text
assert 'C:/Users/' not in t
print('B20_NEGATIVE=PASS_TORN_CORRUPT_NO_ROLLBACK_SPLIT_BRAIN_SOURCE')
