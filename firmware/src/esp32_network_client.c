#ifdef ESP_PLATFORM

#include "esp32_network_client.h"
#include "psa/crypto.h"
#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include "esp_crt_bundle.h"
#include "esp_event.h"
#include "esp_http_client.h"
#include "esp_netif.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "esp_wifi_default.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "mbedtls/platform_util.h"
#include "nvs.h"
#include "nvs_flash.h"

#define NET_IP_BIT BIT0
#define NET_DOWN_BIT BIT1
#define NET_HALT_BIT BIT2
#define NET_WORKER_STACK 8192u
#define NET_POLL_MS 20u

typedef struct {
    vg_net_kind kind;
    uint64_t tag;
    size_t length;
    unsigned char body[VG_NET_BODY_MAX];
} net_job;
typedef struct {
    vg_net_profile profile;
    net001_host_adapter adapter;
    EventGroupHandle_t link;
    QueueHandle_t jobs;
    QueueHandle_t results;
    SemaphoreHandle_t submit_lock;
    TaskHandle_t task;
    esp_netif_t *netif;
    esp_event_handler_instance_t wifi_handler;
    esp_event_handler_instance_t ip_handler;
    bool owns_loop;
    bool wifi_initialized;
    bool sta_attached;
    bool wifi_registered;
    bool ip_registered;
    /* Dedicated worker storage, not 4 KiB payloads on acquisition/task stacks. */
    net_job active;
    net_job staging;
    vg_net_completion completion;
    bool response_overflow;
    uint8_t receipt_media_headers;
} net_client;

static net_client *client;

static TickType_t wait_ticks(uint32_t ms)
{
    TickType_t ticks = pdMS_TO_TICKS(ms);
    return ticks > 0 ? ticks : 1;
}

static bool read_string(nvs_handle_t handle, const char *key, char *out, size_t capacity)
{
    size_t size = capacity;
    return nvs_get_str(handle, key, out, &size) == ESP_OK && size > 1u && size <= capacity;
}

vg_net_profile_result vg_net_load_profile(vg_net_profile *out)
{
    if (!out) return VG_NET_PROFILE_INVALID;
    /* Never use the common erase-on-init-error example: preserve existing NVS. */
    if (nvs_flash_init() != ESP_OK) return VG_NET_PROFILE_STORAGE_ERROR;
    nvs_handle_t handle;
    esp_err_t opened = nvs_open("vgw_net", NVS_READONLY, &handle);
    if (opened == ESP_ERR_NVS_NOT_FOUND) return VG_NET_PROFILE_ABSENT;
    if (opened != ESP_OK) return VG_NET_PROFILE_STORAGE_ERROR;
    vg_net_profile candidate = {0};
    bool valid = read_string(handle, "ssid", candidate.ssid, sizeof(candidate.ssid)) &&
        read_string(handle, "wifi_pass", candidate.wifi_password, sizeof(candidate.wifi_password)) &&
        read_string(handle, "origin", candidate.origin, sizeof(candidate.origin)) &&
        read_string(handle, "bearer", candidate.bearer, sizeof(candidate.bearer)) &&
        read_string(handle, "device", candidate.device_id, sizeof(candidate.device_id)) &&
        nvs_get_u32(handle, "timeout_ms", &candidate.policy.connect_timeout_ms) == ESP_OK &&
        nvs_get_u32(handle, "backoff_ms", &candidate.policy.reconnect_backoff_ms) == ESP_OK &&
        nvs_get_u32(handle, "attempts", &candidate.policy.max_attempts) == ESP_OK &&
        vg_net_profile_valid(&candidate);
    nvs_close(handle);
    if (valid) *out = candidate;
    mbedtls_platform_zeroize(&candidate, sizeof(candidate));
    return valid ? VG_NET_PROFILE_READY : VG_NET_PROFILE_INVALID;
}

