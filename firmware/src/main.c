#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

#include "core_types.h"
#include "core_quality.h"
#include "core_source_mode.h"
#include "core_measurement.h"
#include "core_range.h"
#include "core_alarm.h"

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
    VG_SOURCE_UNKNOWN == 0,
    "Default source mode must be UNKNOWN"
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
            "UNKNOWN_ZERO",
            VG_SOURCE_UNKNOWN,
            NULL,
            false
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

/* Core Measurement Self-Test */

typedef struct {
    const char *name;
    vg_measurement_t measurement;
    bool provide_measurement;
    bool provide_output;
    bool expected_success;
    float expected_value;
} vg_measurement_test_case_t;

static void run_core_measurement_selftest(void)
{
    const vg_measurement_test_case_t cases[] = {
        {
            "SIMULATION_VALID",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 42.5f},
            true, true, true, 42.5f
        },
        {
            "BENCH_TEST_VALID",
            {VG_SOURCE_BENCH_TEST, VG_QUALITY_VALID, true, 21.25f},
            true, true, true, 21.25f
        },
        {
            "VALID_ZERO",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 0.0f},
            true, true, true, 0.0f
        },
        {
            "NAN_REJECTED",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, NAN},
            true, true, false, 0.0f
        },
        {
            "POSITIVE_INFINITY_REJECTED",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, INFINITY},
            true, true, false, 0.0f
        },
        {
            "NEGATIVE_INFINITY_REJECTED",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, -INFINITY},
            true, true, false, 0.0f
        },
        {
            "ZERO_INITIALIZED",
            {0},
            true, true, false, 0.0f
        },
        {
            "UNKNOWN_SOURCE_VALID",
            {VG_SOURCE_UNKNOWN, VG_QUALITY_VALID, true, 5.0f},
            true, true, false, 0.0f
        },
        {
            "UNKNOWN_99_VALID",
            {(vg_source_mode_t)99, VG_QUALITY_VALID, true, 5.0f},
            true, true, false, 0.0f
        },
        {
            "INVALID_WITH_VALUE",
            {VG_SOURCE_SIMULATION, VG_QUALITY_INVALID, true, 5.0f},
            true, true, false, 0.0f
        },
        {
            "MISSING_NO_VALUE",
            {VG_SOURCE_SIMULATION, VG_QUALITY_MISSING, false, 0.0f},
            true, true, false, 0.0f
        },
        {
            "STALE_WITH_VALUE",
            {VG_SOURCE_SIMULATION, VG_QUALITY_STALE, true, 5.0f},
            true, true, false, 0.0f
        },
        {
            "UNKNOWN_QUALITY",
            {VG_SOURCE_SIMULATION, VG_QUALITY_UNKNOWN, true, 5.0f},
            true, true, false, 0.0f
        },
        {
            "VALID_NO_VALUE",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, false, 0.0f},
            true, true, false, 0.0f
        },
        {
            "NULL_MEASUREMENT",
            {0},
            false, true, false, 0.0f
        },
        {
            "NULL_OUTPUT",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 5.0f},
            true, false, false, 0.0f
        }
    };

    const size_t count = sizeof(cases) / sizeof(cases[0]);
    size_t passed = 0;

    const float sentinel = -98765.0f;

    for (size_t i = 0; i < count; ++i) {
        float output = sentinel;

        const vg_measurement_t *measurement_ptr =
            cases[i].provide_measurement
                ? &cases[i].measurement
                : NULL;

        float *output_ptr =
            cases[i].provide_output
                ? &output
                : NULL;

        const bool actual_success =
            vg_measurement_try_get_current_value(
                measurement_ptr,
                output_ptr
            );

        const bool result_matches =
            (actual_success == cases[i].expected_success);

        const bool value_matches =
            actual_success
                ? (output == cases[i].expected_value)
                : (output == sentinel);

        const bool success =
            result_matches && value_matches;

        printf("MEASUREMENT_TEST %s: %s\n",
               cases[i].name,
               success ? "PASS" : "FAIL");

        if (success) {
            ++passed;
        }
    }

    printf("CORE_MEASUREMENT_SELFTEST: %s (%u/%u)\n",
           passed == count ? "PASS" : "FAIL",
           (unsigned)passed,
           (unsigned)count);
}

/* Core Range Self-Test */

