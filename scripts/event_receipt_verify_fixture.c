/* CLI-only host cryptographic interop. Credential input is process environment,
 * never argv/file/output. No database or production SDK crypto claim. */
#include <stdlib.h>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
#include "event_receipt_native_crypto.h"

static uint8_t body[VG_OFFLINE_WIRE_MAX], receipt[512];

static uint32_t little32(const uint8_t *value)
{
    return (uint32_t)value[0] | ((uint32_t)value[1] << 8u) |
        ((uint32_t)value[2] << 16u) | ((uint32_t)value[3] << 24u);
}

int main(int argc, char **argv)
{
    if (argc != 2 || (strcmp(argv[1], "200") && strcmp(argv[1], "201"))) return 3;
#ifdef _WIN32
    if (_setmode(_fileno(stdin), _O_BINARY) == -1) return 3;
#endif
    const char *bearer = getenv("VG_LIVE_DEVICE_TOKEN");
    if (!bearer) return 3;
    size_t key_length = 0u;
    while (key_length <= 256u && bearer[key_length]) ++key_length;
    if (key_length < 32u || key_length > 256u) return 3;
    uint8_t header[8], digest[32];
    if (fread(header, 1u, sizeof(header), stdin) != sizeof(header)) return 3;
    size_t body_length = little32(header), receipt_length = little32(header + 4u);
    if (!body_length || body_length > sizeof(body) || receipt_length > sizeof(receipt) ||
        fread(body, 1u, body_length, stdin) != body_length ||
        fread(receipt, 1u, receipt_length, stdin) != receipt_length || fgetc(stdin) != EOF) return 3;
    const vg_receipt_crypto crypto = vg_receipt_native_provider();
    bool verified = vg_event_receipt_verify(&crypto, (const uint8_t *)bearer, key_length,
        body, body_length, atoi(argv[1]), receipt, receipt_length, digest);
    vg_receipt_zero(digest, sizeof(digest));
    vg_receipt_zero(body, sizeof(body));
    vg_receipt_zero(receipt, sizeof(receipt));
    puts(verified ? "VERIFIED" : "REFUSED");
    return verified ? 0 : 3;
}