static void on_link(void *arg, esp_event_base_t base, int32_t id, void *event_data)
{
    (void)event_data;
    net_client *ctx = arg;
    if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        xEventGroupClearBits(ctx->link, NET_DOWN_BIT);
        xEventGroupSetBits(ctx->link, NET_IP_BIT);
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        xEventGroupClearBits(ctx->link, NET_IP_BIT);
        xEventGroupSetBits(ctx->link, NET_DOWN_BIT);
    }
}

static bool begin_link(void *arg)
{
    net_client *ctx = arg;
    xEventGroupClearBits(ctx->link, NET_DOWN_BIT | NET_IP_BIT);
    return esp_wifi_connect() == ESP_OK;
}
static net001_host_link observe_link(void *arg)
{
    net_client *ctx = arg;
    EventBits_t bits = xEventGroupGetBits(ctx->link);
    if (bits & NET_IP_BIT) return NET001_LINK_UP;
    return bits & NET_DOWN_BIT ? NET001_LINK_DOWN : NET001_LINK_PENDING;
}
static void cancel_link(void *arg)
{
    (void)arg;
    (void)esp_wifi_disconnect();
}

static bool wait_for_link(net_client *ctx)
{
    while (!ctx->adapter.exhausted) {
        if (ulTaskNotifyTake(pdTRUE, 0) != 0u) {
            net001_host_reset(&ctx->adapter);
            xEventGroupClearBits(ctx->link, NET_HALT_BIT);
        }
        uint32_t now = (uint32_t)((uint64_t)esp_timer_get_time() / 1000u);
        if (net001_host_step(&ctx->adapter, now) == NET001_HOST_READY) return true;
        vTaskDelay(wait_ticks(NET_POLL_MS));
    }
    return false;
}

static esp_err_t on_http(esp_http_client_event_t *event)
{
    net_client *ctx = event->user_data;
    if (event->event_id == HTTP_EVENT_ON_HEADER && event->header_key &&
        strcasecmp(event->header_key, "Content-Type") == 0) {
        if (ctx->receipt_media_headers < 2u) ++ctx->receipt_media_headers;
        ctx->completion.event_receipt_media_valid = ctx->receipt_media_headers == 1u &&
            vg_event_receipt_content_type_valid(event->header_value);
    }
    if (event->event_id == HTTP_EVENT_ON_DATA) {
        if (event->data_len < 0 || !vg_net_reply_append(ctx->completion.response,
            &ctx->completion.response_length, event->data, (size_t)event->data_len)) {
            ctx->response_overflow = true;
            return ESP_FAIL;
        }
    }
    return ESP_OK;
}

