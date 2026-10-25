#ifndef VG_EVENT_COMMIT_RECEIPT_H
#define VG_EVENT_COMMIT_RECEIPT_H

#include "offline_state.h"

#define VG_EVENT_RECEIPT_LENGTH 134u
#define VG_EVENT_RECEIPT_CONTENT_TYPE "application/vnd.vgw.event-receipt-v1"

static inline bool vg_event_receipt_content_type_valid(const char *value)
{
    static const char expected[] = VG_EVENT_RECEIPT_CONTENT_TYPE;
    if (!value) return false;
    for (size_t i = 0u; i < sizeof(expected); ++i) {
        unsigned char actual = (unsigned char)value[i];
        if (actual >= (unsigned char)'A' && actual <= (unsigned char)'Z') actual += (unsigned char)('a' - 'A');
        if (actual != (unsigned char)expected[i]) return false;
    }
    return true;
}

typedef struct {
    void *context;
    bool (*sha256)(void *, const uint8_t *, size_t, uint8_t [32]);
    bool (*hmac_sha256)(void *, const uint8_t *, size_t, const uint8_t *, size_t, uint8_t [32]);
} vg_receipt_crypto;

static inline void vg_receipt_zero(void *value, size_t length)
{
    volatile uint8_t *p = (volatile uint8_t *)value;
    while (length-- != 0u) *p++ = 0u;
}

static inline bool vg_receipt_equal32(const uint8_t *a, const uint8_t *b)
{
    volatile uint8_t difference = 0u;
    for (size_t i = 0u; i < 32u; ++i) difference |= (uint8_t)(a[i] ^ b[i]);
    return difference == 0u;
}

static inline int vg_receipt_hex_digit(uint8_t c)
{
    if (c >= (uint8_t)'0' && c <= (uint8_t)'9') return (int)(c - (uint8_t)'0');
    if (c >= (uint8_t)'a' && c <= (uint8_t)'f') return (int)(c - (uint8_t)'a') + 10;
    return -1;
}

static inline bool vg_receipt_unhex32(const uint8_t *raw, uint8_t *out)
{
    for (size_t i = 0u; i < 32u; ++i) {
        int hi = vg_receipt_hex_digit(raw[i * 2u]), lo = vg_receipt_hex_digit(raw[i * 2u + 1u]);
        if (hi < 0 || lo < 0) return false;
        out[i] = (uint8_t)((unsigned)hi * 16u + (unsigned)lo);
    }
    return true;
}

/* Exact-body/status authentication, not an HTTP success or structural precheck.
 * Actual SDK uses PSA crypto; host tests use an independent reference provider.
 * Output is unchanged on every refusal and contains only a public body digest.
 * This function alone never removes a retained event or clears an alarm. */
static inline bool vg_event_receipt_verify(const vg_receipt_crypto *crypto,
    const uint8_t *bearer, size_t bearer_length, const void *body, size_t body_length,
    int status, const void *receipt, size_t receipt_length, uint8_t verified_digest[32])
{
    if (!crypto || !crypto->sha256 || !crypto->hmac_sha256 || !bearer || bearer_length < 32u ||
        bearer_length > 256u || !body || body_length == 0u || body_length > VG_OFFLINE_WIRE_MAX ||
        (status != 200 && status != 201) || !receipt || receipt_length != VG_EVENT_RECEIPT_LENGTH || !verified_digest ||
        !vg_offline_disjoint(crypto, sizeof(*crypto), verified_digest, 32u) ||
        !vg_offline_disjoint(bearer, bearer_length, verified_digest, 32u) ||
        !vg_offline_disjoint(body, body_length, verified_digest, 32u) ||
        !vg_offline_disjoint(receipt, receipt_length, verified_digest, 32u)) return false;
    const uint8_t *raw = (const uint8_t *)receipt;
    if (memcmp(raw, "VGR1:", 5u) != 0 || raw[69] != (uint8_t)':') return false;
    uint8_t claimed[32] = {0}, signature[32] = {0}, digest[32] = {0}, expected[32] = {0};
    char message[96];
    memset(message, 0, sizeof(message));
    bool valid = vg_receipt_unhex32(raw + 5u, claimed) && vg_receipt_unhex32(raw + 70u, signature) &&
        crypto->sha256(crypto->context, (const uint8_t *)body, body_length, digest) &&
        vg_receipt_equal32(claimed, digest);
    if (valid) {
        /* The bounded raw digest is already canonical lowercase hex. */
        int length = snprintf(message, sizeof(message), "VG_EVENT_COMMIT_V1\n%d\n%.*s", status, 64, (const char *)raw + 5u);
        valid = length > 0 && (size_t)length < sizeof(message) &&
            crypto->hmac_sha256(crypto->context, bearer, bearer_length,
                (const uint8_t *)message, (size_t)length, expected) && vg_receipt_equal32(signature, expected);
    }
    if (valid) memcpy(verified_digest, digest, 32u);
    vg_receipt_zero(claimed, sizeof(claimed));
    vg_receipt_zero(signature, sizeof(signature));
    vg_receipt_zero(digest, sizeof(digest));
    vg_receipt_zero(expected, sizeof(expected));
    vg_receipt_zero(message, sizeof(message));
    return valid;
}

#endif
