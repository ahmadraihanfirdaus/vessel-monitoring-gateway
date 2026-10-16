#ifndef VG_NAVIGATION_NMEA_H
#define VG_NAVIGATION_NMEA_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "core_types.h"

/*
 * Phase 7 G1 navigation development foundation.
 *
 * This is a narrow NMEA 0183-style development subset using an RMC-shaped
 * sentence to exercise checksum, parsing/generation, navigation state, and
 * data-age behavior. Furuno GP-39 is a requirements reference only; this code
 * does not claim GP-39 hardware is installed, connected, or compatibility-
 * verified. Physical GNSS/NMEA acquisition is outside this gate.
 */

#define VG_NAV_SENTENCE_MAX 128u

typedef enum {
    VG_NAV_AGE_UNKNOWN = 0,
    VG_NAV_AGE_VALID,
    VG_NAV_AGE_STALE,
    VG_NAV_AGE_OFFLINE
} vg_nav_age_state_t;

typedef struct {
    uint64_t stale_after_ms;
    uint64_t offline_after_ms;
} vg_nav_age_thresholds_t;

typedef struct {
    bool initialized;
    vg_source_mode_t source_mode;
    double latitude_deg;
    double longitude_deg;
    float sog_knots;
    float cog_deg;
    bool fix_valid;
    uint64_t last_valid_ms;
    uint64_t data_age_ms;
    vg_nav_age_state_t age_state;
    vg_data_quality_t quality;
} vg_navigation_state_t;

typedef struct {
    double latitude_deg;
    double longitude_deg;
    float sog_knots;
    float cog_deg;
    bool fix_valid;
} vg_nav_rmc_data_t;

static inline bool vg_nav_age_state_is_known(vg_nav_age_state_t state)
{
    return state == VG_NAV_AGE_VALID ||
           state == VG_NAV_AGE_STALE ||
           state == VG_NAV_AGE_OFFLINE;
}

static inline bool vg_nav_source_mode_supported(vg_source_mode_t mode)
{
    return mode == VG_SOURCE_SIMULATION || mode == VG_SOURCE_BENCH_TEST;
}

static inline bool vg_nav_age_thresholds_valid(const vg_nav_age_thresholds_t *cfg)
{
    return cfg != NULL &&
           cfg->stale_after_ms > 0u &&
           cfg->offline_after_ms > cfg->stale_after_ms;
}

static inline unsigned char vg_nav_checksum_payload(const char *payload)
{
    unsigned char checksum = 0u;
    if (payload == NULL) {
        return 0u;
    }
    for (const unsigned char *p = (const unsigned char *)payload; *p != '\0'; ++p) {
        checksum ^= *p;
    }
    return checksum;
}

static inline int vg_nav_hex_value(char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return 10 + (c - 'A');
    if (c >= 'a' && c <= 'f') return 10 + (c - 'a');
    return -1;
}

static inline bool vg_nav_sentence_checksum_valid(const char *sentence)
{
    if (sentence == NULL || sentence[0] != '$') {
        return false;
    }
    const char *star = strchr(sentence, '*');
    if (star == NULL || star <= sentence + 1 || star[1] == '\0' || star[2] == '\0') {
        return false;
    }
    if (star[3] != '\0' && star[3] != '\r' && star[3] != '\n') {
        return false;
    }
    const int hi = vg_nav_hex_value(star[1]);
    const int lo = vg_nav_hex_value(star[2]);
    if (hi < 0 || lo < 0) {
        return false;
    }
    unsigned char calc = 0u;
    for (const unsigned char *p = (const unsigned char *)(sentence + 1);
         (const char *)p < star; ++p) {
        calc ^= *p;
    }
    const unsigned char expected = (unsigned char)((hi << 4) | lo);
    return calc == expected;
}

