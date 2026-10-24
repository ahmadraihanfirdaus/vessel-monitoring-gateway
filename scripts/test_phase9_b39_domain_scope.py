#!/usr/bin/env python3
"""Independent host Python HMAC domain-scoping oracle with ephemeral keys.

The external registry, device admission and epoch floor are mock policy inputs.
The C99 check is deliberately unauthenticated and cannot authorize an ACK.
"""
from pathlib import Path
import hashlib,hmac,os,secrets,shutil,struct,subprocess,tempfile,zlib

ROOT=Path(__file__).resolve().parents[1]
CC=os.getenv('VG_GCC') or shutil.which('gcc')
assert CC,'B39_GCC_NOT_FOUND'
WIRE=struct.Struct('<4s8I4QI');PREFIX=struct.Struct('<4sIQQ')
assert WIRE.size==72 and PREFIX.size==24
MAX64=(1<<64)-1
KDF_DOMAIN=b'VG_PHASE9_B39_SCOPE_KDF_V1\x00'
AUTH_DOMAIN=b'VG_PHASE9_B39_SCOPE_AUTH_V1\x00'
PURPOSE_RESTORE=1
PURPOSE_PUBLISH=2

def wire_valid(blob):
    if type(blob) is not bytes or len(blob)!=72:return False
    try:p=WIRE.unpack(blob)
    except struct.error:return False
    return (p[0]==b'VG35' and p[1]==1 and p[2]==72 and
            all(p[3:13]) and p[4]!=p[5] and
            zlib.crc32(blob[:68])==p[13] and WIRE.pack(*p)==blob)

def scoped_key(master,key_id,purpose,device_tag):
    assert type(master) is bytes and len(master)==32
    ctx=struct.pack('<IQI',purpose,key_id,device_tag)
    return hmac.new(master,KDF_DOMAIN+ctx,hashlib.sha256).digest()

def seal(master,key_id,epoch,wire,purpose,device_tag):
    msg=PREFIX.pack(b'VG37',1,key_id,epoch)+wire
    ctx=struct.pack('<IQI',purpose,key_id,device_tag)
    mac=hmac.new(scoped_key(master,key_id,purpose,device_tag),AUTH_DOMAIN+ctx+msg,hashlib.sha256).digest()
    return msg+mac

def authorize(blob,expected_wire,policy,keys,caller_purpose,caller_device):
    if type(blob) is not bytes or len(blob)!=128 or not wire_valid(expected_wire):return False
    if type(policy) is not dict or type(keys) is not dict:return False
    try:
        active=policy['active_key_id'];retired=policy['retired_key_id']
        floor=policy['exclusive_epoch_floor'];activated=policy['activation_epoch']
        purpose=policy['purpose_id'];device_tag=policy['device_tag']
        vals=(active,retired,floor,activated,purpose,device_tag,caller_purpose,caller_device)
        if any(type(v) is not int for v in vals):return False
        if not(1<=active<=MAX64 and 0<=retired<=MAX64 and retired!=active and
               0<=floor<MAX64 and 1<=activated<=MAX64 and
               purpose in (1,2) and caller_purpose==purpose and
               1<=device_tag<=0xffffffff and device_tag==caller_device and
               WIRE.unpack(expected_wire)[3]==device_tag):return False
        master=keys.get(active)
        if type(master) is not bytes or len(master)!=32:return False
        magic,version,kid,epoch=PREFIX.unpack_from(blob)
        if magic!=b'VG37' or version!=1 or kid!=active or kid==retired or epoch<=floor or epoch<activated:return False
        if not hmac.compare_digest(blob[24:96],expected_wire):return False
        ctx=struct.pack('<IQI',purpose,active,device_tag)
        mac=hmac.new(scoped_key(master,active,purpose,device_tag),AUTH_DOMAIN+ctx+blob[:96],hashlib.sha256).digest()
        return hmac.compare_digest(mac,blob[96:])
    except (KeyError,TypeError,ValueError,struct.error,OverflowError):return False

def untrusted_precheck(blob,wire,policy,caller_purpose,caller_device):
    if type(blob) is not bytes or len(blob)!=128 or not wire_valid(wire):return False
    if type(policy) is not dict:return False
    try:
        active=policy['active_key_id'];retired=policy['retired_key_id']
        floor=policy['exclusive_epoch_floor'];activated=policy['activation_epoch']
        purpose=policy['purpose_id'];device=policy['device_tag']
        vals=(active,retired,floor,activated,purpose,device,caller_purpose,caller_device)
        if any(type(v) is not int for v in vals):return False
        m,ver,kid,epoch=PREFIX.unpack_from(blob)
        return (m==b'VG37' and ver==1 and kid==active and kid!=retired and
                active!=0 and 0<=retired<=MAX64 and retired!=active and
                activated!=0 and floor<MAX64 and epoch>=activated and epoch>floor and
                purpose in (1,2) and purpose==caller_purpose and device==caller_device and
                device!=0 and device==WIRE.unpack(wire)[3] and
                hmac.compare_digest(blob[24:96],wire))
    except (KeyError,TypeError,ValueError,struct.error):return False

