
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#include "core_types.h"
#include "core_quality.h"
#include "core_source_mode.h"

/*
 * Integrated Vessel Monitoring & Diagnostic Gateway
 *
 * Development-only firmware self-tests.
 *
 * No sensors, physical controls, or vessel
 * integration are involved.
 */

_Static_assert(
    VG_QUALITY_UNKNOWN == 0,
    "Default data quality must be UNKNOWN"
);

_Static_assert(
    VG_SOURCE_SIMULATION != VG_SOURCE_BENCH_TEST &&
    VG_SOURCE_SIMULATION != VG_SOURCE_PHYSICAL &&
    VG_SOURCE_BENCH_TEST != VG_SOURCE_PHYSICAL,
    "Source modes must have distinct values"
);

/* Core Quality Self-Test */

typedef struct {
    const char *name;
    vg_data_quality_t quality;
    bool has_value;
    bool expected;
} vg_quality_test_case_t;

static void run_core_quality_selftest(void)
{
    const vg_quality_test_case_t cases[] = {
        {"VALID_WITH_VALUE", VG_QUALITY_VALID, true, true},
        {"VALID_NO_VALUE", VG_QUALITY_VALID, false, false},
        {"INVALID_WITH_VALUE", VG_QUALITY_INVALID, true, false},
        {"MISSING_NO_VALUE", VG_QUALITY_MISSING, false, false},
        {"STALE_WITH_VALUE", VG_QUALITY_STALE, true, false},
        {"UNKNOWN_NO_VALUE", VG_QUALITY_UNKNOWN, false, false},
        {"UNKNOWN_WITH_VALUE", VG_QUALITY_UNKNOWN, true, false}
    };

    const size_t count = sizeof(cases) / sizeof(cases[0]);
    size_t passed = 0;

    for (size_t i = 0; i < count; ++i) {
        const bool actual = vg_measurement_is_current_valid(
            cases[i].quality,
            cases[i].has_value
        );

        const bool success = (actual == cases[i].expected);

        printf("QUALITY_TEST %s: %s\n",
               cases[i].name,
               success ? "PASS" : "FAIL");

        if (success) {
            ++passed;
        }
    }

    printf("CORE_QUALITY_SELFTEST: %s (%u/%u)\n",
           passed == count ? "PASS" : "FAIL",
           (unsigned)passed,
           (unsigned)count);
}

/* Source Mode Self-Test */

typedef struct {
    const char *name;
    vg_source_mode_t mode;
    const char *expected_label;
    bool expected_known;
} vg_source_mode_test_case_t;

static void run_source_mode_selftest(void)
{
    const vg_source_mode_test_case_t cases[] = {
        {
            "SIMULATION",
            VG_SOURCE_SIMULATION,
            "simulation",
            true
        },
        {
            "BENCH_TEST",
            VG_SOURCE_BENCH_TEST,
            "bench_test",
            true
        },
        {
            "PHYSICAL_LABEL",
            VG_SOURCE_PHYSICAL,
            "physical",
            true
        },
        {
            "UNKNOWN_99",
            (vg_source_mode_t)99,
            NULL,
            false
        }
    };

    const size_t count = sizeof(cases) / sizeof(cases[0]);
    size_t passed = 0;

    for (size_t i = 0; i < count; ++i) {
        const char *actual_label =
            vg_source_mode_to_string(cases[i].mode);

        const bool actual_known =
            vg_source_mode_is_known(cases[i].mode);

        const bool label_matches =
            (actual_label == NULL &&
             cases[i].expected_label == NULL) ||
            (actual_label != NULL &&
             cases[i].expected_label != NULL &&
             strcmp(actual_label, cases[i].expected_label) == 0);

        const bool success =
            label_matches &&
            actual_known == cases[i].expected_known;

        printf("SOURCE_MODE_TEST %s: %s\n",
               cases[i].name,
               success ? "PASS" : "FAIL");

        if (success) {
            ++passed;
        }
    }

    printf("SOURCE_MODE_SELFTEST: %s (%u/%u)\n",
           passed == count ? "PASS" : "FAIL",
           (unsigned)passed,
           (unsigned)count);
}

void app_main(void)
{
    puts("Development scaffold only; "
         "monitoring and alarms are not implemented.");

    run_core_quality_selftest();
    run_source_mode_selftest();
}
