#!/usr/bin/env python3
"""Independent Python struct/zlib oracle for the C99 B35 wire format."""
import os,shutil,struct,subprocess,tempfile,zlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
CC=os.getenv('VG_GCC') or shutil.which('gcc')
assert CC,'B36_GCC_MISSING'
PACK=struct.Struct('<4s8I4QI')
assert PACK.size==72

def reference_parse(raw):
    if len(raw)!=72:return None
    fields=PACK.unpack(raw)
    magic,version,length,device,a,b,generation,ack,snapshot_crc,revision,round_,ep1,ep2,footer=fields
    if magic!=b'VG35' or version!=1 or length!=72 or \
       footer!=zlib.crc32(raw[:68]) or not all((device,a,b,generation,ack,revision,round_,ep1,ep2)) or a==b:
        return None
    if PACK.pack(*fields)!=raw:return None
    return fields

def repair_crc(raw):
    mutable=bytearray(raw)
    struct.pack_into('<I',mutable,68,zlib.crc32(mutable[:68]))
    return bytes(mutable)

with tempfile.TemporaryDirectory(prefix='vg_b36_wire_interop_') as d:
    root=Path(d);exe=root/('interop.exe' if os.name=='nt' else 'interop')
    cp=subprocess.run([CC,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
      '-Ifirmware/src','-Iscripts','scripts/phase9_b36_wire_interop_fixture.c','-o',str(exe)],
      cwd=R,capture_output=True,text=True,timeout=90)
    assert cp.returncode==0,(cp.stdout,cp.stderr)
    def run(*argv):
        p=subprocess.run([str(exe),*map(str,argv)],cwd=R,capture_output=True,text=True,timeout=90)
        assert p.returncode==0,(argv,p.stdout,p.stderr)
        return p.stdout
    b35exe=root/('b35.exe' if os.name=='nt' else 'b35')
    cp35=subprocess.run([CC,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
       '-Ifirmware/src','-Iscripts','scripts/phase9_b35_wire_receipt_fixture.c','-o',str(b35exe)],
       cwd=R,capture_output=True,text=True,timeout=90)
    assert cp35.returncode==0,(cp35.stdout,cp35.stderr)
    def run35(*argv):
        p=subprocess.run([str(b35exe),*map(str,argv)],cwd=R,capture_output=True,text=True,timeout=90)
        assert p.returncode==0,(argv,p.stdout,p.stderr)
        return p.stdout
    checkpoint=root/'checkpoint.bin';wire=root/'receipt.bin'
    assert 'B28_STAGE=PASS_TWO_ROUND_CHECKPOINT_FIXTURE' in run35('stage',checkpoint)
    assert 'B35_STAGE=PASS_CANONICAL_72_BYTES' in run35('stage',checkpoint,wire)
    assert 'B35_WIRE=PASS_accept' in run35('verify',checkpoint,wire,'accept')
    original=wire.read_bytes();fields=reference_parse(original)
    assert fields and fields[6]==13 and fields[7]==10 and fields[9]==101 and fields[10]==2
    assert fields[11]==43 and fields[12]==73
    cases={'accept':original}
    # Format/length/non-canonical cases and different verified metadata.
    for off,name in ((0,'magic'),(4,'version'),(8,'length'),(12,'device'),
       (16,'primary_domain'),(20,'secondary_domain'),(24,'generation'),
       (28,'ack'),(32,'snapshot_crc'),(36,'revision'),(44,'round'),
       (52,'primary_epoch'),(60,'secondary_epoch')):
        b=bytearray(original);b[off]^=1;cases[name]=repair_crc(b)
    cases['footer']=original[:68]+bytes([original[68]^1])+original[69:]
    cases['empty']=b'';cases['truncated']=original[:-1]
    cases['truncated_half']=original[:36];cases['trailing']=original+b'X'
    cases['reversed_endian']=original[:24]+original[24:28][::-1]+original[28:]
    cases['zero_device']=repair_crc(original[:12]+bytes(4)+original[16:])
    cases['duplicate_domain']=repair_crc(original[:20]+original[16:20]+original[24:])
    cases['zero_revision']=repair_crc(original[:36]+bytes(8)+original[44:])
    cases['zero_epoch']=repair_crc(original[:52]+bytes(8)+original[60:])
    cases['stale_ack_valid_crc']=repair_crc(original[:28]+struct.pack('<I',9)+original[32:])
    cases['future_generation_valid_crc']=repair_crc(original[:24]+struct.pack('<I',14)+original[28:])
    assert len(cases)==26 and len(set(cases))==26
    for name,raw in cases.items():
        receipt=root/(name+'.bin');receipt.write_bytes(raw)
        accepted=name=='accept'
        observed=reference_parse(raw)
        if accepted:assert observed==fields,name
        else:assert observed is None or observed!=fields,name
        assert 'B36_WIRE=PASS_'+('accept' if accepted else 'deny') in run('check',wire,receipt,'accept' if accepted else 'deny'),name
print('B36_INTEROP=PASS_26_CROSS_PROCESS_1_ACCEPT_25_DENY_INDEPENDENT_PYTHON_ZLIB_NO_DB')
print('B36_CRC_AUTHENTICATION_ESP_NVS=NOT_VERIFIED')
