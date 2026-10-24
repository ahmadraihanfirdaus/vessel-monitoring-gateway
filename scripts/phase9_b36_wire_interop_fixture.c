/* Independent C99 B36 test oracle. B35 encoder is separately compiled. */
#include <stdio.h>
#include "phase9_b36_wire_interop_host.h"
static bool read_wire(const char *path,uint8_t raw[73],size_t *length){
    FILE *f=fopen(path,"rb");if(!f)return false;
    *length=fread(raw,1,73u,f);
    int err=ferror(f);int extra=fgetc(f);
    if(fclose(f))err=1;
    return !err && extra==EOF;
}
static int check36(const char *golden,const char *candidate,const char *mode){
    uint8_t reference[73]={0},bytes[73]={0};size_t a=0u,b=0u;
    if(!read_wire(golden,reference,&a) || !read_wire(candidate,bytes,&b))return 20;
    vg_b35_receipt oracle;memset(&oracle,0x55,sizeof(oracle));
    vg_b35_receipt candidate_fields;memset(&candidate_fields,0xa5,sizeof(candidate_fields));
    vg_b35_receipt before=candidate_fields;
    bool a_ok=vg_b36_reference_decode(reference,a,&oracle);
    bool b_ok=vg_b36_reference_decode(bytes,b,&candidate_fields);
    if(!a_ok || a!=72u)return 21;
    uint8_t recoded[72];
    if(!vg_b36_reference_encode(&oracle,recoded,sizeof(recoded)) ||
        memcmp(reference,recoded,sizeof(recoded)))return 22;
    bool accepted=b_ok && b==72u &&
       !memcmp(&oracle,&candidate_fields,sizeof(oracle)) &&
       !memcmp(reference,bytes,72u);
    if(!strcmp(mode,"accept")){
        if(!accepted)return 23;
    }else if(!strcmp(mode,"deny")){
        if(accepted || (!b_ok && memcmp(&candidate_fields,&before,sizeof(before))))return 24;
    }else return 25;
    printf("B36_WIRE=PASS_%s\n",mode);return 0;
}
int main(int argc,char **argv){
    if(argc==5 && !strcmp(argv[1],"check"))return check36(argv[2],argv[3],argv[4]);
    return 2;
}
