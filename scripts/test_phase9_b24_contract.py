#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b24_witness_receipt_host.h').read_text()
c=(R/'scripts/phase9_b24_witness_receipt_fixture.c').read_text()
for key in ('vg_b24_issue_ticket','vg_b24_resolve_observation',
            'vg_b23_propose_after_readback','vg_b23_restore_witnessed',
            'ticket->candidate_crc32','vg_b18_crc32',
            '*out=recovered;*committed=now_new','!now_new && !still_old',
            'NOT an authenticator','caller MUST verify'):
 assert key.lower() in h.lower(),key
for key in ('B24_STAGE=PASS_TICKET_NOT_COMMITTED','B24_RESOLVE=PASS_',
            'fread(&f,1,sizeof(f),file)','fwrite(&f,1,sizeof(f),file)'):
 assert key in c,key
for unsafe in ('php artisan','SQLSTATE[','fsync(','esp_partition_write('):
 assert unsafe not in h,unsafe
print('B24_CONTRACT=PASS_HOST_RECEIPT_POLICY_AND_EXPLICIT_TRUST_BOUNDARY')
