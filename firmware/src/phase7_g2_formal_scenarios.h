#ifndef VG_PHASE7_G2_FORMAL_SCENARIOS_H
#define VG_PHASE7_G2_FORMAL_SCENARIOS_H

#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#include "navigation_nmea.h"

/*
 * Phase 7 G2 dedicated formal software-simulation scenarios.
 *
 * Scope:
 *   SIM-008 - malformed/checksum-invalid NMEA-style input is rejected and the
 *             last valid navigation state is not refreshed.
 *   SIM-009 - stopped navigation input causes VALID -> STALE -> OFFLINE using
 *             configurable development thresholds.
 *
 * This is software-simulation evidence only. It does not claim full NMEA 0183
 * conformance, installed Furuno GP-39 hardware, physical GNSS/NMEA bench
 * verification, vessel-approved thresholds, certification or production
 * readiness.
 */

static inline void vg_g2_check(const char *scenario,
                               const char *name,
                               bool ok,
                               unsigned *passed,
                               unsigned *total)
{
    (*total)++;
    if (ok) {
        (*passed)++;
    }
    printf("G2_%s_CHECK %s: %s\n", scenario, name, ok ? "PASS" : "FAIL");
}

static inline bool vg_g2_state_payload_equal(const vg_navigation_state_t *a,
                                             const vg_navigation_state_t *b)
{
    if (a == NULL || b == NULL) {
        return false;
    }
    return a->initialized == b->initialized &&
           a->source_mode == b->source_mode &&
           a->latitude_deg == b->latitude_deg &&
           a->longitude_deg == b->longitude_deg &&
           a->sog_knots == b->sog_knots &&
           a->cog_deg == b->cog_deg &&
           a->fix_valid == b->fix_valid &&
           a->last_valid_ms == b->last_valid_ms;
}

static inline bool vg_g2_run_sim008(void)
{
    unsigned p = 0u;
    unsigned t = 0u;

    const vg_nav_age_thresholds_t cfg = {
        .stale_after_ms = 2000u,
        .offline_after_ms = 5000u
    };
    const vg_nav_rmc_data_t input = {
        .latitude_deg = -6.1754,
        .longitude_deg = 106.8272,
        .sog_knots = 12.5f,
        .cog_deg = 123.4f,
        .fix_valid = true
    };

    char sentence[VG_NAV_SENTENCE_MAX] = {0};
    bool ok = vg_nav_format_rmc_development(&input, sentence, sizeof(sentence));
    vg_g2_check("SIM008", "VALID_SENTENCE_GENERATED", ok, &p, &t);

    vg_navigation_state_t state = {0};
    ok = ok && vg_nav_ingest_sentence(&state, sentence, 1000u, VG_SOURCE_SIMULATION);
    vg_g2_check("SIM008", "INITIAL_VALID_STATE", ok &&
                state.initialized &&
                state.age_state == VG_NAV_AGE_VALID &&
                state.quality == VG_QUALITY_VALID &&
                state.last_valid_ms == 1000u, &p, &t);

    const vg_navigation_state_t snapshot = state;

    char corrupted[VG_NAV_SENTENCE_MAX] = {0};
    strcpy(corrupted, sentence);
    if (strlen(corrupted) > 10u) {
        corrupted[10] = corrupted[10] == '0' ? '1' : '0';
    }

    vg_g2_check("SIM008", "INVALID_CHECKSUM_INJECTED",
                !vg_nav_sentence_checksum_valid(corrupted), &p, &t);

    const bool rejected =
        !vg_nav_ingest_sentence(&state, corrupted, 1500u, VG_SOURCE_SIMULATION);
    vg_g2_check("SIM008", "INVALID_INPUT_REJECTED", rejected, &p, &t);

    vg_g2_check("SIM008", "LAST_VALID_NOT_REFRESHED",
                rejected && state.last_valid_ms == snapshot.last_valid_ms,
                &p, &t);

    vg_g2_check("SIM008", "LAST_VALID_PAYLOAD_PRESERVED",
                rejected && vg_g2_state_payload_equal(&state, &snapshot),
                &p, &t);

    const bool aged = vg_nav_update_age(&state, 3000u, &cfg);
    vg_g2_check("SIM008", "AGE_CONTINUES_FROM_LAST_VALID",
                aged &&
                state.last_valid_ms == 1000u &&
                state.data_age_ms == 2000u &&
                state.age_state == VG_NAV_AGE_STALE &&
                state.quality == VG_QUALITY_STALE,
                &p, &t);

    const bool pass = p == t && t == 7u;
    printf("G2_FORMAL_SCENARIO SIM-008: %s\n", pass ? "PASS" : "FAIL");
    return pass;
}

