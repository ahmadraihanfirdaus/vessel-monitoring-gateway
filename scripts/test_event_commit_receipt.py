"""Actual C receipt verification vs Python SHA256/HMAC; no DB or SDK runtime claim."""
import hashlib
import hmac
from pathlib import Path
import unittest
from phase9_b4_testlib import compile_c

ROOT = Path(__file__).resolve().parents[1]


def c_bytes(value):
    return ','.join(str(byte) for byte in value)


class EventCommitReceiptTest(unittest.TestCase):
    def c(self, tail, key_length=64, body=b'{"device_id":"receipt:demo","event_id":1}', status=201, extra=''):
        # Explicit public synthetic test bytes, never a local profile/credential.
        key = bytes((i*7+11) % 256 for i in range(key_length))
        digest = hashlib.sha256(body).hexdigest()
        mac = hmac.new(key, ('VG_EVENT_COMMIT_V1\n'+str(status)+'\n'+digest).encode(), hashlib.sha256).hexdigest()
        receipt = ('VGR1:'+digest+':'+mac).encode()
        setup = '''#include "event_receipt_native_crypto.h"
static uint8_t key[]={KEY},body[]={BODY},receipt[]={RECEIPT};
static uint8_t expected[]={DIGEST},out[32],sentinel[32];
EXTRA
int main(void){
vg_receipt_crypto crypto=vg_receipt_native_provider();
memset(out,0x5a,sizeof(out));memcpy(sentinel,out,32);
(void)expected;(void)key;(void)body;(void)receipt;(void)crypto;
'''.replace('KEY', c_bytes(key)).replace('BODY', c_bytes(body)).replace('RECEIPT', c_bytes(receipt))
        setup = setup.replace('DIGEST', c_bytes(bytes.fromhex(digest))).replace('EXTRA', extra)
        return compile_c(setup+tail+'\nreturn 0;}\n', extra_flags=('-Os', '-I', str(ROOT/'scripts')))

    def test_independent_hmac_oracle_including_long_bearers_and_body_boundaries(self):
        for size in (32, 64, 65, 128, 256):
            for status in (200, 201):
                self.c('assert(vg_event_receipt_verify(&crypto,key,sizeof(key),body,sizeof(body),'+str(status)+',receipt,sizeof(receipt),out));assert(memcmp(out,expected,32)==0);', key_length=size, status=status)
        for body in (b'x', b'x'*4096):
            self.c('assert(vg_event_receipt_verify(&crypto,key,sizeof(key),body,sizeof(body),201,receipt,sizeof(receipt),out));assert(memcmp(out,expected,32)==0);', body=body)

    def test_every_receipt_byte_tamper_refuses_without_output_mutation(self):
        self.c(r'''
for(size_t i=0;i<sizeof(receipt);i++){
receipt[i]^=1;
assert(!vg_event_receipt_verify(&crypto,key,sizeof(key),body,sizeof(body),201,receipt,sizeof(receipt),out));
assert(memcmp(out,sentinel,32)==0);receipt[i]^=1;
}
''')

    def test_truncation_extra_bytes_bad_status_key_size_and_hex_fail_closed(self):
        self.c(r'''
for(size_t n=0;n<sizeof(receipt);n++){
assert(!vg_event_receipt_verify(&crypto,key,sizeof(key),body,sizeof(body),201,receipt,n,out));
assert(memcmp(out,sentinel,32)==0);
}
uint8_t longer[135];memcpy(longer,receipt,sizeof(receipt));longer[134]='\n';
assert(!vg_event_receipt_verify(&crypto,key,sizeof(key),body,sizeof(body),201,longer,sizeof(longer),out));
for(int status=0;status<600;status++)if(status!=200&&status!=201)
assert(!vg_event_receipt_verify(&crypto,key,sizeof(key),body,sizeof(body),status,receipt,sizeof(receipt),out));
assert(!vg_event_receipt_verify(&crypto,key,31,body,sizeof(body),201,receipt,sizeof(receipt),out));
assert(!vg_event_receipt_verify(&crypto,key,257,body,sizeof(body),201,receipt,sizeof(receipt),out));
receipt[70]='A';assert(!vg_event_receipt_verify(&crypto,key,sizeof(key),body,sizeof(body),201,receipt,sizeof(receipt),out));
assert(memcmp(out,sentinel,32)==0);
''')

    def test_wrong_key_body_or_success_status_cannot_authorize(self):
        self.c(r'''
key[0]^=1;assert(!vg_event_receipt_verify(&crypto,key,sizeof(key),body,sizeof(body),201,receipt,sizeof(receipt),out));key[0]^=1;
body[0]^=1;assert(!vg_event_receipt_verify(&crypto,key,sizeof(key),body,sizeof(body),201,receipt,sizeof(receipt),out));body[0]^=1;
assert(!vg_event_receipt_verify(&crypto,key,sizeof(key),body,sizeof(body),200,receipt,sizeof(receipt),out));
assert(memcmp(out,sentinel,32)==0);
''')

    def test_alias_and_null_output_cannot_mutate_key_body_or_envelope(self):
        self.c(r'''
uint8_t saved_key[sizeof(key)],saved_body[sizeof(body)],saved_receipt[sizeof(receipt)];
memcpy(saved_key,key,sizeof(key));memcpy(saved_body,body,sizeof(body));memcpy(saved_receipt,receipt,sizeof(receipt));
assert(!vg_event_receipt_verify(&crypto,key,sizeof(key),body,sizeof(body),201,receipt,sizeof(receipt),key));
assert(!vg_event_receipt_verify(&crypto,key,sizeof(key),body,sizeof(body),201,receipt,sizeof(receipt),body));
assert(!vg_event_receipt_verify(&crypto,key,sizeof(key),body,sizeof(body),201,receipt,sizeof(receipt),receipt));
assert(!vg_event_receipt_verify(&crypto,key,sizeof(key),body,sizeof(body),201,receipt,sizeof(receipt),NULL));
assert(!vg_event_receipt_verify(NULL,key,sizeof(key),body,sizeof(body),201,receipt,sizeof(receipt),out));
assert(memcmp(key,saved_key,sizeof(key))==0&&memcmp(body,saved_body,sizeof(body))==0&&memcmp(receipt,saved_receipt,sizeof(receipt))==0);
''')

    def test_crypto_provider_failures_never_publish_verified_digest(self):
        self.c(r'''
crypto.sha256=fail_hash;
assert(!vg_event_receipt_verify(&crypto,key,sizeof(key),body,sizeof(body),201,receipt,sizeof(receipt),out));
crypto=vg_receipt_native_provider();crypto.hmac_sha256=fail_mac;
assert(!vg_event_receipt_verify(&crypto,key,sizeof(key),body,sizeof(body),201,receipt,sizeof(receipt),out));
assert(memcmp(out,sentinel,32)==0);
''', extra=r'''
static bool fail_hash(void *ctx,const uint8_t *p,size_t n,uint8_t d[32]){(void)vg_receipt_native_sha256(ctx,p,n,d);return false;}
static bool fail_mac(void *ctx,const uint8_t *k,size_t kn,const uint8_t *p,size_t n,uint8_t d[32]){(void)vg_receipt_native_hmac(ctx,k,kn,p,n,d);return false;}
''')

    def test_sdk_uses_volatile_standard_crypto_and_checks_key_destruction(self):
        source = (ROOT/'firmware/src/esp32_network_client.c').read_text(encoding='utf-8')
        for name in ('psa_hash_compute', 'psa_mac_compute', 'PSA_KEY_LIFETIME_VOLATILE',
                     'psa_destroy_key', 'destroyed == PSA_SUCCESS', 'MBEDTLS_SVC_KEY_ID_INIT'):
            self.assertIn(name, source)
        self.assertNotIn('vg_b40_', source)

    def test_receipt_media_type_is_exact_bounded_and_case_insensitive(self):
        self.c(r'''
assert(vg_event_receipt_content_type_valid("application/vnd.vgw.event-receipt-v1"));
assert(vg_event_receipt_content_type_valid("Application/Vnd.Vgw.Event-Receipt-V1"));
assert(!vg_event_receipt_content_type_valid(NULL));assert(!vg_event_receipt_content_type_valid(""));
assert(!vg_event_receipt_content_type_valid("application/json"));
assert(!vg_event_receipt_content_type_valid("application/vnd.vgw.event-receipt-v1;charset=utf-8"));
assert(!vg_event_receipt_content_type_valid("application/vnd.vgw.event-receipt-v2"));
assert(!vg_event_receipt_content_type_valid(" application/vnd.vgw.event-receipt-v1"));
''')


if __name__ == '__main__':
    unittest.main(verbosity=2)
