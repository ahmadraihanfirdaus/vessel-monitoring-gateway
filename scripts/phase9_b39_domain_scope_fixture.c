/* B39 C99 policy-only harness. A structural PASS is NEVER HMAC approval. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "phase9_b39_domain_scope_host.h"

static int load(const char *path,uint8_t *data,size_t exact) {
    FILE *f=fopen(path,"rb");
    if(!f)return 0;
    size_t got=fread(data,1u,exact,f);
    int extra=fgetc(f);
    int success=(got==exact && extra==EOF && !ferror(f));
    if(fclose(f)!=0)success=0;
    return success;
}
static int selftest(void) {
    /* Check rejection-before-write and pointer aliasing without secrets. */
    uint8_t receipt[128]={0},wire[72]={0};
    vg_b39_scope_policy policy={0};
    uint64_t sentinel=0x1234abcd5678ef90ULL,epoch=sentinel;
    if(vg_b39_precheck_untrusted_scope(receipt,sizeof(receipt),wire,sizeof(wire),
        &policy,1u,7u,&epoch) || epoch!=sentinel)return 1;
    if(vg_b39_precheck_untrusted_scope(receipt,sizeof(receipt),wire,sizeof(wire),
        &policy,1u,7u,(uint64_t *)(void *)receipt) || receipt[0]!=0u)return 2;
    if(vg_b39_precheck_untrusted_scope(receipt,sizeof(receipt),wire,sizeof(wire),
        &policy,1u,7u,(uint64_t *)(void *)&policy))return 3;
    if(vg_b39_precheck_untrusted_scope(receipt,sizeof(receipt),wire,sizeof(wire),
        &policy,1u,0u,&epoch) || epoch!=sentinel)return 4;
    puts("B39_C99_SCOPE_SELFTEST=PASS_STRUCTURAL_ONLY_NO_AUTH");
    return 0;
}
int main(int argc,char **argv) {
    if(argc==2 && !strcmp(argv[1],"selftest"))return selftest();
    if(argc!=6)return 20;
    uint8_t sealed[128],wire[72];
    if(!load(argv[1],sealed,sizeof(sealed)) || !load(argv[2],wire,sizeof(wire))) {
        puts("B39_STRUCTURAL_ONLY=DENIED_NO_AUTH");return 0;
    }
    char *end=NULL;
    unsigned long purpose=strtoul(argv[3],&end,10);
    if(!end || *end || purpose>UINT32_MAX)return 21;
    unsigned long tag=strtoul(argv[4],&end,10);
    if(!end || *end || tag>UINT32_MAX)return 22;
    if(strcmp(argv[5],"pre") && strcmp(argv[5],"post"))return 23;
    int post=!strcmp(argv[5],"post");
    vg_b39_scope_policy policy={0};
    policy.rotation.active_key_id=post?202u:101u;
    policy.rotation.retired_key_id=post?101u:0u;
    policy.rotation.activation_epoch=post?40u:1u;
    policy.rotation.exclusive_epoch_floor=post?39u:0u;
    policy.purpose_id=(uint32_t)purpose;
    policy.device_tag=(uint32_t)tag;
    uint64_t epoch=0x4badbadbadbadbadULL;
    bool ok=vg_b39_precheck_untrusted_scope(sealed,sizeof(sealed),wire,sizeof(wire),
        &policy,(uint32_t)purpose,(uint32_t)tag,&epoch);
    puts(ok?"B39_STRUCTURAL_ONLY=PASS_NO_AUTH":"B39_STRUCTURAL_ONLY=DENIED_NO_AUTH");
    if(!ok && epoch!=0x4badbadbadbadbadULL)return 24;
    return 0;
}