static inline bool vg_g2_run_sim009(void)
{
    unsigned p = 0u;
    unsigned t = 0u;

    const vg_nav_age_thresholds_t cfg = {
        .stale_after_ms = 2000u,
        .offline_after_ms = 5000u
    };
    const vg_nav_rmc_data_t input = {
        .latitude_deg = -6.1754,
        .longitude_deg = 106.8272,
        .sog_knots = 12.5f,
        .cog_deg = 123.4f,
        .fix_valid = true
    };

    vg_g2_check("SIM009", "CONFIGURABLE_THRESHOLDS",
                vg_nav_age_thresholds_valid(&cfg) &&
                cfg.stale_after_ms == 2000u &&
                cfg.offline_after_ms == 5000u,
                &p, &t);

    char sentence[VG_NAV_SENTENCE_MAX] = {0};
    bool ok = vg_nav_format_rmc_development(&input, sentence, sizeof(sentence));

    vg_navigation_state_t state = {0};
    ok = ok && vg_nav_ingest_sentence(&state, sentence, 1000u, VG_SOURCE_SIMULATION);
    vg_g2_check("SIM009", "STREAM_VALID_BEFORE_LOSS",
                ok &&
                state.last_valid_ms == 1000u &&
                state.age_state == VG_NAV_AGE_VALID &&
                state.quality == VG_QUALITY_VALID,
                &p, &t);

    /* No additional sentence is ingested below: this models stream loss. */
    bool step = vg_nav_update_age(&state, 2999u, &cfg);
    vg_g2_check("SIM009", "VALID_BEFORE_STALE_THRESHOLD",
                step &&
                state.last_valid_ms == 1000u &&
                state.data_age_ms == 1999u &&
                state.age_state == VG_NAV_AGE_VALID &&
                state.quality == VG_QUALITY_VALID,
                &p, &t);

    step = vg_nav_update_age(&state, 3000u, &cfg);
    vg_g2_check("SIM009", "STALE_AT_THRESHOLD",
                step &&
                state.last_valid_ms == 1000u &&
                state.data_age_ms == 2000u &&
                state.age_state == VG_NAV_AGE_STALE &&
                state.quality == VG_QUALITY_STALE,
                &p, &t);

    step = vg_nav_update_age(&state, 5999u, &cfg);
    vg_g2_check("SIM009", "STALE_BEFORE_OFFLINE_THRESHOLD",
                step &&
                state.last_valid_ms == 1000u &&
                state.data_age_ms == 4999u &&
                state.age_state == VG_NAV_AGE_STALE &&
                state.quality == VG_QUALITY_STALE,
                &p, &t);

    step = vg_nav_update_age(&state, 6000u, &cfg);
    vg_g2_check("SIM009", "OFFLINE_AT_THRESHOLD",
                step &&
                state.last_valid_ms == 1000u &&
                state.data_age_ms == 5000u &&
                state.age_state == VG_NAV_AGE_OFFLINE &&
                state.quality == VG_QUALITY_MISSING,
                &p, &t);

    vg_g2_check("SIM009", "NO_REFRESH_DURING_STREAM_LOSS",
                state.last_valid_ms == 1000u, &p, &t);

    const bool pass = p == t && t == 7u;
    printf("G2_FORMAL_SCENARIO SIM-009: %s\n", pass ? "PASS" : "FAIL");
    return pass;
}

static inline void run_phase7_g2_formal_scenarios(void)
{
    unsigned passed = 0u;
    const unsigned total = 2u;

    if (vg_g2_run_sim008()) {
        passed++;
    }
    if (vg_g2_run_sim009()) {
        passed++;
    }

    printf("PHASE7_G2_FORMAL_SCENARIOS: %s (%u/%u)\n",
           passed == total ? "PASS" : "FAIL",
           passed,
           total);
}

#endif /* VG_PHASE7_G2_FORMAL_SCENARIOS_H */