typedef struct {
    const char *name;
    vg_measurement_t measurement;
    vg_measurement_range_t range;
    bool provide_measurement;
    bool provide_range;
    bool provide_output;
    bool expected_success;
    float expected_value;
} vg_range_test_case_t;

static void run_core_range_selftest(void)
{
    const vg_range_test_case_t cases[] = {
        {
            "IN_RANGE",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 50.0f},
            {true, 0.0f, 100.0f},
            true, true, true, true, 50.0f
        },
        {
            "MIN_BOUNDARY",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 0.0f},
            {true, 0.0f, 100.0f},
            true, true, true, true, 0.0f
        },
        {
            "MAX_BOUNDARY",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 100.0f},
            {true, 0.0f, 100.0f},
            true, true, true, true, 100.0f
        },
        {
            "NEGATIVE_ALLOWED",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, -12.5f},
            {true, -20.0f, 20.0f},
            true, true, true, true, -12.5f
        },
        {
            "BENCH_TEST_IN_RANGE",
            {VG_SOURCE_BENCH_TEST, VG_QUALITY_VALID, true, 40.0f},
            {true, 0.0f, 100.0f},
            true, true, true, true, 40.0f
        },
        {
            "BELOW_MINIMUM",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, -1.0f},
            {true, 0.0f, 100.0f},
            true, true, true, false, 0.0f
        },
        {
            "ABOVE_MAXIMUM",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 101.0f},
            {true, 0.0f, 100.0f},
            true, true, true, false, 0.0f
        },
        {
            "UNCONFIGURED_RANGE",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 50.0f},
            {false, 0.0f, 100.0f},
            true, true, true, false, 0.0f
        },
        {
            "ZERO_INITIALIZED_RANGE",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 50.0f},
            {0},
            true, true, true, false, 0.0f
        },
        {
            "REVERSED_RANGE",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 50.0f},
            {true, 100.0f, 0.0f},
            true, true, true, false, 0.0f
        },
        {
            "NAN_MINIMUM",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 50.0f},
            {true, NAN, 100.0f},
            true, true, true, false, 0.0f
        },
        {
            "NAN_MAXIMUM",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 50.0f},
            {true, 0.0f, NAN},
            true, true, true, false, 0.0f
        },
        {
            "POSITIVE_INFINITY_MINIMUM",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 50.0f},
            {true, INFINITY, 100.0f},
            true, true, true, false, 0.0f
        },
        {
            "NEGATIVE_INFINITY_MAXIMUM",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 50.0f},
            {true, 0.0f, -INFINITY},
            true, true, true, false, 0.0f
        },
        {
            "UNKNOWN_SOURCE",
            {VG_SOURCE_UNKNOWN, VG_QUALITY_VALID, true, 50.0f},
            {true, 0.0f, 100.0f},
            true, true, true, false, 0.0f
        },
        {
            "INVALID_QUALITY",
            {VG_SOURCE_SIMULATION, VG_QUALITY_INVALID, true, 50.0f},
            {true, 0.0f, 100.0f},
            true, true, true, false, 0.0f
        },
        {
            "MISSING_VALUE",
            {VG_SOURCE_SIMULATION, VG_QUALITY_MISSING, false, 0.0f},
            {true, 0.0f, 100.0f},
            true, true, true, false, 0.0f
        },
        {
            "NAN_MEASUREMENT",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, NAN},
            {true, 0.0f, 100.0f},
            true, true, true, false, 0.0f
        },
        {
            "NULL_MEASUREMENT",
            {0},
            {true, 0.0f, 100.0f},
            false, true, true, false, 0.0f
        },
        {
            "NULL_RANGE",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 50.0f},
            {0},
            true, false, true, false, 0.0f
        },
        {
            "NULL_OUTPUT",
            {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 50.0f},
            {true, 0.0f, 100.0f},
            true, true, false, false, 0.0f
        }
    };

    const size_t count = sizeof(cases) / sizeof(cases[0]);
    size_t passed = 0;
    const float sentinel = -98765.0f;

    for (size_t i = 0; i < count; ++i) {
        float output = sentinel;

        const vg_measurement_t *measurement_ptr =
            cases[i].provide_measurement
                ? &cases[i].measurement
                : NULL;

        const vg_measurement_range_t *range_ptr =
            cases[i].provide_range
                ? &cases[i].range
                : NULL;

        float *output_ptr =
            cases[i].provide_output
                ? &output
                : NULL;

        const bool actual_success =
            vg_measurement_try_get_in_range(
                measurement_ptr,
                range_ptr,
                output_ptr
            );

        const bool result_matches =
            actual_success == cases[i].expected_success;

        const bool value_matches =
            actual_success
                ? (output == cases[i].expected_value)
                : (output == sentinel);

        const bool success =
            result_matches && value_matches;

        printf("RANGE_TEST %s: %s\n",
               cases[i].name,
               success ? "PASS" : "FAIL");

        if (success) {
            ++passed;
        }
    }

    printf("CORE_RANGE_SELFTEST: %s (%u/%u)\n",
           passed == count ? "PASS" : "FAIL",
           (unsigned)passed,
           (unsigned)count);
}


