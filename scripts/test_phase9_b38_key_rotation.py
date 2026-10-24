#!/usr/bin/env python3
"""Host-only key-rotation policy for B37 authenticated receipt.

Two random 256-bit fixture keys are ephemeral. The 'external' key registry and
counter floor are simulated; they are NOT backed by ESP32 or trusted storage.
"""
from pathlib import Path
import hashlib,hmac,os,secrets,shutil,struct,subprocess,tempfile,zlib
ROOT=Path(__file__).resolve().parents[1]
CC=os.getenv('VG_GCC') or shutil.which('gcc')
assert CC,'B38_GCC_MISSING'
WIRE=struct.Struct('<4s8I4QI');PREFIX=struct.Struct('<4sIQQ')
assert WIRE.size==72 and PREFIX.size==24
DOMAIN=b'VG_PHASE9_B37_HOST_AUTH_V1\x00'
MAX64=(1<<64)-1

def valid_wire(blob):
    if not isinstance(blob,bytes) or len(blob)!=72:return False
    parts=WIRE.unpack(blob)
    return (parts[0]==b'VG35' and parts[1]==1 and parts[2]==72 and
            all(parts[3:13]) and parts[4]!=parts[5] and
            zlib.crc32(blob[:68])==parts[13] and WIRE.pack(*parts)==blob)

def seal(key,key_id,epoch,wire):
    msg=PREFIX.pack(b'VG37',1,key_id,epoch)+wire
    return msg+hmac.new(key,DOMAIN+msg,hashlib.sha256).digest()

# The policy must be sourced from a trusted external authority in production.
# Verification cannot silently fall back to the retired key.
def authorize(blob,expected_wire,policy,keys):
    if not isinstance(blob,bytes) or len(blob)!=128 or not valid_wire(expected_wire):return False
    if not isinstance(policy,dict) or not isinstance(keys,dict):return False
    try:
        active=policy['active_key_id'];retired=policy['retired_key_id']
        floor=policy['exclusive_epoch_floor'];activated=policy['activation_epoch']
        if not all(type(x) is int for x in (active,retired,floor,activated)):return False
        if not (1<=active<=MAX64 and 0<=retired<=MAX64 and retired!=active and
                0<=floor<MAX64 and 1<=activated<=MAX64):return False
        key=keys.get(active)
        if not isinstance(key,bytes) or len(key)!=32:return False
        m,version,kid,epoch=PREFIX.unpack_from(blob)
        if (m!=b'VG37' or version!=1 or kid!=active or kid==retired or
            epoch<activated or epoch<=floor or
            not hmac.compare_digest(blob[24:96],expected_wire)):
            return False
        mac=hmac.new(key,DOMAIN+blob[:96],hashlib.sha256).digest()
        return hmac.compare_digest(blob[96:],mac)
    except (ValueError,TypeError,KeyError,struct.error,OverflowError):return False

def untrusted_precheck(blob,expected_wire,policy):
    if not isinstance(blob,bytes) or len(blob)!=128 or not valid_wire(expected_wire):return False
    if not isinstance(policy,dict):return False
    active=policy.get('active_key_id');retired=policy.get('retired_key_id')
    floor=policy.get('exclusive_epoch_floor');activated=policy.get('activation_epoch')
    if not all(type(x) is int for x in (active,retired,floor,activated)):return False
    if not (1<=active<=MAX64 and 0<=retired<=MAX64 and retired!=active and
            0<=floor<MAX64 and 1<=activated<=MAX64):return False
    try:m,ver,kid,epoch=PREFIX.unpack_from(blob)
    except struct.error:return False
    return (m==b'VG37' and ver==1 and kid==active and kid!=retired and
            epoch>=activated and epoch>floor and
            hmac.compare_digest(blob[24:96],expected_wire) and valid_wire(blob[24:96]))

