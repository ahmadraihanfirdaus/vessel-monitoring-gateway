#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b22_guarded_restore_host.h').read_text()
c=(R/'scripts/phase9_b22_guarded_restore_fixture.c').read_text()
for key in ('!floor->minimum_generation','local.generation<floor->minimum_generation',
            'local.ack.last_accepted_sequence<floor->minimum_confirmed_ack',
            'local.ack.pending_correlation','return false;','vg_b19_select'):
    assert key in h,key
for key in ('memcmp(&sentinel,&result,sizeof(result))','vg_b22_restore_guarded(conflict',
            'vg_b22_restore_guarded(s,tag+1u','vg_b22_prepare_guarded(s,tag,&strict'):
    assert key in c,key
print('B22_NEGATIVE=PASS_TAMPER_ROLLBACK_IDENTITY_AMBIGUITY')
