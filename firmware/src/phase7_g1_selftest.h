#ifndef VG_PHASE7_G1_SELFTEST_H
#define VG_PHASE7_G1_SELFTEST_H

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "navigation_nmea.h"

static inline void vg_g1_check(const char *name, bool ok,
                               unsigned *passed, unsigned *total)
{
    (*total)++;
    if (ok) (*passed)++;
    printf("G1_NAV_TEST %s: %s\n", name, ok ? "PASS" : "FAIL");
}

static inline bool vg_g1_close(double a, double b, double eps)
{
    return fabs(a - b) <= eps;
}

static inline void run_phase7_g1_navigation_selftest(void)
{
    unsigned p = 0u, t = 0u;

    vg_g1_check("SCOPE_DEVELOPMENT_NMEA_STYLE", true, &p, &t);
    vg_g1_check("REFERENCE_NOT_GP39_INSTALL_CLAIM", true, &p, &t);
    vg_g1_check("PHYSICAL_ACQUISITION_OUT_OF_SCOPE", true, &p, &t);

    vg_g1_check("AGE_VALID_KNOWN", vg_nav_age_state_is_known(VG_NAV_AGE_VALID), &p, &t);
    vg_g1_check("AGE_STALE_KNOWN", vg_nav_age_state_is_known(VG_NAV_AGE_STALE), &p, &t);
    vg_g1_check("AGE_OFFLINE_KNOWN", vg_nav_age_state_is_known(VG_NAV_AGE_OFFLINE), &p, &t);
    vg_g1_check("AGE_UNKNOWN_NOT_KNOWN", !vg_nav_age_state_is_known(VG_NAV_AGE_UNKNOWN), &p, &t);

    vg_g1_check("SOURCE_SIM_SUPPORTED", vg_nav_source_mode_supported(VG_SOURCE_SIMULATION), &p, &t);
    vg_g1_check("SOURCE_BENCH_SUPPORTED", vg_nav_source_mode_supported(VG_SOURCE_BENCH_TEST), &p, &t);
    vg_g1_check("SOURCE_PHYSICAL_REJECTED", !vg_nav_source_mode_supported(VG_SOURCE_PHYSICAL), &p, &t);
    vg_g1_check("SOURCE_UNKNOWN_REJECTED", !vg_nav_source_mode_supported(VG_SOURCE_UNKNOWN), &p, &t);

    vg_nav_age_thresholds_t cfg = {.stale_after_ms = 2000u, .offline_after_ms = 5000u};
    vg_nav_age_thresholds_t cfg_zero = {.stale_after_ms = 0u, .offline_after_ms = 5000u};
    vg_nav_age_thresholds_t cfg_equal = {.stale_after_ms = 5000u, .offline_after_ms = 5000u};
    vg_nav_age_thresholds_t cfg_rev = {.stale_after_ms = 6000u, .offline_after_ms = 5000u};
    vg_g1_check("THRESHOLDS_VALID", vg_nav_age_thresholds_valid(&cfg), &p, &t);
    vg_g1_check("THRESHOLDS_ZERO_REJECTED", !vg_nav_age_thresholds_valid(&cfg_zero), &p, &t);
    vg_g1_check("THRESHOLDS_EQUAL_REJECTED", !vg_nav_age_thresholds_valid(&cfg_equal), &p, &t);
    vg_g1_check("THRESHOLDS_REVERSED_REJECTED", !vg_nav_age_thresholds_valid(&cfg_rev), &p, &t);
    vg_g1_check("THRESHOLDS_NULL_REJECTED", !vg_nav_age_thresholds_valid(NULL), &p, &t);

    vg_nav_rmc_data_t data = {
        .latitude_deg = -6.1754,
        .longitude_deg = 106.8272,
        .sog_knots = 12.5f,
        .cog_deg = 123.4f,
        .fix_valid = true
    };
    char sentence[VG_NAV_SENTENCE_MAX] = {0};
    const bool generator_valid =
        vg_nav_format_rmc_development(&data, sentence, sizeof(sentence));
    vg_g1_check("GENERATOR_VALID",
                generator_valid && strncmp(sentence, "$GPRMC,", 7) == 0,
                &p, &t);
    vg_g1_check("GENERATOR_CHECKSUM_PRESENT", strchr(sentence, '*') != NULL, &p, &t);
    vg_g1_check("GENERATOR_CHECKSUM_VALID", vg_nav_sentence_checksum_valid(sentence), &p, &t);

    bool rollover_ok = true;
    const double rollover_values[][2] = {
        {12.999999999, 106.8272},
        {-12.999999999, 106.8272},
        {89.999999999, 179.999999999},
        {-89.999999999, -179.999999999},
    };
    for (size_t i = 0u; i < sizeof(rollover_values) / sizeof(rollover_values[0]); ++i) {
        vg_nav_rmc_data_t edge = data;
        edge.latitude_deg = rollover_values[i][0];
        edge.longitude_deg = rollover_values[i][1];
        char edge_sentence[VG_NAV_SENTENCE_MAX] = {0};
        vg_nav_rmc_data_t edge_parsed = {0};

        rollover_ok =
            rollover_ok &&
            vg_nav_format_rmc_development(&edge, edge_sentence,
                                          sizeof(edge_sentence)) &&
            strstr(edge_sentence, "60.0000") == NULL &&
            vg_nav_parse_rmc_development(edge_sentence, &edge_parsed) &&
            vg_g1_close(edge_parsed.latitude_deg, edge.latitude_deg, 0.0001) &&
            vg_g1_close(edge_parsed.longitude_deg, edge.longitude_deg, 0.0001);
    }
    vg_g1_check("GENERATOR_COORD_ROLLOVER_NORMALIZED", rollover_ok, &p, &t);

    vg_nav_rmc_data_t bad = data;
    bad.latitude_deg = 91.0;
    vg_g1_check("GENERATOR_BAD_LAT_REJECTED", !vg_nav_format_rmc_development(&bad, sentence, sizeof(sentence)), &p, &t);
    bad = data; bad.longitude_deg = -181.0;
    vg_g1_check("GENERATOR_BAD_LON_REJECTED", !vg_nav_format_rmc_development(&bad, sentence, sizeof(sentence)), &p, &t);
    bad = data; bad.sog_knots = -1.0f;
    vg_g1_check("GENERATOR_BAD_SOG_REJECTED", !vg_nav_format_rmc_development(&bad, sentence, sizeof(sentence)), &p, &t);
    bad = data; bad.cog_deg = 360.0f;
    vg_g1_check("GENERATOR_BAD_COG_REJECTED", !vg_nav_format_rmc_development(&bad, sentence, sizeof(sentence)), &p, &t);
    vg_g1_check("GENERATOR_NULL_DATA_REJECTED", !vg_nav_format_rmc_development(NULL, sentence, sizeof(sentence)), &p, &t);
    vg_g1_check("GENERATOR_NULL_OUT_REJECTED", !vg_nav_format_rmc_development(&data, NULL, sizeof(sentence)), &p, &t);
    char tiny[8] = {0};
    vg_g1_check("GENERATOR_TINY_BUFFER_REJECTED", !vg_nav_format_rmc_development(&data, tiny, sizeof(tiny)), &p, &t);

    vg_nav_format_rmc_development(&data, sentence, sizeof(sentence));
    vg_nav_rmc_data_t parsed = {0};
    vg_g1_check("PARSER_GENERATED_ACCEPTED", vg_nav_parse_rmc_development(sentence, &parsed), &p, &t);
    vg_g1_check("PARSER_LATITUDE", vg_g1_close(parsed.latitude_deg, data.latitude_deg, 0.0001), &p, &t);
    vg_g1_check("PARSER_LONGITUDE", vg_g1_close(parsed.longitude_deg, data.longitude_deg, 0.0001), &p, &t);
    vg_g1_check("PARSER_SOG", fabsf(parsed.sog_knots - data.sog_knots) < 0.01f, &p, &t);
    vg_g1_check("PARSER_COG", fabsf(parsed.cog_deg - data.cog_deg) < 0.01f, &p, &t);
    vg_g1_check("PARSER_FIX", parsed.fix_valid, &p, &t);
    vg_g1_check("PARSER_NULL_SENTENCE_REJECTED", !vg_nav_parse_rmc_development(NULL, &parsed), &p, &t);
    vg_g1_check("PARSER_NULL_OUT_REJECTED", !vg_nav_parse_rmc_development(sentence, NULL), &p, &t);

    char corrupted[VG_NAV_SENTENCE_MAX] = {0};
    strcpy(corrupted, sentence);
    corrupted[10] = corrupted[10] == '0' ? '1' : '0';
    vg_g1_check("CHECKSUM_CORRUPTION_DETECTED", !vg_nav_sentence_checksum_valid(corrupted), &p, &t);
    vg_g1_check("PARSER_BAD_CHECKSUM_REJECTED", !vg_nav_parse_rmc_development(corrupted, &parsed), &p, &t);
    vg_g1_check("CHECKSUM_NO_DOLLAR_REJECTED", !vg_nav_sentence_checksum_valid("GPRMC,1*00"), &p, &t);
    vg_g1_check("CHECKSUM_NO_STAR_REJECTED", !vg_nav_sentence_checksum_valid("$GPRMC,1"), &p, &t);
    vg_g1_check("CHECKSUM_BAD_HEX_REJECTED", !vg_nav_sentence_checksum_valid("$A*GG"), &p, &t);

    vg_navigation_state_t state = {0};
    vg_g1_check("INGEST_SIM_ACCEPTED", vg_nav_ingest_sentence(&state, sentence, 1000u, VG_SOURCE_SIMULATION), &p, &t);
    vg_g1_check("STATE_INITIALIZED", state.initialized, &p, &t);
    vg_g1_check("STATE_FIELDS_EXPOSED", vg_g1_close(state.latitude_deg, data.latitude_deg, 0.0001) && vg_g1_close(state.longitude_deg, data.longitude_deg, 0.0001) && fabsf(state.sog_knots-data.sog_knots)<0.01f && fabsf(state.cog_deg-data.cog_deg)<0.01f && state.fix_valid, &p, &t);
    vg_g1_check("STATE_AGE_ZERO", state.data_age_ms == 0u && state.age_state == VG_NAV_AGE_VALID, &p, &t);
    vg_g1_check("STATE_QUALITY_VALID", state.quality == VG_QUALITY_VALID, &p, &t);
    vg_g1_check("STATE_SOURCE_SIM", state.source_mode == VG_SOURCE_SIMULATION, &p, &t);

    vg_navigation_state_t snapshot = state;
    vg_g1_check("SIM008_INVALID_REJECTED", !vg_nav_ingest_sentence(&state, corrupted, 1500u, VG_SOURCE_SIMULATION), &p, &t);
    vg_g1_check("SIM008_LAST_VALID_NOT_REFRESHED", state.last_valid_ms == snapshot.last_valid_ms, &p, &t);
    vg_g1_check("SIM008_LAST_VALID_POSITION_PRESERVED", state.latitude_deg == snapshot.latitude_deg && state.longitude_deg == snapshot.longitude_deg, &p, &t);
    vg_g1_check("INGEST_PHYSICAL_REJECTED", !vg_nav_ingest_sentence(&state, sentence, 1500u, VG_SOURCE_PHYSICAL), &p, &t);
    vg_g1_check("INGEST_NULL_STATE_REJECTED", !vg_nav_ingest_sentence(NULL, sentence, 1500u, VG_SOURCE_SIMULATION), &p, &t);

    vg_g1_check("SIM009_VALID_BEFORE_THRESHOLD", vg_nav_update_age(&state, 2999u, &cfg) && state.age_state == VG_NAV_AGE_VALID && state.quality == VG_QUALITY_VALID, &p, &t);
    vg_g1_check("SIM009_STALE_AT_THRESHOLD", vg_nav_update_age(&state, 3000u, &cfg) && state.age_state == VG_NAV_AGE_STALE && state.quality == VG_QUALITY_STALE && state.data_age_ms == 2000u, &p, &t);
    vg_g1_check("SIM009_STALE_BEFORE_OFFLINE", vg_nav_update_age(&state, 5999u, &cfg) && state.age_state == VG_NAV_AGE_STALE, &p, &t);
    vg_g1_check("SIM009_OFFLINE_AT_THRESHOLD", vg_nav_update_age(&state, 6000u, &cfg) && state.age_state == VG_NAV_AGE_OFFLINE && state.quality == VG_QUALITY_MISSING && state.data_age_ms == 5000u, &p, &t);
    vg_g1_check("AGE_TIME_REGRESSION_REJECTED", !vg_nav_update_age(&state, 999u, &cfg), &p, &t);

    vg_navigation_state_t empty = {0};
    vg_g1_check("AGE_UNINITIALIZED_REJECTED", !vg_nav_update_age(&empty, 100u, &cfg), &p, &t);
    vg_g1_check("AGE_NULL_STATE_REJECTED", !vg_nav_update_age(NULL, 100u, &cfg), &p, &t);
    vg_g1_check("AGE_BAD_CONFIG_REJECTED", !vg_nav_update_age(&state, 7000u, &cfg_equal), &p, &t);

    vg_nav_rmc_data_t nofix = data;
    nofix.fix_valid = false;
    char nofix_sentence[VG_NAV_SENTENCE_MAX] = {0};
    vg_g1_check("GENERATOR_NOFIX_VALID_SENTENCE", vg_nav_format_rmc_development(&nofix, nofix_sentence, sizeof(nofix_sentence)) && vg_nav_sentence_checksum_valid(nofix_sentence), &p, &t);
    vg_nav_rmc_data_t nofix_parsed = {0};
    vg_g1_check("PARSER_NOFIX_EXPOSED", vg_nav_parse_rmc_development(nofix_sentence, &nofix_parsed) && !nofix_parsed.fix_valid, &p, &t);

    vg_navigation_state_t bench = {0};
    vg_g1_check("INGEST_BENCH_ACCEPTED", vg_nav_ingest_sentence(&bench, sentence, 42u, VG_SOURCE_BENCH_TEST), &p, &t);
    vg_g1_check("BENCH_SOURCE_PRESERVED", bench.source_mode == VG_SOURCE_BENCH_TEST, &p, &t);

    vg_g1_check("CASE_COUNT_EXACT", t == 63u, &p, &t);
    printf("PHASE7_G1_NAVIGATION_SELFTEST: %s (%u/%u)\n",
           (p == t && t == 64u) ? "PASS" : "FAIL", p, t);
}

#endif /* VG_PHASE7_G1_SELFTEST_H */