static bool perform_once(net_client *ctx)
{
    char url[VG_NET_URL_MAX];
    char authorization[VG_NET_TOKEN_MAX + 8u];
    size_t origin_len = strlen(ctx->profile.origin);
    if (ctx->profile.origin[origin_len - 1u] == '/') --origin_len;
    const char *path = ctx->active.kind == VG_NET_TELEMETRY ? "/api/v1/telemetry" : "/api/v1/events";
    int written = snprintf(url, sizeof(url), "%.*s%s", (int)origin_len, ctx->profile.origin, path);
    if (written < 0 || (size_t)written >= sizeof(url)) return false;
    written = snprintf(authorization, sizeof(authorization), "Bearer %s", ctx->profile.bearer);
    if (written < 0 || (size_t)written >= sizeof(authorization)) return false;
    ctx->completion.response_length = 0u;
    ctx->completion.response[0] = '\0';
    ctx->completion.http_status = 0;
    ctx->response_overflow = false;
    ctx->receipt_media_headers = 0u;
    ctx->completion.event_receipt_media_valid = false;
    esp_http_client_config_t configuration = {
        .url = url,
        .method = HTTP_METHOD_POST,
        .transport_type = HTTP_TRANSPORT_OVER_SSL,
        .timeout_ms = (int)ctx->profile.policy.connect_timeout_ms,
        .is_async = true,
        .disable_auto_redirect = true,
        .max_authorization_retries = -1,
        .skip_cert_common_name_check = false,
        .crt_bundle_attach = esp_crt_bundle_attach,
        .event_handler = on_http,
        .user_data = ctx,
    };
    esp_http_client_handle_t http = esp_http_client_init(&configuration);
    if (!http) {
        mbedtls_platform_zeroize(authorization, sizeof(authorization));
        return false;
    }
    bool configured = esp_http_client_set_header(http, "Content-Type", "application/json") == ESP_OK &&
        esp_http_client_set_header(http, "Accept", "application/json") == ESP_OK &&
        esp_http_client_set_header(http, "Authorization", authorization) == ESP_OK &&
        esp_http_client_set_post_field(http, (const char *)ctx->active.body, (int)ctx->active.length) == ESP_OK;
    if (configured && ctx->active.kind == VG_NET_EVENT)
        configured = esp_http_client_set_header(http, "X-VG-Event-Receipt", "1") == ESP_OK;
    esp_err_t result = ESP_FAIL;
    if (configured) {
        int64_t started = esp_timer_get_time();
        for (;;) {
            int64_t now = esp_timer_get_time();
            if (started < 0 || now < started || (uint64_t)(now - started) >=
                (uint64_t)ctx->profile.policy.connect_timeout_ms * 1000u) {
                result = ESP_ERR_TIMEOUT;
                break;
            }
            result = esp_http_client_perform(http);
            if (result != ESP_ERR_HTTP_EAGAIN || ctx->response_overflow) break;
            vTaskDelay(wait_ticks(NET_POLL_MS));
        }
    }
    ctx->completion.http_status = esp_http_client_get_status_code(http);
    esp_http_client_cleanup(http);
    mbedtls_platform_zeroize(authorization, sizeof(authorization));
    return result == ESP_OK && !ctx->response_overflow;
}

static void worker(void *arg)
{
    net_client *ctx = arg;
    for (;;) {
        if (ulTaskNotifyTake(pdTRUE, 0) != 0u) {
            net001_host_reset(&ctx->adapter);
            xEventGroupClearBits(ctx->link, NET_HALT_BIT);
        }
        if (xQueueReceive(ctx->jobs, &ctx->active, wait_ticks(NET_POLL_MS)) != pdTRUE) continue;
        memset(&ctx->completion, 0, sizeof(ctx->completion));
        ctx->completion.tag = ctx->active.tag;
        for (uint32_t attempt = 0u; attempt < ctx->profile.policy.max_attempts; ++attempt) {
            if (xEventGroupGetBits(ctx->link) & NET_HALT_BIT) break;
            if (!wait_for_link(ctx)) break;
            bool received = perform_once(ctx);
            int status = ctx->completion.http_status;
            if (received && (status == 200 || status == 201)) {
                ctx->completion.completed = true;
                break;
            }
            /* No redirect following or credential retries. Permanent schema,
             * identity/conflict and auth failures require caller intervention. */
            if (!vg_net_http_retryable(received, status, ctx->response_overflow)) break;
            if (attempt + 1u < ctx->profile.policy.max_attempts) vTaskDelay(wait_ticks(ctx->profile.policy.reconnect_backoff_ms));
        }
        if (!ctx->completion.completed) xEventGroupSetBits(ctx->link, NET_HALT_BIT);
        /* Backpressure waits only in this worker. Acquisition never waits for
         * a result consumer; its zero-wait job submission can return false. */
        (void)xQueueSend(ctx->results, &ctx->completion, portMAX_DELAY);
        mbedtls_platform_zeroize(&ctx->active, sizeof(ctx->active));
    }
}

