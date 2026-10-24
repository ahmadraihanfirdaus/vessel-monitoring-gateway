#!/usr/bin/env python3
"""B43 independent Python HMAC oracle + isolated-process C99 bounded nonce ledger."""
from pathlib import Path
import hashlib,hmac,os,secrets,shutil,struct,subprocess,tempfile,zlib
ROOT=Path(__file__).resolve().parents[1]
CC=os.getenv('VG_GCC') or shutil.which('gcc')
assert CC,'B43_GCC_NOT_FOUND'
WIRE=struct.Struct('<4s8I4QI')
KDF=b'VG_PHASE9_B39_SCOPE_KDF_V1\x00'
AUTH=b'VG_PHASE9_B39_SCOPE_AUTH_V1\x00'
CHALLENGE=b'VG_PHASE9_B42_CHALLENGE_AUTH_V1\x00'
def sealed_receipt(master,wire,purpose,device):
    ctx=struct.pack('<IQI',purpose,202,device)
    scoped=hmac.new(master,KDF+ctx,hashlib.sha256).digest()
    body=struct.pack('<4sIQQ',b'VG37',1,202,40)+wire
    assert len(body)==96
    return body+hmac.new(scoped,AUTH+ctx+body,hashlib.sha256).digest()
def proof(master,nonce,receipt,wire,purpose,device):
    data=nonce+receipt+wire+struct.pack('<QQIIQ',12,777,purpose,device,40)
    assert len(data)==248
    return hmac.new(master,CHALLENGE+data,hashlib.sha256).digest()
with tempfile.TemporaryDirectory(prefix='vg_b43_') as temp:
    d=Path(temp);ext='.exe' if os.name=='nt' else ''
    for src,name in [('phase9_b35_wire_receipt_fixture.c','c35'),
                     ('phase9_b43_nonce_ledger_fixture.c','c43')]:
        cp=subprocess.run([CC,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
            '-Ifirmware/src','scripts/'+src,'-o',str(d/(name+ext))],cwd=ROOT,
            capture_output=True,text=True,timeout=90)
        assert cp.returncode==0,(src,cp.stderr)
    def invoke(exe,*argv):
        cp=subprocess.run([str(exe),*map(str,argv)],cwd=ROOT,capture_output=True,
                          text=True,timeout=90)
        assert cp.returncode==0,(argv,cp.stdout,cp.stderr,cp.returncode)
        return cp.stdout.strip()
    snapshot=d/'checkpoint.bin';wirefile=d/'wire.bin'
    assert 'PASS_TWO_ROUND_CHECKPOINT_FIXTURE' in invoke(d/('c35'+ext),'stage',snapshot)
    assert 'PASS_CANONICAL_72_BYTES' in invoke(d/('c35'+ext),'stage',snapshot,wirefile)
    wire=wirefile.read_bytes();assert len(wire)==72
    assert zlib.crc32(wire[:68])==WIRE.unpack(wire)[13]
    device=WIRE.unpack(wire)[3]
    master=secrets.token_bytes(32)
    nonce=secrets.token_bytes(16)
    while not any(nonce):nonce=secrets.token_bytes(16)
    receipt=sealed_receipt(master,wire,1,device)
    mac=proof(master,nonce,receipt,wire,1,device)
    cases=[]
    def add(name,accepted,*,key=master,sealed=receipt,issued=nonce,echo=nonce,
            signature=mac,purpose=1,dev=device,post_revision=12,
            revision_floor=11,source=777,mode='first',marker=None):
        cases.append((name,accepted,key,sealed,issued,echo,signature,purpose,dev,
                      post_revision,revision_floor,source,mode,marker))
    accept_modes={'first':'ACCEPT','replay':'REPLAY_DENIED',
                  'replay-after-denial':'REPLAY_DENIED','alias':'ALIAS_DENIED',
                  'ledger-corrupt':'CORRUPT_DENIED','exhaust':'EXHAUST_DENIED',
                  'alias-input':'ALIAS_DENIED'}
    for mode,marker in accept_modes.items():add('valid_'+mode,True,mode=mode,marker=marker)
    for i in range(16):
        changed=bytearray(nonce);changed[i]^=0x80
        add('nonce_bit_'+str(i),False,issued=bytes(changed),echo=bytes(changed))
    for i in (0,1,8,15,16,23,31):
        changed=bytearray(mac);changed[i]^=0x40
        add('proof_bit_'+str(i),False,signature=bytes(changed))
    add('wrong_key',False,key=secrets.token_bytes(32))
    add('zero_nonce',False,issued=bytes(16),echo=bytes(16))
    add('echo_mismatch',False,echo=secrets.token_bytes(16))
    add('post_revision_changed',False,post_revision=13)
    add('revision_floor_stale',False,revision_floor=12)
    add('wrong_source',False,source=778)
    add('wrong_purpose',False,purpose=2)
    add('wrong_device',False,dev=device+1)
    add('damaged_seal',False,sealed=receipt[:5]+bytes([receipt[5]^1])+receipt[6:])
    add('zero_hmac',False,signature=bytes(32))
    add('nonce_changed_keep_echo',False,issued=secrets.token_bytes(16))
    accepted=sum(case[1] for case in cases)
    assert accepted==7,(len(cases),accepted)
    for i,(name,expect,key,sealed,issued,echo,signature,purpose,dev,rev,floor,source,mode,marker) in enumerate(cases):
        files=[]
        for label,data in [('key',key),('sealed',sealed),('nonce',issued),
                           ('echo',echo),('proof',signature)]:
            path=d/f'{i}_{label}.bin';path.write_bytes(data);files.append(path)
        out=invoke(d/('c43'+ext),files[0],files[1],wirefile,files[2],files[3],
                   files[4],purpose,dev,rev,floor,source,mode,
                   'accept' if expect else 'deny')
        expected_marker=f'B43_LEDGER={marker}_TEST_ONLY' if expect else 'B43_LEDGER=DENIED_TEST_ONLY'
        assert out==expected_marker,(name,out,expected_marker)
print(f'B43_NONCE_LEDGER=PASS_{len(cases)}_CROSS_PROCESS_{accepted}_VALID_{len(cases)-accepted}_DENY_NO_DB')
print('B43_REPLAY_SAME_PROCESS_BOUNDED_FAIL_CLOSED=VERIFIED')
print('B43_DURABLE_NONCE_REPLAY_CAS_THREAD_SAFETY_ESP32=NOT_VERIFIED')
