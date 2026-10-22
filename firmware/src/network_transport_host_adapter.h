#ifndef NET001_NETWORK_TRANSPORT_HOST_ADAPTER_H
#define NET001_NETWORK_TRANSPORT_HOST_ADAPTER_H
/*
 * Phase 9 NET-001 — off-repository HOST-ONLY proposal.
 * NO ESP-IDF / Wi-Fi / HTTP / TLS / endpoint / credentials implementation.
 * NO source integration, safety-engine integration, or production approval.
 *
 * All injected driver callbacks MUST return immediately (nonblocking contract).
 * The caller supplies a monotonic uint32_t millisecond tick to each step.
 * The caller supplies every numerical policy; this header has no defaults.
 * Time subtraction handles one uint32_t wrap; call often enough to avoid
 * an unobserved full tick period between relevant state observations.
 *
 * At most one state transition and at most two bounded callback invocations
 * occur in a call to net001_host_step; there is no wait/retry loop.
 */
#include <stdbool.h>
#include <stdint.h>

typedef enum {
    NET001_HOST_IDLE = 0,
    NET001_HOST_CONNECTING,
    NET001_HOST_READY,
    NET001_HOST_BACKOFF
} net001_host_state;

typedef enum {
    NET001_LINK_PENDING = 0,
    NET001_LINK_UP,
    NET001_LINK_DOWN,
    NET001_LINK_ERROR
} net001_host_link;

typedef struct {
    /* Values are mandatory external policy (TBD until approved). */
    uint32_t connect_timeout_ms;
    uint32_t reconnect_backoff_ms;
    uint32_t max_attempts;
} net001_host_policy;

typedef struct {
    void *context;
    /* begin/observe/cancel are REQUIRED nonblocking host/test callbacks. */
    bool (*begin)(void *context);
    net001_host_link (*observe)(void *context);
    void (*cancel)(void *context);
} net001_host_driver;

typedef struct {
    net001_host_state state;
    net001_host_policy policy;
    net001_host_driver driver;
    uint32_t state_since_ms;
    uint32_t attempts_in_cycle;
    bool exhausted;
    bool initialized;
} net001_host_adapter;

static inline bool net001_host_init(net001_host_adapter *adapter,
                                    net001_host_policy policy,
                                    net001_host_driver driver)
{
    if (!adapter || !driver.begin || !driver.observe || !driver.cancel ||
        policy.connect_timeout_ms == 0u ||
        policy.reconnect_backoff_ms == 0u || policy.max_attempts == 0u) {
        return false;
    }
    adapter->state = NET001_HOST_IDLE;
    adapter->policy = policy;
    adapter->driver = driver;
    adapter->state_since_ms = 0u;
    adapter->attempts_in_cycle = 0u;
    adapter->exhausted = false;
    adapter->initialized = true;
    return true;
}

/* Stop and reset are explicit caller operations; no automatic retry after
 * exhaustion. Cancelling is a nonblocking *driver contract*, not a guarantee
 * about arbitrary external implementations. */
static inline void net001_host_reset(net001_host_adapter *adapter)
{
    if (!adapter || !adapter->initialized) return;
    if (adapter->state == NET001_HOST_CONNECTING ||
        adapter->state == NET001_HOST_READY) {
        adapter->driver.cancel(adapter->driver.context);
    }
    adapter->state = NET001_HOST_IDLE;
    adapter->state_since_ms = 0u;
    adapter->attempts_in_cycle = 0u;
    adapter->exhausted = false;
}

static inline void net001_host_failed_attempt(net001_host_adapter *adapter,
                                               uint32_t now_ms)
{
    adapter->state_since_ms = now_ms;
    if (adapter->attempts_in_cycle >= adapter->policy.max_attempts) {
        adapter->state = NET001_HOST_IDLE;
        adapter->exhausted = true;
    } else {
        adapter->state = NET001_HOST_BACKOFF;
    }
}

static inline net001_host_state net001_host_step(net001_host_adapter *adapter,
                                                 uint32_t now_ms)
{
    net001_host_link link;
    if (!adapter || !adapter->initialized)
        return NET001_HOST_IDLE;
    if (adapter->exhausted)
        return adapter->state;

    switch (adapter->state) {
    case NET001_HOST_IDLE:
        if (adapter->attempts_in_cycle >= adapter->policy.max_attempts) {
            adapter->exhausted = true;
            break;
        }
        adapter->attempts_in_cycle++;
        adapter->state_since_ms = now_ms;
        if (adapter->driver.begin(adapter->driver.context)) {
            adapter->state = NET001_HOST_CONNECTING;
        } else {
            net001_host_failed_attempt(adapter, now_ms);
        }
        break;
    case NET001_HOST_CONNECTING:
        link = adapter->driver.observe(adapter->driver.context);
        if (link == NET001_LINK_UP) {
            adapter->state = NET001_HOST_READY;
            adapter->attempts_in_cycle = 0u;
        } else if (link == NET001_LINK_ERROR || link == NET001_LINK_DOWN ||
                   (uint32_t)(now_ms - adapter->state_since_ms) >=
                       adapter->policy.connect_timeout_ms) {
            adapter->driver.cancel(adapter->driver.context);
            net001_host_failed_attempt(adapter, now_ms);
        }
        break;
    case NET001_HOST_READY:
        link = adapter->driver.observe(adapter->driver.context);
        if (link != NET001_LINK_UP) {
            adapter->driver.cancel(adapter->driver.context);
            adapter->state_since_ms = now_ms;
            adapter->attempts_in_cycle = 0u; /* fresh reconnect cycle */
            adapter->state = NET001_HOST_BACKOFF;
        }
        break;
    case NET001_HOST_BACKOFF:
        if ((uint32_t)(now_ms - adapter->state_since_ms) >=
            adapter->policy.reconnect_backoff_ms) {
            adapter->state = NET001_HOST_IDLE;
        }
        break;
    default:
        adapter->exhausted = true;
        adapter->state = NET001_HOST_IDLE;
        break;
    }
    return adapter->state;
}

#endif /* NET001_NETWORK_TRANSPORT_HOST_ADAPTER_H */
