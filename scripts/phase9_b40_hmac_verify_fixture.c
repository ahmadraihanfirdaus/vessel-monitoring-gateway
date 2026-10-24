/* B40 host-only test verifier: standalone process, secrets in disposable test files. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "phase9_b40_hmac_verify_host.h"
static int exact_read(const char *path,uint8_t *buf,size_t len) {
    FILE *f=fopen(path,"rb");if(!f)return 0;
    size_t got=fread(buf,1u,len,f);int extra=fgetc(f);
    int ok=(got==len && extra==EOF && !ferror(f));
    if(fclose(f)!=0)ok=0;
    return ok;
}
static int selftest(void) {
    static const uint8_t sha_abc[32]={0xba,0x78,0x16,0xbf,0x8f,0x01,0xcf,0xea,
    0x41,0x41,0x40,0xde,0x5d,0xae,0x22,0x23,0xb0,0x03,0x61,0xa3,0x96,0x17,
    0x7a,0x9c,0xb4,0x10,0xff,0x61,0xf2,0x00,0x15,0xad};
    static const uint8_t rfc4231_1[32]={0xb0,0x34,0x4c,0x61,0xd8,0xdb,0x38,0x53,
    0x5c,0xa8,0xaf,0xce,0xaf,0x0b,0xf1,0x2b,0x88,0x1d,0xc2,0x00,0xc9,0x83,
    0x3d,0xa7,0x26,0xe9,0x37,0x6c,0x2e,0x32,0xcf,0xf7};
    static const uint8_t rfc4231_2[32]={0x5b,0xdc,0xc1,0x46,0xbf,0x60,0x75,0x4e,
    0x6a,0x04,0x24,0x26,0x08,0x95,0x75,0xc7,0x5a,0x00,0x3f,0x08,0x9d,0x27,
    0x39,0x83,0x9d,0xec,0x58,0xb9,0x64,0xec,0x38,0x43};
    uint8_t digest[32],key[20];vg_b40_sha s;
    vg_b40_sha_init(&s);vg_b40_sha_update(&s,(const uint8_t *)"abc",3u);
    vg_b40_sha_final(&s,digest);if(memcmp(digest,sha_abc,32u))return 1;
    memset(key,0x0b,sizeof(key));
    if(!vg_b40_hmac(key,sizeof(key),(const uint8_t *)"Hi There",8u,NULL,0u,digest) ||
        memcmp(digest,rfc4231_1,32u))return 2;
    if(!vg_b40_hmac((const uint8_t *)"Jefe",4u,
        (const uint8_t *)"what do ya want for nothing?",28u,NULL,0u,digest) ||
        memcmp(digest,rfc4231_2,32u))return 3;
    vg_b40_zero(key,sizeof(key));vg_b40_zero(digest,sizeof(digest));
    puts("B40_SHA256_HMAC_RFC4231=PASS_3_VECTORS");return 0;
}
int main(int argc,char **argv) {
    if(argc==2 && !strcmp(argv[1],"selftest"))return selftest();
    if(argc!=7)return 20;
    uint8_t master[32],blob[128],wire[72];
    if(!exact_read(argv[1],master,sizeof(master)) ||
       !exact_read(argv[2],blob,sizeof(blob)) ||
       !exact_read(argv[3],wire,sizeof(wire))){
        puts("B40_HOST_HMAC=DENIED_TEST_ONLY");return 0;
    }
    char *end=NULL;
    unsigned long purpose=strtoul(argv[4],&end,10);
    if(!end || *end || purpose>UINT32_MAX)return 21;
    unsigned long dev=strtoul(argv[5],&end,10);
    if(!end || *end || dev>UINT32_MAX)return 22;
    if(strcmp(argv[6],"pre") && strcmp(argv[6],"post") &&
       strcmp(argv[6],"floor") && strcmp(argv[6],"future"))return 23;
    int pre=!strcmp(argv[6],"pre");
    vg_b39_scope_policy policy={0};
    policy.rotation.active_key_id=pre?101u:202u;
    policy.rotation.retired_key_id=pre?0u:101u;
    policy.rotation.activation_epoch=pre?1u:40u;
    policy.rotation.exclusive_epoch_floor=pre?0u:39u;
    if(!strcmp(argv[6],"floor"))policy.rotation.exclusive_epoch_floor=40u;
    if(!strcmp(argv[6],"future"))policy.rotation.activation_epoch=41u;
    policy.purpose_id=(uint32_t)purpose;policy.device_tag=(uint32_t)dev;
    uint64_t epoch=0x55aabbccddee1122ULL;
    bool ok=vg_b40_verify_host_hmac(blob,sizeof(blob),wire,sizeof(wire),&policy,
             (uint32_t)purpose,(uint32_t)dev,master,sizeof(master),&epoch);
    vg_b40_zero(master,sizeof(master));
    if(!ok && epoch!=0x55aabbccddee1122ULL)return 24;
    if(ok && epoch!=vg_b36_get64(blob+16u))return 25;
    puts(ok?"B40_HOST_HMAC=ACCEPT_TEST_ONLY":"B40_HOST_HMAC=DENIED_TEST_ONLY");
    return 0;
}
