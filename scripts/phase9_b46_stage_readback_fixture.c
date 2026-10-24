/* Standalone host-only C99 two-slot staged-write/readback admission fixture. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "phase9_b46_stage_readback_host.h"
static int read_blob(const char *path,uint8_t *out,size_t *len){
    if(!strcmp(path,"-")){*len=0u;return 1;}
    FILE *f=fopen(path,"rb");if(!f)return 0;
    *len=fread(out,1u,VG_B44_SNAPSHOT_LENGTH+1u,f);
    int eof=fgetc(f),ok=!ferror(f)&&eof==EOF;
    if(fclose(f))ok=0;
    return ok;
}
static int read_key(const char *path,uint8_t key[32]){
    FILE *f=fopen(path,"rb");if(!f)return 0;
    size_t n=fread(key,1u,32u,f);int eof=fgetc(f);
    int ok=(n==32u&&eof==EOF&&!ferror(f));if(fclose(f))ok=0;
    return ok;
}
static int number(const char *s,uint64_t *n){
    if(!s||!*s||*s=='-')return 0;
    char *end=NULL;unsigned long long tmp=strtoull(s,&end,10);
    if(s==end||*end)return 0;
    *n=(uint64_t)tmp;return 1;
}
static int selftest(void){
    uint8_t key[32],old[192],newer[192],observed[192];memset(key,0x17,sizeof(key));
    vg_b43_nonce_ledger a,b;vg_b43_ledger_init(&a);vg_b43_ledger_init(&b);
    uint8_t nonce[16];memset(nonce,0x32,sizeof(nonce));
    memcpy(b.used,nonce,sizeof(nonce));b.count=1u;if(!vg_b43_ledger_valid(&b))return 40;
    if(!vg_b44_seal_nonce_ledger(&a,11u,777u,key,32u,old,sizeof(old))||
       !vg_b44_seal_nonce_ledger(&b,12u,777u,key,32u,newer,sizeof(newer)))return 41;
    memcpy(observed,newer,sizeof(observed));
    vg_b43_nonce_ledger output;memset(&output,0xA5,sizeof(output));
    vg_b43_nonce_ledger before=output;
    uint64_t gen=UINT64_C(0xFEEDABCDACDCFEED);uint8_t idx=0xABu;
    if(vg_b46_admit_staged_readback(old,192u,NULL,0u,newer,192u,observed,192u,
          1u,777u,key,32u,&output,&gen,(uint8_t*)(void *)&gen)||
       memcmp(&before,&output,sizeof(output))||gen!=UINT64_C(0xFEEDABCDACDCFEED))return 42;
    if(vg_b46_admit_staged_readback(old,192u,NULL,0u,newer,192u,observed,192u,
          1u,777u,key,32u,(vg_b43_nonce_ledger*)(void *)old,&gen,&idx)||
       memcmp(&before,&output,sizeof(output)))return 43;
    if(vg_b46_admit_staged_readback(old,192u,NULL,0u,newer,192u,observed,192u,
          1u,777u,key,32u,&output,(uint64_t*)(void *)&output,&idx)||
       memcmp(&before,&output,sizeof(output)))return 44;
    if(vg_b46_admit_staged_readback(old,192u,NULL,0u,newer,192u,observed,192u,
          1u,777u,key,32u,&output,&gen,(uint8_t*)(void *)newer)||
       memcmp(&before,&output,sizeof(output)))return 45;
    if(vg_b46_admit_staged_readback(old,192u,NULL,0u,newer,192u,observed,192u,
          1u,777u,key,32u,&output,&gen,&idx)==false)return 46;
    if(gen!=12u||idx!=1u||memcmp(&output,&b,sizeof(b)))return 47;
    puts("B46_ALIAS_FAIL_CLOSED_NO_OUTPUT_ON_DENY=PASS");return 0;
}
int main(int argc,char **argv){
    if(argc==2&&!strcmp(argv[1],"selftest"))return selftest();
    if(argc!=9)return 20;
    uint8_t a[193],b[193],staged[193],readback[193],key[32];
    size_t na=0u,nb=0u,ns=0u,nr=0u;
    uint64_t floor=0u,source=0u;
    if(!read_blob(argv[1],a,&na)||!read_blob(argv[2],b,&nb)||
       !read_blob(argv[3],staged,&ns)||!read_blob(argv[4],readback,&nr)||
       !read_key(argv[5],key)||!number(argv[7],&floor)||
       !number(argv[8],&source))return 21;
    vg_b43_nonce_ledger result;memset(&result,0xA5,sizeof(result));
    vg_b43_nonce_ledger original=result;
    uint64_t gen=UINT64_C(0xBADA55BADA55BADA);uint8_t index=0xACu;
    bool passed=vg_b46_admit_staged_readback(strcmp(argv[1],"-")?a:NULL,na,
       strcmp(argv[2],"-")?b:NULL,nb,
       strcmp(argv[3],"-")?staged:NULL,ns,
       strcmp(argv[4],"-")?readback:NULL,nr,
       floor,source,key,32u,&result,&gen,&index);
    if(!passed){
        if(memcmp(&result,&original,sizeof(result))||
           gen!=UINT64_C(0xBADA55BADA55BADA)||index!=0xACu)return 22;
        puts("B46_DENY_OUTPUT_UNCHANGED_HOST_ONLY");return 0;
    }
    FILE *f=fopen(argv[6],"wb");if(!f)return 23;
    uint8_t wire[141];wire[0]=index;vg_b40_put_le64(wire+1u,gen);
    vg_b40_put_le32(wire+9u,result.count);
    memcpy(wire+13u,result.used,sizeof(result.used));
    int ok=fwrite(wire,1u,sizeof(wire),f)==sizeof(wire)&&!ferror(f);
    if(fclose(f))ok=0;
    if(!ok)return 24;
    printf("B46_ACCEPT_INACTIVE_SLOT_%u_GEN_%llu_HOST_ONLY\n",(unsigned)index,
           (unsigned long long)gen);return 0;
}