/* Development-only alarm lifecycle self-test: no physical outputs. */
static void run_core_alarm_selftest(void)
{
    unsigned passed = 0;
    unsigned total = 0;
#define ALARM_CHECK(name, expression) do { \
    bool success = (expression); \
    ++total; \
    if (success) { ++passed; } \
    printf("ALARM_TEST %s: %s\n", name, success ? "PASS" : "FAIL"); \
} while (0)

    vg_alarm_id_allocator_t ids = {0};
    vg_alarm_id_allocator_init(&ids);
    vg_alarm_t alarm = {0};
    ALARM_CHECK("ZERO_RECORD_REJECTED", !vg_alarm_is_consistent(&alarm));
    ALARM_CHECK("NULL_CONSISTENCY_REJECTED", !vg_alarm_is_consistent(NULL));
    ALARM_CHECK("NULL_ACK_REJECTED", !vg_alarm_try_acknowledge(NULL, 10));
    ALARM_CHECK("NULL_CLEAR_REJECTED", !vg_alarm_try_clear_condition(NULL, 10));
    ALARM_CHECK("RAISE_SIMULATION", vg_alarm_try_raise(
        &ids, &alarm, 2, VG_SOURCE_SIMULATION, 1, 7, 100));
    ALARM_CHECK("FIRST_ID_AND_STATE", alarm.id == 1 &&
        alarm.state == VG_ALARM_STATE_ACTIVE_UNACK && alarm.condition_active);
    ALARM_CHECK("INITIAL_TIMESTAMPS_ABSENT", !alarm.acknowledged &&
        !alarm.has_acknowledged_at && !alarm.has_cleared_at &&
        alarm.raised_at == 100 && vg_alarm_is_consistent(&alarm));
    ALARM_CHECK("REJECT_EARLY_ACK", !vg_alarm_try_acknowledge(&alarm, 99) &&
        alarm.state == VG_ALARM_STATE_ACTIVE_UNACK && !alarm.acknowledged);
    ALARM_CHECK("ACK_ACTIVE", vg_alarm_try_acknowledge(&alarm, 110));
    ALARM_CHECK("ACK_DOES_NOT_CLEAR", alarm.condition_active &&
        alarm.state == VG_ALARM_STATE_ACTIVE_ACK && alarm.acknowledged &&
        alarm.raised_at == 100 && !alarm.has_cleared_at);
    ALARM_CHECK("ACK_TIMESTAMP", alarm.has_acknowledged_at &&
        alarm.acknowledged_at == 110 && vg_alarm_is_consistent(&alarm));
    ALARM_CHECK("REPEAT_ACK_REJECTED", !vg_alarm_try_acknowledge(&alarm, 111) &&
        alarm.acknowledged_at == 110);
    ALARM_CHECK("CLEAR_BEFORE_ACK_REJECTED", !vg_alarm_try_clear_condition(&alarm, 109) &&
        alarm.condition_active && !alarm.has_cleared_at);
    ALARM_CHECK("CLEAR_AFTER_RECOVERY", vg_alarm_try_clear_condition(&alarm, 130));
    ALARM_CHECK("CLEARED_PRESERVES_ACK", alarm.state == VG_ALARM_STATE_CLEARED &&
        !alarm.condition_active && alarm.acknowledged &&
        alarm.acknowledged_at == 110 && alarm.has_cleared_at &&
        alarm.cleared_at == 130 && vg_alarm_is_consistent(&alarm));
    ALARM_CHECK("REPEAT_CLEAR_REJECTED", !vg_alarm_try_clear_condition(&alarm, 140) &&
        alarm.cleared_at == 130);
    ALARM_CHECK("ACK_AFTER_CLEAR_REJECTED", !vg_alarm_try_acknowledge(&alarm, 140));
    ALARM_CHECK("REOPEN_SAME_RECORD_REJECTED", !vg_alarm_try_raise(
        &ids, &alarm, 2, VG_SOURCE_SIMULATION, 1, 7, 150) && ids.next_id == 2);

    vg_alarm_t second = {0};
    ALARM_CHECK("SECOND_ID_UNIQUE_IN_BOOT", vg_alarm_try_raise(
        &ids, &second, 3, VG_SOURCE_BENCH_TEST, 4, 9, 200) &&
        second.id == 2 && alarm.id != second.id);
    ALARM_CHECK("REJECT_BACKWARDS_CLEAR_UNACK", !vg_alarm_try_clear_condition(
        &second, 199) && second.condition_active && !second.has_cleared_at);
    ALARM_CHECK("CLEAR_UNACK", vg_alarm_try_clear_condition(&second, 200) &&
        second.state == VG_ALARM_STATE_CLEARED && !second.acknowledged &&
        !second.has_acknowledged_at && vg_alarm_is_consistent(&second));

    vg_alarm_t invalid = {0};
    ALARM_CHECK("UNKNOWN_MODE_REJECTED", !vg_alarm_try_raise(
        &ids, &invalid, 2, VG_SOURCE_UNKNOWN, 1, 9, 10) && ids.next_id == 3);
    ALARM_CHECK("PHYSICAL_MODE_REJECTED", !vg_alarm_try_raise(
        &ids, &invalid, 2, VG_SOURCE_PHYSICAL, 1, 9, 10) && ids.next_id == 3);
    ALARM_CHECK("ZERO_SOURCE_REJECTED", !vg_alarm_try_raise(
        &ids, &invalid, 0, VG_SOURCE_SIMULATION, 1, 9, 10) && ids.next_id == 3);
    ALARM_CHECK("ZERO_PRIORITY_REJECTED", !vg_alarm_try_raise(
        &ids, &invalid, 2, VG_SOURCE_SIMULATION, 0, 9, 10) && ids.next_id == 3);
    ALARM_CHECK("ZERO_REASON_REJECTED", !vg_alarm_try_raise(
        &ids, &invalid, 2, VG_SOURCE_SIMULATION, 1, 0, 10) && ids.next_id == 3);
    ALARM_CHECK("NULL_RAISE_REJECTED", !vg_alarm_try_raise(
        &ids, NULL, 2, VG_SOURCE_SIMULATION, 1, 9, 10) && ids.next_id == 3);
    ALARM_CHECK("NULL_ALLOCATOR_REJECTED", !vg_alarm_try_raise(
        NULL, &invalid, 2, VG_SOURCE_SIMULATION, 1, 9, 10) && invalid.id == 0);
    ids.next_id = UINT64_MAX;
    ALARM_CHECK("ALLOCATOR_OVERFLOW_GUARD", !vg_alarm_try_raise(
        &ids, &invalid, 2, VG_SOURCE_SIMULATION, 1, 9, 10) &&
        invalid.id == 0 && ids.next_id == UINT64_MAX);
    vg_alarm_t tampered = {0};
    vg_alarm_id_allocator_init(&ids);
    (void)vg_alarm_try_raise(&ids, &tampered, 5, VG_SOURCE_SIMULATION, 1, 3, 1);
    tampered.state = VG_ALARM_STATE_ACTIVE_ACK;
    ALARM_CHECK("INCONSISTENT_STATE_REJECTED", !vg_alarm_is_consistent(&tampered) &&
        !vg_alarm_try_acknowledge(&tampered, 5) &&
        !vg_alarm_try_clear_condition(&tampered, 6));

#undef ALARM_CHECK
    printf("CORE_ALARM_SELFTEST: %s (%u/%u)\n",
           passed == total ? "PASS" : "FAIL", passed, total);
}

void app_main(void)
{
    puts("Development self-test scaffold only; "
         "operational monitoring and alarm outputs are not implemented.");

    run_core_quality_selftest();
    run_source_mode_selftest();
    run_core_measurement_selftest();
    run_core_range_selftest();
    run_core_alarm_selftest();
}
