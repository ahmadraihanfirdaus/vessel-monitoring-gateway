#include <stdio.h>
#include <string.h>
#include "phase9_b37_hmac_receipt_host.h"
/* Precheck only, no secret/key or HMAC on C99. Authentication is in Python.
 * Successful precheck must never be treated as permission to publish ACK. */
static bool read_bounded(const char *path,uint8_t *dst,size_t max,size_t *n){
    FILE *f=fopen(path,"rb");if(!f)return false;
    *n=fread(dst,1,max+1u,f);
    int err=ferror(f);int extra=fgetc(f);
    if(fclose(f))err=1;
    return !err && extra==EOF;
}
int main(int argc,char **argv){
    if(argc!=3)return 2;
    uint8_t raw[129]={0},wire[73]={0};size_t a=0u,b=0u;
    if(!read_bounded(argv[1],raw,128u,&a) ||
       !read_bounded(argv[2],wire,72u,&b))return 20;
    uint64_t kid=UINT64_C(0xA5A5A5A5A5A5A5A5),epoch=kid;
    const uint64_t sentinel=kid;
    bool structural=vg_b37_peek_untrusted(raw,a,wire,b,&kid,&epoch);
    if(!structural && (kid!=sentinel || epoch!=sentinel))return 21;
    puts(structural ? "B37_STRUCTURAL_ONLY=PASS_NO_AUTH" : "B37_STRUCTURAL_ONLY=DENIED_NO_AUTH");
    return 0;
}