static inline bool vg_nav_format_coord(double degrees,
                                       bool latitude,
                                       char *number,
                                       size_t number_size,
                                       char *hemisphere)
{
    if (number == NULL || hemisphere == NULL || !isfinite(degrees)) {
        return false;
    }
    const double limit = latitude ? 90.0 : 180.0;
    if (degrees < -limit || degrees > limit) {
        return false;
    }
    const double abs_deg = fabs(degrees);
    const int whole_deg = (int)floor(abs_deg);
    const double minutes = (abs_deg - (double)whole_deg) * 60.0;
    int n;
    if (latitude) {
        n = snprintf(number, number_size, "%02d%07.4f", whole_deg, minutes);
        *hemisphere = degrees < 0.0 ? 'S' : 'N';
    } else {
        n = snprintf(number, number_size, "%03d%07.4f", whole_deg, minutes);
        *hemisphere = degrees < 0.0 ? 'W' : 'E';
    }
    return n > 0 && (size_t)n < number_size;
}

static inline bool vg_nav_format_rmc_development(const vg_nav_rmc_data_t *data,
                                                  char *out,
                                                  size_t out_size)
{
    if (data == NULL || out == NULL || out_size == 0u ||
        !isfinite(data->latitude_deg) || data->latitude_deg < -90.0 || data->latitude_deg > 90.0 ||
        !isfinite(data->longitude_deg) || data->longitude_deg < -180.0 || data->longitude_deg > 180.0 ||
        !isfinite(data->sog_knots) || data->sog_knots < 0.0f ||
        !isfinite(data->cog_deg) || data->cog_deg < 0.0f || data->cog_deg >= 360.0f) {
        return false;
    }

    char lat[16] = {0};
    char lon[16] = {0};
    char ns = 'N';
    char ew = 'E';
    if (!vg_nav_format_coord(data->latitude_deg, true, lat, sizeof(lat), &ns) ||
        !vg_nav_format_coord(data->longitude_deg, false, lon, sizeof(lon), &ew)) {
        return false;
    }

    char payload[VG_NAV_SENTENCE_MAX] = {0};
    const int pn = snprintf(payload, sizeof(payload),
                            "GPRMC,000000.00,%c,%s,%c,%s,%c,%.2f,%.2f,010100,,,A",
                            data->fix_valid ? 'A' : 'V',
                            lat, ns, lon, ew,
                            (double)data->sog_knots,
                            (double)data->cog_deg);
    if (pn <= 0 || (size_t)pn >= sizeof(payload)) {
        return false;
    }

    const unsigned char checksum = vg_nav_checksum_payload(payload);
    const int n = snprintf(out, out_size, "$%s*%02X", payload, (unsigned)checksum);
    return n > 0 && (size_t)n < out_size;
}

static inline bool vg_nav_copy_field(const char **cursor,
                                     const char *end,
                                     char *out,
                                     size_t out_size)
{
    if (cursor == NULL || *cursor == NULL || out == NULL || out_size == 0u) {
        return false;
    }
    const char *start = *cursor;
    const char *p = start;
    while (p < end && *p != ',') {
        ++p;
    }
    const size_t len = (size_t)(p - start);
    if (len + 1u > out_size) {
        return false;
    }
    memcpy(out, start, len);
    out[len] = '\0';
    *cursor = (p < end && *p == ',') ? p + 1 : p;
    return true;
}

static inline bool vg_nav_parse_double_strict(const char *text, double *out)
{
    if (text == NULL || text[0] == '\0' || out == NULL) {
        return false;
    }
    char *end = NULL;
    const double v = strtod(text, &end);
    if (end == text || *end != '\0' || !isfinite(v)) {
        return false;
    }
    *out = v;
    return true;
}

static inline bool vg_nav_parse_float_strict(const char *text, float *out)
{
    double v = 0.0;
    if (!vg_nav_parse_double_strict(text, &v) || v < -3.4028234e38 || v > 3.4028234e38) {
        return false;
    }
    *out = (float)v;
    return isfinite(*out);
}

static inline bool vg_nav_parse_coord(const char *number,
                                      char hemisphere,
                                      bool latitude,
                                      double *out)
{
    double raw = 0.0;
    if (!vg_nav_parse_double_strict(number, &raw) || raw < 0.0 || out == NULL) {
        return false;
    }
    const int degrees = (int)floor(raw / 100.0);
    const double minutes = raw - ((double)degrees * 100.0);
    const int max_deg = latitude ? 90 : 180;
    if (degrees < 0 || degrees > max_deg || minutes < 0.0 || minutes >= 60.0) {
        return false;
    }
    if (degrees == max_deg && minutes != 0.0) {
        return false;
    }
    if (latitude) {
        if (hemisphere != 'N' && hemisphere != 'S') return false;
    } else {
        if (hemisphere != 'E' && hemisphere != 'W') return false;
    }
    double value = (double)degrees + minutes / 60.0;
    if (hemisphere == 'S' || hemisphere == 'W') {
        value = -value;
    }
    *out = value;
    return true;
}