static void release_failed_start(net_client *ctx)
{
    if (ctx->wifi_initialized) { (void)esp_wifi_stop(); (void)esp_wifi_deinit(); }
    if (ctx->wifi_registered) (void)esp_event_handler_instance_unregister(WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, ctx->wifi_handler);
    if (ctx->ip_registered) (void)esp_event_handler_instance_unregister(IP_EVENT, IP_EVENT_STA_GOT_IP, ctx->ip_handler);
    if (ctx->sta_attached) (void)esp_wifi_clear_default_wifi_driver_and_handlers(ctx->netif);
    if (ctx->netif) esp_netif_destroy(ctx->netif);
    if (ctx->owns_loop) (void)esp_event_loop_delete_default();
    if (ctx->link) vEventGroupDelete(ctx->link);
    if (ctx->jobs) vQueueDelete(ctx->jobs);
    if (ctx->results) vQueueDelete(ctx->results);
    if (ctx->submit_lock) vSemaphoreDelete(ctx->submit_lock);
    mbedtls_platform_zeroize(ctx, sizeof(*ctx));
    free(ctx);
}

bool vg_net_start(const vg_net_profile *profile)
{
    if (client || !vg_net_profile_valid(profile)) return false;
#if !CONFIG_MBEDTLS_CERTIFICATE_BUNDLE || !CONFIG_ESP_HTTP_CLIENT_ENABLE_HTTPS || \
    !CONFIG_MBEDTLS_HAVE_TIME_DATE || CONFIG_ESP_TLS_INSECURE || CONFIG_ESP_TLS_SKIP_SERVER_CERT_VERIFY
    return false; /* Never silently downgrade TLS validation. */
#endif
    wifi_mode_t existing;
    if (esp_wifi_get_mode(&existing) != ESP_ERR_WIFI_NOT_INIT) return false;
    net_client *ctx = calloc(1u, sizeof(*ctx));
    if (!ctx) return false;
    ctx->profile = *profile;
    ctx->link = xEventGroupCreate();
    ctx->jobs = xQueueCreate(1u, sizeof(net_job));
    ctx->results = xQueueCreate(1u, sizeof(vg_net_completion));
    ctx->submit_lock = xSemaphoreCreateMutex();
    if (!ctx->link || !ctx->jobs || !ctx->results || !ctx->submit_lock) goto failed;
    esp_err_t result = esp_netif_init();
    if (result != ESP_OK && result != ESP_ERR_INVALID_STATE) goto failed;
    result = esp_event_loop_create_default();
    if (result != ESP_OK && result != ESP_ERR_INVALID_STATE) goto failed;
    ctx->owns_loop = result == ESP_OK;
    esp_netif_config_t interface = ESP_NETIF_DEFAULT_WIFI_STA();
    ctx->netif = esp_netif_new(&interface);
    if (!ctx->netif || esp_netif_attach_wifi_station(ctx->netif) != ESP_OK) goto failed;
    ctx->sta_attached = true;
    if (esp_wifi_set_default_wifi_sta_handlers() != ESP_OK) goto failed;
    wifi_init_config_t init = WIFI_INIT_CONFIG_DEFAULT();
    if (esp_wifi_init(&init) != ESP_OK) goto failed;
    ctx->wifi_initialized = true;
    if (esp_wifi_set_storage(WIFI_STORAGE_RAM) != ESP_OK) goto failed;
    wifi_config_t wifi = {0};
    memcpy(wifi.sta.ssid, profile->ssid, strlen(profile->ssid));
    memcpy(wifi.sta.password, profile->wifi_password, strlen(profile->wifi_password));
    wifi.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;
    result = esp_wifi_set_mode(WIFI_MODE_STA);
    if (result == ESP_OK) result = esp_wifi_set_config(WIFI_IF_STA, &wifi);
    mbedtls_platform_zeroize(&wifi, sizeof(wifi));
    if (result != ESP_OK) goto failed;
    if (esp_event_handler_instance_register(WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, on_link, ctx, &ctx->wifi_handler) != ESP_OK) goto failed;
    ctx->wifi_registered = true;
    if (esp_event_handler_instance_register(IP_EVENT, IP_EVENT_STA_GOT_IP, on_link, ctx, &ctx->ip_handler) != ESP_OK) goto failed;
    ctx->ip_registered = true;
    net001_host_driver driver = {ctx, begin_link, observe_link, cancel_link};
    if (!net001_host_init(&ctx->adapter, profile->policy, driver) || esp_wifi_start() != ESP_OK) goto failed;
    if (xTaskCreate(worker, "vgw_https", NET_WORKER_STACK, ctx, 1u, &ctx->task) != pdPASS) goto failed;
    client = ctx;
    return true;
failed:
    release_failed_start(ctx);
    return false;
}

