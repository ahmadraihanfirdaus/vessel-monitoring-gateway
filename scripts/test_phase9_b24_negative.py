#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/phase9_b24_witness_receipt_fixture.c').read_text()
h=(R/'firmware/src/phase9_b24_witness_receipt_host.h').read_text()
for key in ('"out_of_order"','"stale"','"future"','"tamper_target"',
            '"tamper_previous"','"tamper_expected"','"tamper_ticket"',
            '"wrong_tag"','"wrong_slot"','"partial"',
            '"rollback_ack"','"wrap_gen"','memcmp(&restored,&unchanged'):
 assert key in s,key
for key in ('candidate_len!=size','target_slot>1u',
            'previous.generation==UINT32_MAX','proposed.confirmed_ack<',
            'recovered.ack.pending','(now_new && newer)','(still_old && !newer)'):
 assert key in h,key
print('B24_NEGATIVE=PASS_12_REJECTED_OR_MISMATCHED_OBSERVATIONS')
