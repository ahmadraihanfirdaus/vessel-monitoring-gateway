#ifndef VG_ESP32_NETWORK_PROFILE_H
#define VG_ESP32_NETWORK_PROFILE_H

/* Shared, side-effect-free admission for the real ESP-IDF transport port.
 * No network, credential values, operational defaults or GPIO actions here.
 * Bounds below are implementation resource limits, not vessel policy. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "telemetry_contract.h"
#include "network_transport_host_adapter.h"

#define VG_NET_ORIGIN_MAX 192u
#define VG_NET_TOKEN_MAX 256u
#define VG_NET_BODY_MAX 4096u
#define VG_NET_REPLY_MAX 512u
#define VG_NET_URL_MAX 224u
#define VG_NET_POLICY_MS_MAX 60000u
#define VG_NET_ATTEMPTS_MAX 16u

typedef enum { VG_NET_TELEMETRY = 1, VG_NET_EVENT = 2 } vg_net_kind;
typedef struct {
    char ssid[33];
    char wifi_password[65];
    char origin[VG_NET_ORIGIN_MAX + 1u];
    char bearer[VG_NET_TOKEN_MAX + 1u];
    char device_id[VG_TELEMETRY_MAX_ID_LEN + 1u];
    net001_host_policy policy;
} vg_net_profile;

static inline size_t vg_net_length(const char *s, size_t bound)
{
    size_t n = 0u;
    if (!s) return bound;
    while (n < bound && s[n]) ++n;
    return n;
}

static inline bool vg_net_origin_valid(const char *origin)
{
    size_t n = vg_net_length(origin, VG_NET_ORIGIN_MAX + 1u);
    if (n < 9u || n > VG_NET_ORIGIN_MAX || memcmp(origin, "https://", 8u)) return false;
    /* An origin only. Fixed API paths are appended; no userinfo, redirects,
     * query/fragment, whitespace, percent-escaped authority or backslashes. */
    size_t end = n;
    if (origin[end - 1u] == '/') --end;
    if (end <= 8u) return false;
    for (size_t i = 8u; i < end; ++i) {
        unsigned char c = (unsigned char)origin[i];
        if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
              (c >= '0' && c <= '9') || c == '.' || c == '-' || c == ':' || c == '[' || c == ']')) return false;
    }
    /* Validate port and authority shape without resolving DNS or accepting
     * a second URL. The SDK still parses the URL and verifies the hostname. */
    size_t port = end, host_end = end;
    if (origin[8] == '[') {
        size_t close = 9u;
        while (close < end && origin[close] != ']') ++close;
        if (close == end || close == 9u) return false;
        for (size_t i = 9u; i < close; ++i) {
            char c = origin[i];
            if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') ||
                  (c >= 'A' && c <= 'F') || c == ':' || c == '.')) return false;
        }
        if (close + 1u < end) {
            if (origin[close + 1u] != ':') return false;
            port = close + 2u;
        }
    } else {
        for (size_t i = 8u; i < end; ++i) {
            if (origin[i] == ':') { host_end = i; port = i + 1u; break; }
            if (origin[i] == '[' || origin[i] == ']') return false;
        }
        if (host_end == 8u || origin[8] == '.' || origin[8] == '-' ||
            origin[host_end - 1u] == '.' || origin[host_end - 1u] == '-') return false;
        for (size_t i = 9u; i < host_end; ++i) if (origin[i] == '.' && origin[i - 1u] == '.') return false;
    }
    if (port != end) {
        unsigned number = 0u;
        for (size_t i = port; i < end; ++i) {
            if (origin[i] < '0' || origin[i] > '9') return false;
            number = number * 10u + (unsigned)(origin[i] - '0');
            if (number > 65535u) return false;
        }
        if (number == 0u) return false;
    } else if (origin[end - 1u] == ':') return false;
    return true;
}

static inline bool vg_net_profile_valid(const vg_net_profile *p)
{
    if (!p || vg_net_length(p->ssid, sizeof(p->ssid)) == 0u ||
        vg_net_length(p->ssid, sizeof(p->ssid)) >= sizeof(p->ssid)) return false;
    size_t password_len = vg_net_length(p->wifi_password, sizeof(p->wifi_password));
    if (password_len < 8u || password_len > 63u || !vg_net_origin_valid(p->origin) ||
        !vg_tel_safe_token(p->device_id, VG_TELEMETRY_MAX_ID_LEN)) return false;
    size_t token_len = vg_net_length(p->bearer, sizeof(p->bearer));
    if (token_len < 32u || token_len > VG_NET_TOKEN_MAX) return false;
    for (size_t i = 0u; i < token_len; ++i) {
        unsigned char c = (unsigned char)p->bearer[i];
        if (!((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
              (c >= '0' && c <= '9') || c == '-' || c == '_' || c == '.' || c == '~' ||
              c == '+' || c == '/' || c == '=')) return false;
    }
    return p->policy.connect_timeout_ms > 0u && p->policy.connect_timeout_ms <= VG_NET_POLICY_MS_MAX &&
        p->policy.reconnect_backoff_ms > 0u && p->policy.reconnect_backoff_ms <= VG_NET_POLICY_MS_MAX &&
        p->policy.max_attempts > 0u && p->policy.max_attempts <= VG_NET_ATTEMPTS_MAX;
}

static inline bool vg_net_job_valid(vg_net_kind kind, const void *body, size_t length)
{
    return (kind == VG_NET_TELEMETRY || kind == VG_NET_EVENT) && body && length > 0u && length <= VG_NET_BODY_MAX;
}

static inline bool vg_net_reply_append(char *out, size_t *used, const void *bytes, size_t length)
{
    if (!out || !used || *used > VG_NET_REPLY_MAX || length > VG_NET_REPLY_MAX - *used ||
        (!bytes && length != 0u)) return false;
    if (length != 0u) memcpy(out + *used, bytes, length);
    *used += length;
    out[*used] = '\0';
    return true;
}

static inline bool vg_net_http_retryable(bool transport_completed, int status, bool response_overflow)
{
    if (response_overflow || status < 0 || status > 599) return false;
    if (status == 408 || status == 429 || status >= 500) return true;
    return !transport_completed && (status == 0 || status == 200 || status == 201);
}

#endif