bool vg_net_submit(vg_net_kind kind, const void *body, size_t length, uint64_t tag)
{
    if (!client || !vg_net_job_valid(kind, body, length) || (xEventGroupGetBits(client->link) & NET_HALT_BIT)) return false;
    /* Fixed heap-owned staging avoids a 4 KiB acquisition stack object. Both
     * lock and queue have zero wait; concurrent/full submissions fail visibly. */
    if (xSemaphoreTake(client->submit_lock, 0) != pdTRUE) return false;
    memset(&client->staging, 0, sizeof(client->staging));
    client->staging.kind = kind;
    client->staging.tag = tag;
    client->staging.length = length;
    memcpy(client->staging.body, body, length);
    bool submitted = xQueueSend(client->jobs, &client->staging, 0) == pdTRUE;
    mbedtls_platform_zeroize(&client->staging, sizeof(client->staging));
    (void)xSemaphoreGive(client->submit_lock);
    return submitted;
}

bool vg_net_take_completion(vg_net_completion *out)
{
    return client && out && xQueueReceive(client->results, out, 0) == pdTRUE;
}

bool vg_net_request_reset(void)
{
    return client && xTaskNotifyGive(client->task) == pdPASS;
}

static bool receipt_sha256(void *context, const uint8_t *body, size_t length, uint8_t out[32])
{
    (void)context;
    size_t written = 0u;
    return psa_crypto_init() == PSA_SUCCESS &&
        psa_hash_compute(PSA_ALG_SHA_256, body, length, out, 32u, &written) == PSA_SUCCESS && written == 32u;
}

static bool receipt_hmac_sha256(void *context, const uint8_t *key, size_t key_length,
    const uint8_t *message, size_t message_length, uint8_t out[32])
{
    (void)context;
    if (psa_crypto_init() != PSA_SUCCESS) return false;
    psa_key_attributes_t attributes = PSA_KEY_ATTRIBUTES_INIT;
    psa_set_key_lifetime(&attributes, PSA_KEY_LIFETIME_VOLATILE);
    psa_set_key_type(&attributes, PSA_KEY_TYPE_HMAC);
    psa_set_key_bits(&attributes, key_length * 8u);
    psa_set_key_usage_flags(&attributes, PSA_KEY_USAGE_SIGN_MESSAGE);
    psa_set_key_algorithm(&attributes, PSA_ALG_HMAC(PSA_ALG_SHA_256));
    mbedtls_svc_key_id_t handle = MBEDTLS_SVC_KEY_ID_INIT;
    psa_status_t imported = psa_import_key(&attributes, key, key_length, &handle);
    psa_reset_key_attributes(&attributes);
    if (imported != PSA_SUCCESS) return false;
    size_t written = 0u;
    psa_status_t computed = psa_mac_compute(handle, PSA_ALG_HMAC(PSA_ALG_SHA_256),
        message, message_length, out, 32u, &written);
    psa_status_t destroyed = psa_destroy_key(handle);
    return computed == PSA_SUCCESS && destroyed == PSA_SUCCESS && written == 32u;
}

bool vg_net_verify_event_receipt(const void *body, size_t body_length, int status,
    const void *receipt, size_t receipt_length, uint8_t verified_digest[32])
{
    if (!client) return false;
    const vg_receipt_crypto crypto = {NULL, receipt_sha256, receipt_hmac_sha256};
    return vg_event_receipt_verify(&crypto, (const uint8_t *)client->profile.bearer,
        vg_net_length(client->profile.bearer, VG_NET_TOKEN_MAX + 1u), body, body_length,
        status, receipt, receipt_length, verified_digest);
}

#endif
