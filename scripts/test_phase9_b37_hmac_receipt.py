#!/usr/bin/env python3
"""Host-only HMAC-sealed VG35 receipt; independent C99 structural peek.

Ephemeral test secret is never written to the repository or evidence.
No authenticated device storage, hardware key, TLS or ESP32 functionality.
"""
import hashlib,hmac,os,secrets,shutil,struct,subprocess,tempfile,zlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
CC=os.getenv('VG_GCC') or shutil.which('gcc')
assert CC,'B37_GCC_MISSING'
PRELUDE=struct.Struct('<4sIQQ');INNER=struct.Struct('<4s8I4QI')
assert PRELUDE.size==24 and INNER.size==72
LENGTH=128
LABEL=b'VG_PHASE9_B37_HOST_AUTH_V1\x00'

def canonical_wire(data):
    if len(data)!=72:return False
    fields=INNER.unpack(data)
    magic,version,length,device,da,db,gen,ack,crc,revision,round_,ep1,ep2,footer=fields
    return (magic==b'VG35' and version==1 and length==72 and
      all((device,da,db,gen,ack,revision,round_,ep1,ep2)) and da!=db and
      footer==zlib.crc32(data[:68]) and INNER.pack(*fields)==data)

def seal(key,key_id,epoch,wire):
    msg=PRELUDE.pack(b'VG37',1,key_id,epoch)+wire
    return msg+hmac.new(key,LABEL+msg,hashlib.sha256).digest()

def verify(key,key_id,min_exclusive_epoch,expected_wire,blob):
    if not isinstance(blob,bytes) or len(blob)!=LENGTH or not canonical_wire(expected_wire):return False
    if not isinstance(key,bytes) or len(key)!=32 or not isinstance(key_id,int) or key_id<=0:return False
    if not isinstance(min_exclusive_epoch,int) or min_exclusive_epoch<0:return False
    magic,version,kid,epoch=PRELUDE.unpack_from(blob,0)
    if (magic!=b'VG37' or version!=1 or kid!=key_id or epoch<=min_exclusive_epoch or
        not hmac.compare_digest(blob[24:96],expected_wire)):
        return False
    expected=hmac.new(key,LABEL+blob[:96],hashlib.sha256).digest()
    return hmac.compare_digest(blob[96:],expected)

with tempfile.TemporaryDirectory(prefix='vg_b37_ephemeral_') as folder:
    d=Path(folder);exe=d/('b37.exe' if os.name=='nt' else 'b37')
    b35=d/('b35.exe' if os.name=='nt' else 'b35')
    for source,out in [('scripts/phase9_b37_hmac_receipt_fixture.c',exe),
                       ('scripts/phase9_b35_wire_receipt_fixture.c',b35)]:
        cp=subprocess.run([CC,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
              '-Ifirmware/src','-Iscripts',source,'-o',str(out)],cwd=R,
              capture_output=True,text=True,timeout=90)
        assert cp.returncode==0,(source,cp.stdout,cp.stderr)
    def run(executable,*argv):
        proc=subprocess.run([str(executable),*map(str,argv)],cwd=R,
                            capture_output=True,text=True,timeout=60)
        assert proc.returncode==0,(argv,proc.stdout,proc.stderr)
        return proc.stdout.strip()
    chk=d/'checkpoint.bin';wire_path=d/'VG35.bin'
    assert 'PASS_TWO_ROUND_CHECKPOINT_FIXTURE' in run(b35,'stage',chk)
    assert 'PASS_CANONICAL_72_BYTES' in run(b35,'stage',chk,wire_path)
    wire=wire_path.read_bytes();assert canonical_wire(wire)
    key=secrets.token_bytes(32);wrong=secrets.token_bytes(32)
    key_id=0x1122334455667788;epoch=37;floor=36
    valid=seal(key,key_id,epoch,wire)
    assert len(valid)==128 and verify(key,key_id,floor,wire,valid)
    cases=[('accept',valid,key,key_id,floor,wire,True)]
    def deny(name,b, k=key, kid=key_id, f=floor, w=wire):
        cases.append((name,b,k,kid,f,w,False))
    for offset,name in [(0,'magic'),(4,'version'),(8,'keyid'),(16,'epoch'),
           (24,'wire_magic'),(28,'wire_version'),(32,'wire_length'),
           (36,'wire_device'),(40,'wire_primary'),(44,'wire_secondary'),
           (48,'wire_generation'),(52,'wire_ack'),(56,'wire_snapshot_crc'),
           (60,'wire_revision'),(68,'wire_round'),(76,'wire_primary_epoch'),
           (84,'wire_secondary_epoch'),(92,'wire_crc'),(96,'mac_begin'),
           (111,'mac_middle'),(127,'mac_end')]:
        b=bytearray(valid);b[offset]^=1;deny(name,bytes(b))
    # A structurally valid but unsigned mutation of the inner record.
    forged_wire=bytearray(wire);forged_wire[52]^=1
    struct.pack_into('<I',forged_wire,68,zlib.crc32(forged_wire[:68]))
    forged=valid[:24]+bytes(forged_wire)+valid[96:]
    deny('rebuilt_crc_unsigned_forgery',forged)
    # A valid HMAC for another device audience, epoch, or active identity.
    alternate=bytearray(wire);alternate[36]^=2
    struct.pack_into('<I',alternate,68,zlib.crc32(alternate[:68]))
    deny('valid_hmac_wrong_device',seal(key,key_id,epoch,bytes(alternate)))
    deny('valid_hmac_wrong_keyid',seal(key,key_id+1,epoch,wire))
    deny('valid_hmac_stale_epoch',seal(key,key_id,floor,wire))
    deny('valid_hmac_future_from_other_key',seal(wrong,key_id,epoch+1,wire))
    deny('wrong_active_key',valid,k=wrong)
    deny('wrong_expected_id',valid,kid=key_id+1)
    deny('epoch_replay_floor',valid,f=epoch)
    deny('replaced_expected_wire',valid,w=bytes(alternate))
    deny('prefix_truncated',valid[:24]);deny('no_mac',valid[:96])
    deny('trailing_byte',valid+b'X');deny('empty',b'')
    # Recomputing CRC never grants authentication, even when prefix is valid.
    deny('malformed_crc_rebuilt_unsigned',valid[:24]+bytes(forged_wire)+bytes(32))
    assert len(cases)==36,len(cases)
    structural_with_invalid_auth=0
    for name,blob,k,kid,fl,w,expect in cases:
        path=d/(name+'.seal');path.write_bytes(blob)
        structural=run(exe,path,wire_path)
        assert structural in ('B37_STRUCTURAL_ONLY=PASS_NO_AUTH',
                              'B37_STRUCTURAL_ONLY=DENIED_NO_AUTH'),(name,structural)
        got=verify(k,kid,fl,w,blob)
        assert got is expect,(name,got,expect)
        if not got and structural=='B37_STRUCTURAL_ONLY=PASS_NO_AUTH':
            structural_with_invalid_auth+=1
    assert structural_with_invalid_auth>=5,structural_with_invalid_auth
    assert verify(key,key_id,floor,wire,valid)
    # Do not persist/copy key; all signed bytes stay in temporary folder.
print('B37_HMAC=PASS_36_HOST_CASES_1_ACCEPT_35_DENY_EPHEMERAL_KEY')
print('B37_KEY_PROVISIONING_COUNTER_PERSISTENCE_ESP32=NOT_VERIFIED')
