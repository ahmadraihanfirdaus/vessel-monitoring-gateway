#ifndef VG_ESP32_NETWORK_CLIENT_H
#define VG_ESP32_NETWORK_CLIENT_H

#include "esp32_network_profile.h"
#include "event_commit_receipt.h"

typedef enum {
    VG_NET_PROFILE_ABSENT = 0, VG_NET_PROFILE_READY,
    VG_NET_PROFILE_INVALID, VG_NET_PROFILE_STORAGE_ERROR
} vg_net_profile_result;
typedef struct {
    uint64_t tag;
    bool completed;
    int http_status;
    size_t response_length;
    char response[VG_NET_REPLY_MAX + 1u];
    bool event_receipt_media_valid; /* Structural media check, not authentication. */
} vg_net_completion;

#ifdef ESP_PLATFORM
/* Startup-only, single caller. NVS read only; never erases a partition or logs
 * credentials. No profile means transport disabled, not a sampling failure. */
vg_net_profile_result vg_net_load_profile(vg_net_profile *out);
bool vg_net_start(const vg_net_profile *profile);
/* Bounded copies, zero queue wait. On false the caller retains its data.
 * Completed HTTP is not an authenticated application receipt and never
 * automatically removes latest state or critical journal entries. */
bool vg_net_submit(vg_net_kind kind, const void *body, size_t length, uint64_t tag);
bool vg_net_take_completion(vg_net_completion *out);
/* Explicitly reset an exhausted connection cycle; nonblocking task notification. */
bool vg_net_request_reset(void);
/* Worker-side standard crypto only, no network IO. Verifies an exact-body,
 * status-bound application receipt with the immutable external device bearer.
 * No secret leaves this module; success is not a storage deletion by itself. */
bool vg_net_verify_event_receipt(const void *body, size_t body_length, int status,
    const void *receipt, size_t receipt_length, uint8_t verified_digest[32]);
#endif

#endif
