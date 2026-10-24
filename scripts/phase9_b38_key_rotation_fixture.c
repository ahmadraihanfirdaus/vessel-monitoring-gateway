#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include "phase9_b38_key_rotation_host.h"
static bool read_exact(const char *path,uint8_t *data,size_t count,size_t *actual){
    FILE *f=fopen(path,"rb");if(!f)return false;
    *actual=fread(data,1,count+1u,f);
    int err=ferror(f);int extra=fgetc(f);
    if(fclose(f))err=1;
    return !err && extra==EOF;
}
int main(int argc,char **argv){
    if(argc!=4)return 2;
    uint8_t sealed[129]={0},wire[73]={0};size_t s=0u,w=0u;
    if(!read_exact(argv[1],sealed,128u,&s)||!read_exact(argv[2],wire,72u,&w))return 20;
    const bool post=argv[3][0]=='p' && argv[3][1]=='o' && argv[3][2]=='s' && argv[3][3]=='t' && argv[3][4]=='\0';
    const bool pre=argv[3][0]=='p' && argv[3][1]=='r' && argv[3][2]=='e' && argv[3][3]=='\0';
    if(!post && !pre)return 3;
    vg_b38_policy p=post ? (vg_b38_policy){202u,101u,40u,39u} :
                        (vg_b38_policy){101u,0u,1u,0u};
    uint64_t epoch=UINT64_C(0xDDCCBBAA99887766),sentinel=epoch;
    bool ok=vg_b38_precheck_rotation(sealed,s,wire,w,&p,&epoch);
    if(!ok && epoch!=sentinel)return 21;
    puts(ok ? "B38_STRUCTURAL_ONLY=PASS_NO_AUTH" : "B38_STRUCTURAL_ONLY=DENIED_NO_AUTH");
    return 0;
}
