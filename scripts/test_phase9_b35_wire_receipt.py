#!/usr/bin/env python3
"""Cross-process B35 canonical wire receipt and strict no-write denial matrix."""
import os,shutil,subprocess,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
cc=os.getenv('VG_GCC') or shutil.which('gcc')
assert cc,'B35_GCC_MISSING'
cases=(
    'accept',
    'wrong_magic',
    'wrong_version',
    'wrong_length_field',
    'wrong_device',
    'wrong_primary_domain',
    'wrong_secondary_domain',
    'wrong_generation',
    'wrong_ack',
    'wrong_snapshot_crc',
    'wrong_revision',
    'wrong_round',
    'wrong_primary_epoch',
    'wrong_secondary_epoch',
    'wrong_footer',
    'truncated',
    'trailing',
    'empty',
    'null_raw',
    'null_envelope',
    'null_snapshot',
    'null_dest',
    'zero_snapshot_len',
    'snapshot_mutation',
    'envelope_revision',
    'envelope_ack',
    'envelope_generation',
    'envelope_marker',
    'envelope_domain',
    'envelope_witness',
    'envelope_pending',
    'alias_dest_raw',
    'alias_dest_snapshot',
    'alias_dest_envelope',
    'alias_raw_snapshot',
    'alias_raw_envelope',
    'encode_null_output',
    'encode_tiny_capacity',
    'encode_alias_output_snapshot',
    'encode_alias_written_output',
    'encode_wrong_snapshot',
)
assert len(cases)==41 and len(set(cases))==41
with tempfile.TemporaryDirectory(prefix='vg_b35_wire_') as td:
    exe=Path(td)/('b35.exe' if os.name=='nt' else 'b35')
    snapshot=Path(td)/'fixture.bin'
    receipt=Path(td)/'receipt.bin'
    comp=subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
        '-Ifirmware/src','-Iscripts','scripts/phase9_b35_wire_receipt_fixture.c','-o',str(exe)],
        cwd=R,capture_output=True,text=True,timeout=90)
    assert comp.returncode==0,(comp.stdout,comp.stderr)
    def run(*args):
        result=subprocess.run([str(exe),*args],cwd=R,capture_output=True,text=True,timeout=90)
        assert result.returncode==0,(args,result.stdout,result.stderr)
        return result.stdout
    # Stage B28 fixture in first process; write B35 record in a second.
    assert 'B28_STAGE=PASS_TWO_ROUND_CHECKPOINT_FIXTURE' in run('stage',str(snapshot))
    assert 'B35_STAGE=PASS_CANONICAL_72_BYTES' in run('stage',str(snapshot),str(receipt))
    assert len(receipt.read_bytes())==72
    for case in cases:
        assert 'B35_WIRE=PASS_'+case in run('verify',str(snapshot),str(receipt),case),case
print('B35_WIRE_RECEIPT=PASS_41_CROSS_PROCESS_CASES_1_ACCEPT_40_DENY_NO_DB')
print('B35_CRYPTOGRAPHIC_AUTH_DURABLE_CAS_ESP_NVS=NOT_VERIFIED')
