"""Real pure-C admission/frame helpers; actual ESP-IDF image is a separate gate."""
import unittest
from pathlib import Path
from phase9_b4_testlib import compile_c

ROOT = Path(__file__).resolve().parents[1]
BASE = r'''
#include "esp32_network_profile.h"
#include "runtime_uplink_frame.h"
static inline vg_net_profile good(void) {
    vg_net_profile p = {0};
    strcpy(p.ssid,"synthetic-lab");
    strcpy(p.wifi_password,"example-only");
    strcpy(p.origin,"https://example.invalid");
    memset(p.bearer,'x',32u);
    strcpy(p.device_id,"runtime:demo");
    p.policy=(net001_host_policy){1000u,50u,3u};
    return p;
}
'''


class Esp32NetworkPortTest(unittest.TestCase):
    def c(self, body):
        return compile_c(BASE + '\nint main(void) {\n' + body + '\nreturn 0; }\n', extra_flags=('-Os',))

    def test_profile_policy_and_string_bounds(self):
        self.c(r'''
vg_net_profile p=good(); assert(vg_net_profile_valid(&p));
assert(!vg_net_profile_valid(NULL));
p.policy.connect_timeout_ms=0u;assert(!vg_net_profile_valid(&p));
p=good();p.policy.connect_timeout_ms=60000u;assert(vg_net_profile_valid(&p));
p.policy.connect_timeout_ms=60001u;assert(!vg_net_profile_valid(&p));
p=good();p.policy.reconnect_backoff_ms=0u;assert(!vg_net_profile_valid(&p));
p=good();p.policy.reconnect_backoff_ms=60001u;assert(!vg_net_profile_valid(&p));
p=good();p.policy.max_attempts=0u;assert(!vg_net_profile_valid(&p));
p.policy.max_attempts=16u;assert(vg_net_profile_valid(&p));
p.policy.max_attempts=17u;assert(!vg_net_profile_valid(&p));
p=good();p.ssid[0]=0;assert(!vg_net_profile_valid(&p));
p=good();memset(p.ssid,'s',sizeof(p.ssid));assert(!vg_net_profile_valid(&p));
p.ssid[32]=0;assert(vg_net_profile_valid(&p));
p=good();memset(p.wifi_password,'x',sizeof(p.wifi_password));assert(!vg_net_profile_valid(&p));
p.wifi_password[63]=0;assert(vg_net_profile_valid(&p));
p.wifi_password[7]=0;assert(!vg_net_profile_valid(&p));
p=good();p.bearer[31]=0;assert(!vg_net_profile_valid(&p));
p=good();memset(p.bearer,'x',sizeof(p.bearer));assert(!vg_net_profile_valid(&p));
p.bearer[256]=0;assert(vg_net_profile_valid(&p));
p.bearer[9]='\r';assert(!vg_net_profile_valid(&p));
p=good();p.bearer[9]=' ';assert(!vg_net_profile_valid(&p));
p=good();p.bearer[9]='+';p.bearer[10]='/';p.bearer[31]='=';assert(vg_net_profile_valid(&p));
p=good();memset(p.device_id,'d',sizeof(p.device_id));assert(!vg_net_profile_valid(&p));
p.device_id[48]=0;assert(vg_net_profile_valid(&p));
''')

    def test_https_authority_admission(self):
        self.c(r'''
const char *bad[]={"http://example.invalid","https://","https:///", "https://a/path",
"https://a?query", "https://a#fragment", "https://a\\other", "https://a\r\nInjected",
"https://" "user:" "example@" "example.invalid", "https://a:0", "https://a:65536", "https://a:99999999999999999999",
"https://a:", "https://a:4x", "https://.a", "https://a.", "https://a..b", "https://[::1", "https://[]", "https://[::1]other"};
for(size_t i=0;i<sizeof(bad)/sizeof(bad[0]);i++)assert(!vg_net_origin_valid(bad[i]));
assert(vg_net_origin_valid("https://example.invalid/"));
assert(vg_net_origin_valid("https://example.invalid:65535"));
assert(vg_net_origin_valid("https://[::1]:443"));
assert(!vg_net_origin_valid(NULL));
vg_net_profile p=good();memset(p.origin,'a',sizeof(p.origin));assert(!vg_net_profile_valid(&p));
''')

    def test_queue_body_reply_and_retry_limits(self):
        self.c(r'''
char bytes[VG_NET_BODY_MAX]={0};
assert(vg_net_job_valid(VG_NET_TELEMETRY,bytes,sizeof(bytes)));
assert(vg_net_job_valid(VG_NET_EVENT,bytes,1u));
assert(!vg_net_job_valid(0,bytes,1u));assert(!vg_net_job_valid(VG_NET_EVENT,NULL,1u));
assert(!vg_net_job_valid(VG_NET_EVENT,bytes,0u));assert(!vg_net_job_valid(VG_NET_EVENT,bytes,sizeof(bytes)+1u));
char reply[VG_NET_REPLY_MAX+1u];memset(reply,'z',sizeof(reply));size_t used=0u;
assert(vg_net_reply_append(reply,&used,NULL,0u));assert(used==0u&&reply[0]==0);
assert(vg_net_reply_append(reply,&used,bytes,VG_NET_REPLY_MAX));assert(used==VG_NET_REPLY_MAX&&reply[used]==0);
char before[sizeof(reply)];memcpy(before,reply,sizeof(reply));
assert(!vg_net_reply_append(reply,&used,bytes,1u));assert(used==VG_NET_REPLY_MAX&&!memcmp(before,reply,sizeof(reply)));
used=0u;assert(!vg_net_reply_append(reply,&used,NULL,1u));
assert(vg_net_http_retryable(false,0,false));assert(vg_net_http_retryable(true,503,false));
assert(vg_net_http_retryable(true,429,false));assert(vg_net_http_retryable(true,408,false));
int permanent[]={200,201,301,302,307,401,403,409,413,422,600,-1};
for(size_t i=0;i<sizeof(permanent)/sizeof(permanent[0]);i++)assert(!vg_net_http_retryable(true,permanent[i],false));
assert(vg_net_http_retryable(false,201,false));assert(!vg_net_http_retryable(false,0,true));
''')

    def test_frame_preserves_zero_null_source_and_failure_outputs(self):
        self.c(r'''
vg_measurement_t sample={VG_SOURCE_SIMULATION,VG_QUALITY_VALID,true,0.0f};
vg_telemetry_payload_t p={0},before;char wire[4097]={0},old[4097]={0};
assert(vg_runtime_uplink_frame("runtime:demo","synthetic-boot",UINT64_MAX,UINT64_MAX,&sample,&p,wire,sizeof(wire)));
assert(strstr(wire,"\"value\":0")&&strstr(wire,"simulation"));
sample.quality=VG_QUALITY_INVALID;
assert(vg_runtime_uplink_frame("runtime:demo","synthetic-boot",2u,2u,&sample,&p,wire,sizeof(wire)));
assert(strstr(wire,"\"value\":null")&&!p.channels[0].has_value);
memcpy(&before,&p,sizeof(p));memcpy(old,wire,sizeof(wire));
assert(!vg_runtime_uplink_frame("runtime:demo","synthetic-boot",2u,2u,&sample,&p,wire,4u));
assert(!memcmp(&p,&before,sizeof(p))&&!memcmp(wire,old,sizeof(wire)));
sample.source_mode=VG_SOURCE_PHYSICAL;
assert(!vg_runtime_uplink_frame("runtime:demo","synthetic-boot",2u,2u,&sample,&p,wire,sizeof(wire)));
assert(!memcmp(&p,&before,sizeof(p))&&!memcmp(wire,old,sizeof(wire)));
sample.source_mode=VG_SOURCE_SIMULATION;
assert(!vg_runtime_uplink_frame("runtime:demo","synthetic-boot",2u,2u,&sample,&p,(char*)&p,sizeof(p)));
''')

    def test_real_sdk_security_and_nonblocking_boundaries_are_present(self):
        src = (ROOT/'firmware/src/esp32_network_client.c').read_text(encoding='utf-8')
        for required in ['NVS_READONLY', 'WIFI_STORAGE_RAM', 'esp_crt_bundle_attach',
                         '.skip_cert_common_name_check = false', '.disable_auto_redirect = true',
                         '.is_async = true', 'ESP_ERR_HTTP_EAGAIN', 'now - started',
                         'xSemaphoreTake(client->submit_lock, 0)', 'xQueueSend(client->jobs, &client->staging, 0)',
                         'vg_net_http_retryable', 'NET_HALT_BIT', 'CONFIG_MBEDTLS_HAVE_TIME_DATE',
                         'CONFIG_ESP_TLS_INSECURE', 'CONFIG_ESP_TLS_SKIP_SERVER_CERT_VERIFY']:
            self.assertIn(required, src)
        self.assertNotIn('nvs_flash_erase(', src)
        self.assertNotIn('ESP_ERROR_CHECK(', src)
        self.assertNotIn('skip_cert_common_name_check = true', src)
        workflow = (ROOT/'.github/workflows/phase9-multi-context-ci.yml').read_text(encoding='utf-8')
        self.assertIn('firmware-esp32-sdk:', workflow)
        self.assertIn('platformio==6.2.0', workflow)
        self.assertIn('scripts/build_esp32_port.py', workflow)
        self.assertEqual(workflow.count("php-version: '8.2.35'"), 3)
        self.assertIn('contents: read', workflow)


if __name__ == '__main__':
    unittest.main(verbosity=2)