with tempfile.TemporaryDirectory(prefix='vg_b39_scope_') as dir_name:
    d=Path(dir_name)
    exe35=d/('b35.exe' if os.name=='nt' else 'b35')
    exe39=d/('b39.exe' if os.name=='nt' else 'b39')
    for source,exe in (('scripts/phase9_b35_wire_receipt_fixture.c',exe35),
                       ('scripts/phase9_b39_domain_scope_fixture.c',exe39)):
        p=subprocess.run([CC,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
                          '-Ifirmware/src','-Iscripts',source,'-o',str(exe)],
                          cwd=ROOT,capture_output=True,text=True,timeout=90)
        assert p.returncode==0,(source,p.stdout,p.stderr)
    def run(exe,*args):
        result=subprocess.run([str(exe),*map(str,args)],cwd=ROOT,capture_output=True,text=True,timeout=60)
        assert result.returncode==0,(args,result.returncode,result.stdout,result.stderr)
        return result.stdout.strip()
    assert run(exe39,'selftest')=='B39_C99_SCOPE_SELFTEST=PASS_STRUCTURAL_ONLY_NO_AUTH'
    ck=d/'checkpoint.bin';wfile=d/'wire.bin'
    assert 'PASS_TWO_ROUND_CHECKPOINT_FIXTURE' in run(exe35,'stage',ck)
    assert 'PASS_CANONICAL_72_BYTES' in run(exe35,'stage',ck,wfile)
    wire=wfile.read_bytes();assert wire_valid(wire)
    tag=WIRE.unpack(wire)[3]
    old_key=secrets.token_bytes(32);new_key=secrets.token_bytes(32)
    while new_key==old_key:new_key=secrets.token_bytes(32)
    wrong=secrets.token_bytes(32)
    keys={101:old_key,202:new_key}
    old={'active_key_id':101,'retired_key_id':0,'activation_epoch':1,'exclusive_epoch_floor':0,
         'purpose_id':PURPOSE_RESTORE,'device_tag':tag}
    post={'active_key_id':202,'retired_key_id':101,'activation_epoch':40,'exclusive_epoch_floor':39,
          'purpose_id':PURPOSE_RESTORE,'device_tag':tag}
    publish={**post,'purpose_id':PURPOSE_PUBLISH}
    r=seal(new_key,202,40,wire,PURPOSE_RESTORE,tag)
    p=seal(new_key,202,40,wire,PURPOSE_PUBLISH,tag)
    old_blob=seal(old_key,101,39,wire,PURPOSE_RESTORE,tag)
    assert authorize(r,wire,post,keys,1,tag) and authorize(p,wire,publish,keys,2,tag)
    assert r!=p and r[:96]==p[:96]  # MAC binding, not accidental wire difference.
    cases=[('restore_allowed',r,wire,post,keys,1,tag,True,'post'),
           ('publish_allowed',p,wire,publish,keys,2,tag,True,'post')]
    def deny(name,blob=r,wire_=wire,pol=post,keyring=keys,purpose=1,device=tag,stage='post'):
        cases.append((name,blob,wire_,pol,keyring,purpose,device,False,stage))
    deny('purpose_cross_replay_restore_to_publish',r,wire,publish,keys,2,tag)
    deny('purpose_cross_replay_publish_to_restore',p)
    deny('purpose_policy_mismatch',r,wire,post,keys,2,tag)
    deny('device_policy_mismatch',r,wire,{**post,'device_tag':tag+1},keys,1,tag)
    deny('device_caller_mismatch',r,wire,post,keys,1,tag+1)
    deny('purpose_unknown',r,wire,{**post,'purpose_id':3},keys,3,tag)
    deny('purpose_zero',r,wire,{**post,'purpose_id':0},keys,0,tag)
    deny('device_zero',r,wire,{**post,'device_tag':0},keys,1,0)
    deny('retired_after_rotation',old_blob)
    deny('wrong_active_key_id',r,wire,{**post,'active_key_id':101})
    deny('retired_same_as_active',r,wire,{**post,'retired_key_id':202})
    deny('before_activated_epoch',r,wire,{**post,'activation_epoch':41})
    deny('epoch_replayed',r,wire,{**post,'exclusive_epoch_floor':40})
    deny('wrong_master_secret',r,wire,post,{202:wrong})
    deny('retired_master_secret_only',r,wire,post,{101:old_key})
    deny('too_short_secret',r,wire,post,{202:new_key[:-1]})
    deny('too_long_secret',r,wire,post,{202:new_key+b'0'})
    deny('master_string_invalid',r,wire,post,{202:'not secret'})
    deny('master_none_invalid',r,wire,post,{202:None})
    deny('keys_not_dict',r,wire,post,None)
    deny('policy_not_dict',r,wire,None)
    deny('caller_bool_purpose',r,wire,post,keys,True,tag)
    deny('caller_bool_device',r,wire,post,keys,1,True)
    deny('policy_bool_purpose',r,wire,{**post,'purpose_id':True})
    deny('invalid_floor_neg',r,wire,{**post,'exclusive_epoch_floor':-1})
    deny('invalid_floor_max',r,wire,{**post,'exclusive_epoch_floor':MAX64})
    deny('invalid_key_id_zero',r,wire,{**post,'active_key_id':0})
    deny('invalid_activated_zero',r,wire,{**post,'activation_epoch':0})
    deny('wrong_wire',r,wire[:-1]+bytes([wire[-1]^1]))
    deny('wire_none',r,None)
    deny('trailing_byte',r+b'x')
    deny('truncated_mac',r[:-1])
    deny('empty_blob',b'')
    deny('wrong_key_signer',seal(old_key,202,40,wire,1,tag))
    deny('old_domain_hmac',PREFIX.pack(b'VG37',1,202,40)+wire+
         hmac.new(new_key,b'VG_PHASE9_B37_HOST_AUTH_V1\x00'+PREFIX.pack(b'VG37',1,202,40)+wire,hashlib.sha256).digest())
    deny('purpose2_with_domain1_mac',p[:96]+r[96:],wire,publish,keys,2,tag)
    altered=bytearray(wire);altered[52]^=1
    altered[68:72]=struct.pack('<I',zlib.crc32(altered[:68]))
    deny('forged_crc_valid_other_device',seal(new_key,202,40,bytes(altered),1,tag))
    deny('forged_crc_valid_context_tag',seal(new_key,202,40,bytes(altered),1,tag+1))
    deny('unsig_epoch_flip',r[:16]+(41).to_bytes(8,'little')+r[24:])
    for offset in (96,103,119,127):
        blob=bytearray(r);blob[offset]^=0x80
        deny('mac_mutation_'+str(offset),bytes(blob))
    assert len(cases)==45,len(cases)
    structural_ok_without_auth=0
    for name,blob,expected_wire,policy,keyring,purpose,device,expected,stage in cases:
        actual=authorize(blob,expected_wire,policy,keyring,purpose,device)
        assert actual is expected,(name,actual,expected)
        # C99 uses pre/post known test policy, caller scope supplied by fixture.
        path=d/(name+'.bin');path.write_bytes(blob)
        cli_purpose=purpose if type(purpose) is int and 0<=purpose<=2 else 1
        cli_device=device if type(device) is int and 0<=device<=0xffffffff else tag
        cpp=run(exe39,path,wfile,cli_purpose,cli_device,stage)
        assert cpp in ('B39_STRUCTURAL_ONLY=PASS_NO_AUTH','B39_STRUCTURAL_ONLY=DENIED_NO_AUTH'),(name,cpp)
        # Structural precheck needs not match cases with custom simulated external policy;
        # it uses known pre/post mode without keyring or external policy modifications.
        selected=old if stage=='pre' else {**post,'purpose_id':cli_purpose,'device_tag':cli_device}
        expected_structural=untrusted_precheck(blob,wire,selected,cli_purpose,cli_device)
        assert (cpp=='B39_STRUCTURAL_ONLY=PASS_NO_AUTH')==expected_structural,(name,cpp,expected_structural)
        if not actual and expected_structural:structural_ok_without_auth+=1
    assert structural_ok_without_auth>=8,structural_ok_without_auth
print('B39_DOMAIN_SCOPE=PASS_45_CASES_2_ACCEPT_43_DENY_EPHEMERAL_KEYS')
print('B39_C99_STRUCTURAL_PASS_NEVER_AUTHORIZES_ACK=VERIFIED')
print('B39_ESP32_KEY_PROVISIONING_DOMAIN_POLICY_ATOMIC_CAS=NOT_VERIFIED')
