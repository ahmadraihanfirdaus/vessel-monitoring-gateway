/* Standalone B43 C99 cross-process fixture; no DB, filesystem persistence,
 * malloc, locks or network operations in the verifier under test. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "phase9_b43_nonce_ledger_host.h"
static int read_exact(const char *path,uint8_t *out,size_t length){
    FILE *f=fopen(path,"rb");if(!f)return 0;
    size_t n=fread(out,1u,length,f);int tail=fgetc(f);
    int ok=n==length&&tail==EOF&&!ferror(f);
    if(fclose(f)!=0)ok=0;
    return ok;
}
static int parse(const char *value,uint64_t *out){
    char *end=NULL;unsigned long long n=strtoull(value,&end,10);
    if(!value[0]||value[0]=='-'||!end||*end)return 0;
    *out=(uint64_t)n;return 1;
}
static void setup(vg_b41_observation *a,uint32_t purpose,uint32_t dev){
    memset(a,0,sizeof(*a));a->authority_revision=12u;a->source_id=777u;
    a->scope.purpose_id=purpose;a->scope.device_tag=dev;
    a->scope.rotation.active_key_id=202u;
    a->scope.rotation.retired_key_id=101u;
    a->scope.rotation.activation_epoch=40u;
    a->scope.rotation.exclusive_epoch_floor=39u;
}
static bool verify(const uint8_t *sealed,const uint8_t *wire,
    const vg_b41_observation *pre,const vg_b41_observation *post,
    uint64_t floor,uint64_t source,uint32_t purpose,uint32_t dev,
    const uint8_t *master,const uint8_t *nonce,const uint8_t *echo,
    const uint8_t *mac,vg_b43_nonce_ledger *ledger,uint64_t *epoch){
    return vg_b43_verify_once(sealed,128u,wire,72u,pre,post,floor,source,purpose,
        dev,master,32u,nonce,16u,echo,16u,mac,32u,ledger,epoch);
}
static void make_proof(const uint8_t *master,const uint8_t *sealed,const uint8_t *wire,
    uint8_t *nonce,uint32_t purpose,uint32_t dev,uint8_t proof[32]){
    static const uint8_t domain[]="VG_PHASE9_B42_CHALLENGE_AUTH_V1";
    uint8_t payload[248];size_t at=0u;
    memcpy(payload+at,nonce,16u);at+=16u;
    memcpy(payload+at,sealed,128u);at+=128u;
    memcpy(payload+at,wire,72u);at+=72u;
    vg_b40_put_le64(payload+at,12u);at+=8u;
    vg_b40_put_le64(payload+at,777u);at+=8u;
    vg_b40_put_le32(payload+at,purpose);at+=4u;
    vg_b40_put_le32(payload+at,dev);at+=4u;
    vg_b40_put_le64(payload+at,40u);at+=8u;
    if(at!=sizeof(payload)||!vg_b40_hmac(master,32u,domain,sizeof(domain),
            payload,sizeof(payload),proof))abort();
    vg_b40_zero(payload,sizeof(payload));
}
int main(int argc,char **argv){
    if(argc!=14)return 20;
    uint8_t master[32],sealed[128],wire[72],nonce[16],echo[16],mac[32];
    if(!read_exact(argv[1],master,sizeof(master))||
       !read_exact(argv[2],sealed,sizeof(sealed))||
       !read_exact(argv[3],wire,sizeof(wire))||
       !read_exact(argv[4],nonce,sizeof(nonce))||
       !read_exact(argv[5],echo,sizeof(echo))||
       !read_exact(argv[6],mac,sizeof(mac)))return 21;
    uint64_t purpose=0u,dev=0u,rev=0u,floor=0u,source=0u;
    if(!parse(argv[7],&purpose)||!parse(argv[8],&dev)||
       !parse(argv[9],&rev)||!parse(argv[10],&floor)||
       !parse(argv[11],&source)||purpose>UINT32_MAX||dev>UINT32_MAX)return 22;
    const char *mode=argv[12],*expected=argv[13];
    vg_b41_observation pre,post;setup(&pre,(uint32_t)purpose,(uint32_t)dev);
    setup(&post,(uint32_t)purpose,(uint32_t)dev);post.authority_revision=rev;
    vg_b43_nonce_ledger ledger;vg_b43_ledger_init(&ledger);
    uint64_t epoch=UINT64_C(0x8877665544332211);
    bool accepted=verify(sealed,wire,&pre,&post,floor,source,(uint32_t)purpose,
       (uint32_t)dev,master,nonce,echo,mac,&ledger,&epoch);
    bool expected_accept=!strcmp(expected,"accept");
    if(accepted!=expected_accept)return 23;
    if(!accepted){
        if(epoch!=UINT64_C(0x8877665544332211)||ledger.count!=0u||
           !vg_b43_ledger_valid(&ledger))return 24;
        puts("B43_LEDGER=DENIED_TEST_ONLY");return 0;
    }
    if(epoch!=40u||ledger.count!=1u||!vg_b43_ledger_valid(&ledger))return 25;
    vg_b43_nonce_ledger snapshot=ledger;
    uint64_t sentinel=UINT64_C(0x8877665544332211);
    if(!strcmp(mode,"first")){
        puts("B43_LEDGER=ACCEPT_TEST_ONLY");return 0;
    }
    if(!strcmp(mode,"replay")||!strcmp(mode,"replay-after-denial")){
        if(verify(sealed,wire,&pre,&post,floor,source,(uint32_t)purpose,
           (uint32_t)dev,master,nonce,echo,mac,&ledger,&sentinel)||
           sentinel!=UINT64_C(0x8877665544332211)||
           memcmp(&snapshot,&ledger,sizeof(ledger)))return 26;
        if(!strcmp(mode,"replay-after-denial")){
            uint8_t bad[32];memcpy(bad,mac,sizeof(bad));bad[1]^=0x80u;
            if(verify(sealed,wire,&pre,&post,floor,source,(uint32_t)purpose,
                (uint32_t)dev,master,nonce,echo,bad,&ledger,&sentinel)||
                memcmp(&snapshot,&ledger,sizeof(ledger)))return 27;
        }
        puts("B43_LEDGER=REPLAY_DENIED_TEST_ONLY");return 0;
    }
    if(!strcmp(mode,"alias")){
        if(verify(sealed,wire,&pre,&post,floor,source,(uint32_t)purpose,
           (uint32_t)dev,master,nonce,echo,mac,&ledger,
           (uint64_t *)(void *)&ledger)||memcmp(&snapshot,&ledger,sizeof(ledger)))return 28;
        puts("B43_LEDGER=ALIAS_DENIED_TEST_ONLY");return 0;
    }
    if(!strcmp(mode,"ledger-corrupt")){
        ledger.used[2][0]=1u;
        vg_b43_nonce_ledger corrupt=ledger;
        if(vg_b43_ledger_valid(&ledger)||verify(sealed,wire,&pre,&post,floor,source,
           (uint32_t)purpose,(uint32_t)dev,master,nonce,echo,mac,&ledger,&sentinel)||
           memcmp(&corrupt,&ledger,sizeof(ledger)))return 29;
        puts("B43_LEDGER=CORRUPT_DENIED_TEST_ONLY");return 0;
    }
    if(!strcmp(mode,"exhaust")){
        for(size_t i=1u;i<=VG_B43_NONCE_CAPACITY;++i){
            uint8_t next[16],echo_next[16],proof[32];memcpy(next,nonce,16u);
            next[0]=(uint8_t)(nonce[0]^(uint8_t)i);next[1]^=(uint8_t)i;memcpy(echo_next,next,16u);
            make_proof(master,sealed,wire,next,(uint32_t)purpose,(uint32_t)dev,proof);
            vg_b43_nonce_ledger before=ledger;
            sentinel=UINT64_C(0x8877665544332211);
            bool ok=verify(sealed,wire,&pre,&post,floor,source,(uint32_t)purpose,
                (uint32_t)dev,master,next,echo_next,proof,&ledger,&sentinel);
            if(i<VG_B43_NONCE_CAPACITY){
                if(!ok||ledger.count!=i+1u||sentinel!=40u)return 30;
            }else{
                if(ok||sentinel!=UINT64_C(0x8877665544332211)||
                   memcmp(&before,&ledger,sizeof(ledger)))return 31;
            }
        }
        puts("B43_LEDGER=EXHAUST_DENIED_TEST_ONLY");return 0;
    }
    if(!strcmp(mode,"alias-input")){
        /* Ensure ledger region cannot alias input even on otherwise valid proof. */
        if(verify(sealed,wire,&pre,&post,floor,source,(uint32_t)purpose,
           (uint32_t)dev,master,(const uint8_t *)(const void *)&ledger,echo,
           mac,&ledger,&sentinel)||memcmp(&snapshot,&ledger,sizeof(ledger)))return 32;
        puts("B43_LEDGER=ALIAS_DENIED_TEST_ONLY");return 0;
    }
    return 33;
}
