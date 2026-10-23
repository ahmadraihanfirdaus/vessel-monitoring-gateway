#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b27_quorum_sequence_host.h').read_text()
c=(R/'scripts/phase9_b27_quorum_sequence_fixture.c').read_text()
for s in ('vg_b27_confirm_sequence','vg_b26_confirm(before,middle',
    'vg_b26_confirm(middle,after','!first_committed','!second_committed',
    'tickets[0].proposed.generation!=tickets[1].previous.generation',
    'tickets[0].proposed.confirmed_ack!=tickets[1].previous.confirmed_ack',
    'final_guard.accepted_round!=guard->accepted_round+2u',
    '*next=final_guard','*restored=second','*committed=true',
    'EXTERNALLY','No ESP32/NVS/power loss claim'):
    assert s.lower() in h.lower(),s
for s in ('B27_STAGE=PASS_TWO_SEQUENTIAL_PROPOSALS_NO_TRUST','B27_SEQUENCE=PASS_',
    'memcmp(&next,&nx,sizeof(nx))!=0','memcmp(&out,&ox,sizeof(ox))!=0',
    'vg_b27_confirm_sequence('):assert s in c,s
for s in ('SQLSTATE[','php artisan','esp_partition_write(','fsync(','sqlite3'):
    assert s not in h,s
print('B27_CONTRACT=PASS_TWO_ROUND_QUORUM_CHAIN_AND_OUTPUT_ATOMICITY')
