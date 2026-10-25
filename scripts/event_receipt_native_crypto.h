#ifndef VG_EVENT_RECEIPT_NATIVE_CRYPTO_H
#define VG_EVENT_RECEIPT_NATIVE_CRYPTO_H

/* Host reference provider only. Production ESP-IDF uses PSA in the actual
 * network module, never this header. Reuse the existing tested SHA/HMAC math. */
#include "event_commit_receipt.h"
#include "phase9_b40_hmac_verify_host.h"

static inline bool vg_receipt_native_sha256(void *context, const uint8_t *body,
    size_t length, uint8_t out[32])
{
    (void)context;
    if (!body || !out) return false;
    vg_b40_sha state;
    vg_b40_sha_init(&state);
    vg_b40_sha_update(&state, body, length);
    vg_b40_sha_final(&state, out);
    return true;
}

static inline bool vg_receipt_native_hmac(void *context, const uint8_t *key, size_t key_length,
    const uint8_t *message, size_t message_length, uint8_t out[32])
{
    (void)context;
    if (!key || !out || !message || key_length > 256u) return false;
    uint8_t normalized[32];
    const uint8_t *input = key;
    size_t input_length = key_length;
    if (key_length > 64u) {
        if (!vg_receipt_native_sha256(NULL, key, key_length, normalized)) return false;
        input = normalized;
        input_length = sizeof(normalized);
    }
    bool valid = vg_b40_hmac(input, input_length, message, message_length, NULL, 0u, out);
    vg_receipt_zero(normalized, sizeof(normalized));
    return valid;
}

static inline vg_receipt_crypto vg_receipt_native_provider(void)
{
    const vg_receipt_crypto provider = {NULL, vg_receipt_native_sha256, vg_receipt_native_hmac};
    return provider;
}

#endif