static inline bool vg_nav_parse_rmc_development(const char *sentence,
                                                 vg_nav_rmc_data_t *out)
{
    if (sentence == NULL || out == NULL || !vg_nav_sentence_checksum_valid(sentence)) {
        return false;
    }

    const char *star = strchr(sentence, '*');
    if (star == NULL) return false;
    const char *cursor = sentence + 1;

    char f[13][24];
    memset(f, 0, sizeof(f));
    for (size_t i = 0; i < 13u; ++i) {
        if (!vg_nav_copy_field(&cursor, star, f[i], sizeof(f[i]))) {
            return false;
        }
    }
    if (cursor != star) {
        return false;
    }
    if (strcmp(f[0], "GPRMC") != 0) {
        return false;
    }
    if (f[2][0] == '\0' || f[2][1] != '\0' || (f[2][0] != 'A' && f[2][0] != 'V')) {
        return false;
    }
    if (f[4][0] == '\0' || f[4][1] != '\0' || f[6][0] == '\0' || f[6][1] != '\0') {
        return false;
    }

    vg_nav_rmc_data_t parsed = {0};
    if (!vg_nav_parse_coord(f[3], f[4][0], true, &parsed.latitude_deg) ||
        !vg_nav_parse_coord(f[5], f[6][0], false, &parsed.longitude_deg) ||
        !vg_nav_parse_float_strict(f[7], &parsed.sog_knots) ||
        !vg_nav_parse_float_strict(f[8], &parsed.cog_deg)) {
        return false;
    }
    if (parsed.sog_knots < 0.0f || parsed.cog_deg < 0.0f || parsed.cog_deg >= 360.0f) {
        return false;
    }
    parsed.fix_valid = f[2][0] == 'A';
    *out = parsed;
    return true;
}

static inline bool vg_nav_ingest_sentence(vg_navigation_state_t *state,
                                          const char *sentence,
                                          uint64_t now_ms,
                                          vg_source_mode_t source_mode)
{
    if (state == NULL || sentence == NULL || !vg_nav_source_mode_supported(source_mode)) {
        return false;
    }
    vg_nav_rmc_data_t parsed = {0};
    if (!vg_nav_parse_rmc_development(sentence, &parsed)) {
        return false;
    }

    vg_navigation_state_t next = *state;
    next.initialized = true;
    next.source_mode = source_mode;
    next.latitude_deg = parsed.latitude_deg;
    next.longitude_deg = parsed.longitude_deg;
    next.sog_knots = parsed.sog_knots;
    next.cog_deg = parsed.cog_deg;
    next.fix_valid = parsed.fix_valid;
    next.last_valid_ms = now_ms;
    next.data_age_ms = 0u;
    next.age_state = VG_NAV_AGE_VALID;
    next.quality = VG_QUALITY_VALID;
    *state = next;
    return true;
}

static inline bool vg_nav_update_age(vg_navigation_state_t *state,
                                     uint64_t now_ms,
                                     const vg_nav_age_thresholds_t *cfg)
{
    if (state == NULL || !state->initialized ||
        !vg_nav_source_mode_supported(state->source_mode) ||
        !vg_nav_age_thresholds_valid(cfg) ||
        now_ms < state->last_valid_ms) {
        return false;
    }

    const uint64_t age = now_ms - state->last_valid_ms;
    state->data_age_ms = age;
    if (age < cfg->stale_after_ms) {
        state->age_state = VG_NAV_AGE_VALID;
        state->quality = VG_QUALITY_VALID;
    } else if (age < cfg->offline_after_ms) {
        state->age_state = VG_NAV_AGE_STALE;
        state->quality = VG_QUALITY_STALE;
    } else {
        state->age_state = VG_NAV_AGE_OFFLINE;
        state->quality = VG_QUALITY_MISSING;
    }
    return true;
}

#endif /* VG_NAVIGATION_NMEA_H */