with tempfile.TemporaryDirectory(prefix='vg_b38_ephemeral_') as folder:
    d=Path(folder);b35=d/('b35.exe' if os.name=='nt' else 'b35')
    b38=d/('b38.exe' if os.name=='nt' else 'b38')
    for src,out in (('scripts/phase9_b35_wire_receipt_fixture.c',b35),
                    ('scripts/phase9_b38_key_rotation_fixture.c',b38)):
        comp=subprocess.run([CC,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
          '-Ifirmware/src','-Iscripts',src,'-o',str(out)],cwd=ROOT,capture_output=True,
          text=True,timeout=90)
        assert comp.returncode==0,(src,comp.stdout,comp.stderr)
    def run(exe,*args):
        proc=subprocess.run([str(exe),*map(str,args)],cwd=ROOT,capture_output=True,text=True,timeout=60)
        assert proc.returncode==0,(args,proc.stdout,proc.stderr)
        return proc.stdout.strip()
    checkpoint=d/'checkpoint.bin';wirefile=d/'wire.bin'
    assert 'PASS_TWO_ROUND_CHECKPOINT_FIXTURE' in run(b35,'stage',checkpoint)
    assert 'PASS_CANONICAL_72_BYTES' in run(b35,'stage',checkpoint,wirefile)
    wire=wirefile.read_bytes();assert valid_wire(wire)
    old_key=secrets.token_bytes(32);new_key=secrets.token_bytes(32)
    while old_key==new_key:new_key=secrets.token_bytes(32)
    wrong_key=secrets.token_bytes(32)
    old={'active_key_id':101,'retired_key_id':0,'activation_epoch':1,'exclusive_epoch_floor':0}
    new={'active_key_id':202,'retired_key_id':101,'activation_epoch':40,'exclusive_epoch_floor':39}
    keyring={101:old_key,202:new_key}
    before=seal(old_key,101,39,wire);after=seal(new_key,202,40,wire)
    assert authorize(before,wire,old,keyring) and authorize(after,wire,new,keyring)
    cases=[('old_before_cutover',before,old,keyring,wire,True,'pre'),
           ('new_after_cutover',after,new,keyring,wire,True,'post')]
    def deny(name,blob=after,policy=new,keys=keyring,expected=wire,stage='post'):
        cases.append((name,blob,policy,keys,expected,False,stage))
    # Old signing key is explicitly retired; never try it as a fallback.
    deny('old_receipt_post_cutover',before)
    deny('old_key_new_epoch',seal(old_key,101,42,wire))
    deny('new_key_before_cutover',seal(new_key,202,39,wire))
    deny('new_signer_with_old_policy',after,old,keyring,wire,'pre')
    deny('new_receipt_replayed_same_epoch',after,{**new,'exclusive_epoch_floor':40})
    deny('new_receipt_before_activation',after,{**new,'activation_epoch':41})
    deny('key_id_downgrade',after,{**new,'active_key_id':101})
    deny('retired_equal_active',after,{**new,'retired_key_id':202})
    deny('zero_active',after,{**new,'active_key_id':0})
    deny('zero_activation',after,{**new,'activation_epoch':0})
    deny('max_floor',after,{**new,'exclusive_epoch_floor':MAX64})
    deny('negative_floor',after,{**new,'exclusive_epoch_floor':-1})
    deny('negative_retired',after,{**new,'retired_key_id':-1})
    deny('wrong_current_secret',after,new,{101:old_key,202:wrong_key})
    deny('key_material_missing',after,new,{101:old_key})
    deny('bad_key_length_short',after,new,{202:new_key[:31]})
    deny('bad_key_length_long',after,new,{202:new_key+b'x'})
    deny('wrong_expected_wire',after,new,keyring,wire[:-1]+bytes([wire[-1]^1]))
    deny('wrong_expected_type',after,new,keyring,None)
    deny('no_payload',b'')
    deny('trailing_byte',after+b'x')
    deny('truncated_mac',after[:-1])
    deny('replaced_key_id',seal(new_key,203,40,wire))
    deny('replayed_old_key_with_valid_new_mac',seal(new_key,101,40,wire))
    deny('future_new_key_wrong_signer',seal(old_key,202,41,wire))
    deny('unsigned_future_epoch',after[:16]+(41).to_bytes(8,'little')+after[24:])
    deny('alternate_active_epoch',seal(new_key,202,39,wire))
    # Satisfy all structural checks while failing cryptographic integrity.
    for offset in (96,97,103,111,120,127):
        blob=bytearray(after);blob[offset]^=1
        deny('mac_mutated_'+str(offset),bytes(blob))
    for offset in (0,4,8,16,24,28,36,52,68,92):
        blob=bytearray(after);blob[offset]^=1
        deny('wire_or_prefix_mutated_'+str(offset),bytes(blob))
    changed=bytearray(wire);changed[52]^=1
    changed[68:72]=struct.pack('<I',zlib.crc32(changed[:68]))
    deny('forged_crc_valid_not_authenticated',seal(old_key,202,40,bytes(changed)))
    deny('hmac_valid_wrong_device',seal(new_key,202,40,bytes(changed)))
    assert len(cases)==47,len(cases)
    structural_false_auth=0
    for name,blob,policy,keys,expected,expected_ok,stage in cases:
        p=d/(name+'.bin');p.write_bytes(blob)
        c99=run(b38,p,wirefile,stage)
        assert c99 in ('B38_STRUCTURAL_ONLY=PASS_NO_AUTH','B38_STRUCTURAL_ONLY=DENIED_NO_AUTH'),(name,c99)
        got=authorize(blob,expected,policy,keys)
        assert got is expected_ok,(name,got,expected_ok)
        # C99's fixture uses predefined PRE/POST policy, independent of Python
        # override states used for cryptographic rejection cases.
        policy_fixture=old if stage=='pre' else new
        structurally_ok=untrusted_precheck(blob,wire,policy_fixture)
        assert (c99=='B38_STRUCTURAL_ONLY=PASS_NO_AUTH')==structurally_ok,(name,c99)
        if not got and structurally_ok:structural_false_auth+=1
    assert structural_false_auth>=6,structural_false_auth
    # No persistent keyring or test key material is written under ROOT.
print('B38_ROTATION=PASS_47_CASES_2_ACCEPT_45_DENY_NO_RETIRED_KEY_FALLBACK')
print('B38_EXTERNAL_TRUSTED_KEYRING_COUNTER_ESP32=NOT_VERIFIED')
