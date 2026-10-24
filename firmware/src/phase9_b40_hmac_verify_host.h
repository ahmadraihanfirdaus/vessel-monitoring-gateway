#ifndef PHASE9_B40_HMAC_VERIFY_HOST_H
#define PHASE9_B40_HMAC_VERIFY_HOST_H
/* HOST TEST-ONLY SHA256/HMAC reference implementation, not hardware/production crypto.
 * Never use a structural precheck alone to authorize checkpoint/ACK. External key
 * provisioning, counter durability, concurrency and key confidentiality NOT VERIFIED. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "phase9_b39_domain_scope_host.h"

typedef struct vg_b40_sha {
    uint32_t h[8];
    uint64_t byte_count;
    uint8_t buf[64];
    size_t used;
} vg_b40_sha;
static inline uint32_t vg_b40_ror(uint32_t a,unsigned int n) {return (a>>n)|(a<<(32u-n));}
static inline uint32_t vg_b40_be32(const uint8_t *p) {
    return ((uint32_t)p[0]<<24u)|((uint32_t)p[1]<<16u)|((uint32_t)p[2]<<8u)|p[3];
}
static inline void vg_b40_put_be32(uint8_t *p,uint32_t x) {
    p[0]=(uint8_t)(x>>24u);p[1]=(uint8_t)(x>>16u);p[2]=(uint8_t)(x>>8u);p[3]=(uint8_t)x;
}
static inline void vg_b40_put_le32(uint8_t *p,uint32_t x) {
    for(unsigned int i=0u;i<4u;++i)p[i]=(uint8_t)(x>>(8u*i));
}
static inline void vg_b40_put_le64(uint8_t *p,uint64_t x) {
    for(unsigned int i=0u;i<8u;++i)p[i]=(uint8_t)(x>>(8u*i));
}
static inline void vg_b40_zero(void *ptr,size_t n) {
    volatile uint8_t *p=(volatile uint8_t *)ptr;
    while(n--) *p++=0u;
}
static inline void vg_b40_sha_init(vg_b40_sha *s) {
    static const uint32_t iv[8]={0x6a09e667u,0xbb67ae85u,0x3c6ef372u,0xa54ff53au,
        0x510e527fu,0x9b05688cu,0x1f83d9abu,0x5be0cd19u};
    memcpy(s->h,iv,sizeof(iv));s->byte_count=0u;s->used=0u;
    memset(s->buf,0,sizeof(s->buf));
}
static inline void vg_b40_sha_block(vg_b40_sha *s,const uint8_t *p) {
    static const uint32_t k[64]={
        0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,0x3956c25bu,0x59f111f1u,0x923f82a4u,0xab1c5ed5u,
        0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,
        0xe49b69c1u,0xefbe4786u,0x0fc19dc6u,0x240ca1ccu,0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
        0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,0xc6e00bf3u,0xd5a79147u,0x06ca6351u,0x14292967u,
        0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,0x650a7354u,0x766a0abbu,0x81c2c92eu,0x92722c85u,
        0xa2bfe8a1u,0xa81a664bu,0xc24b8b70u,0xc76c51a3u,0xd192e819u,0xd6990624u,0xf40e3585u,0x106aa070u,
        0x19a4c116u,0x1e376c08u,0x2748774cu,0x34b0bcb5u,0x391c0cb3u,0x4ed8aa4au,0x5b9cca4fu,0x682e6ff3u,
        0x748f82eeu,0x78a5636fu,0x84c87814u,0x8cc70208u,0x90befffau,0xa4506cebu,0xbef9a3f7u,0xc67178f2u};
    uint32_t w[64];
    for(unsigned int i=0u;i<16u;++i)w[i]=vg_b40_be32(p+4u*i);
    for(unsigned int i=16u;i<64u;++i){
        uint32_t x=w[i-15u],y=w[i-2u];
        uint32_t s0=vg_b40_ror(x,7u)^vg_b40_ror(x,18u)^(x>>3u);
        uint32_t s1=vg_b40_ror(y,17u)^vg_b40_ror(y,19u)^(y>>10u);
        w[i]=w[i-16u]+s0+w[i-7u]+s1;
    }
    uint32_t a=s->h[0],b=s->h[1],c=s->h[2],d=s->h[3];
    uint32_t e=s->h[4],f=s->h[5],g=s->h[6],h=s->h[7];
    for(unsigned int i=0u;i<64u;++i){
        uint32_t s1=vg_b40_ror(e,6u)^vg_b40_ror(e,11u)^vg_b40_ror(e,25u);
        uint32_t ch=(e&f)^((~e)&g);
        uint32_t t1=h+s1+ch+k[i]+w[i];
        uint32_t s0=vg_b40_ror(a,2u)^vg_b40_ror(a,13u)^vg_b40_ror(a,22u);
        uint32_t maj=(a&b)^(a&c)^(b&c);
        uint32_t t2=s0+maj;
        h=g;g=f;f=e;e=d+t1;d=c;c=b;b=a;a=t1+t2;
    }
    s->h[0]+=a;s->h[1]+=b;s->h[2]+=c;s->h[3]+=d;
    s->h[4]+=e;s->h[5]+=f;s->h[6]+=g;s->h[7]+=h;
    vg_b40_zero(w,sizeof(w));
}
static inline void vg_b40_sha_update(vg_b40_sha *s,const uint8_t *p,size_t n) {
    for(size_t i=0u;i<n;++i){
        s->buf[s->used++]=p[i];
        if(s->used==64u){vg_b40_sha_block(s,s->buf);s->used=0u;}
    }
    s->byte_count+=(uint64_t)n;
}
static inline void vg_b40_sha_final(vg_b40_sha *s,uint8_t out[32]) {
    const uint64_t bitlen=s->byte_count*8u;
    s->buf[s->used++]=0x80u;
    if(s->used>56u){while(s->used<64u)s->buf[s->used++]=0u;
        vg_b40_sha_block(s,s->buf);s->used=0u;}
    while(s->used<56u)s->buf[s->used++]=0u;
    for(unsigned int i=0u;i<8u;++i)s->buf[56u+i]=(uint8_t)(bitlen>>(56u-8u*i));
    vg_b40_sha_block(s,s->buf);
    for(unsigned int i=0u;i<8u;++i)vg_b40_put_be32(out+4u*i,s->h[i]);
    vg_b40_zero(s,sizeof(*s));
}
/* Host oracle: standard HMAC with two message fragments (no heap or OpenSSL). */
static inline bool vg_b40_hmac(const uint8_t *key,size_t keylen,
    const uint8_t *a,size_t alen,const uint8_t *b,size_t blen,uint8_t out[32]) {
    if(!key || !out || (alen && !a) || (blen && !b) || keylen>64u)return false;
    uint8_t ipad[64],opad[64],inner[32];vg_b40_sha s;
    memset(ipad,0,sizeof(ipad));memcpy(ipad,key,keylen);
    for(unsigned int i=0u;i<64u;++i){opad[i]=(uint8_t)(ipad[i]^0x5cu);
        ipad[i]=(uint8_t)(ipad[i]^0x36u);}
    vg_b40_sha_init(&s);vg_b40_sha_update(&s,ipad,sizeof(ipad));
    if(alen)vg_b40_sha_update(&s,a,alen);
    if(blen)vg_b40_sha_update(&s,b,blen);
    vg_b40_sha_final(&s,inner);
    vg_b40_sha_init(&s);vg_b40_sha_update(&s,opad,sizeof(opad));
    vg_b40_sha_update(&s,inner,sizeof(inner));vg_b40_sha_final(&s,out);
    vg_b40_zero(ipad,sizeof(ipad));vg_b40_zero(opad,sizeof(opad));
    vg_b40_zero(inner,sizeof(inner));return true;
}
static inline bool vg_b40_ct_eq32(const uint8_t *a,const uint8_t *b) {
    uint8_t difference=0u;
    for(unsigned int i=0u;i<32u;++i)difference|=(uint8_t)(a[i]^b[i]);
    return difference==0u;
}
static inline bool vg_b40_verify_host_hmac(const uint8_t *sealed,size_t sealed_len,
    const uint8_t *expected_wire,size_t wire_len,const vg_b39_scope_policy *policy,
    uint32_t purpose,uint32_t device_tag,const uint8_t *master,size_t master_len,
    uint64_t *verified_epoch) {
    static const uint8_t kdf_domain[]="VG_PHASE9_B39_SCOPE_KDF_V1";
    static const uint8_t auth_domain[]="VG_PHASE9_B39_SCOPE_AUTH_V1";
    vg_b31_region key_reg,blob_reg,wire_reg,pol_reg,out_reg;
    if(!sealed || !expected_wire || !policy || !master || !verified_epoch ||
       master_len!=32u || sealed_len!=128u || wire_len!=72u ||
       !vg_b31_region_of(master,master_len,&key_reg) ||
       !vg_b31_region_of(sealed,sealed_len,&blob_reg) ||
       !vg_b31_region_of(expected_wire,wire_len,&wire_reg) ||
       !vg_b31_region_of(policy,sizeof(*policy),&pol_reg) ||
       !vg_b31_region_of(verified_epoch,sizeof(*verified_epoch),&out_reg) ||
       vg_b31_overlaps(key_reg,blob_reg) || vg_b31_overlaps(key_reg,wire_reg) ||
       vg_b31_overlaps(key_reg,pol_reg) || vg_b31_overlaps(key_reg,out_reg))return false;
    uint64_t candidate_epoch=0u;
    if(!vg_b39_precheck_untrusted_scope(sealed,sealed_len,expected_wire,wire_len,
            policy,purpose,device_tag,&candidate_epoch))return false;
    uint8_t context[16],payload[112],scoped[32],tag[32];
    vg_b40_put_le32(context,purpose);
    vg_b40_put_le64(context+4u,policy->rotation.active_key_id);
    vg_b40_put_le32(context+12u,device_tag);
    memcpy(payload,context,sizeof(context));memcpy(payload+16u,sealed,96u);
    bool computed=vg_b40_hmac(master,master_len,kdf_domain,sizeof(kdf_domain),
                               context,sizeof(context),scoped) &&
        vg_b40_hmac(scoped,sizeof(scoped),auth_domain,sizeof(auth_domain),
                   payload,sizeof(payload),tag);
    bool accepted=computed && vg_b40_ct_eq32(tag,sealed+96u);
    vg_b40_zero(context,sizeof(context));vg_b40_zero(payload,sizeof(payload));
    vg_b40_zero(scoped,sizeof(scoped));vg_b40_zero(tag,sizeof(tag));
    if(!accepted)return false;
    *verified_epoch=candidate_epoch;
    return true;
}
#endif
