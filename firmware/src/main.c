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
#include "core_scheduler.h"
#include "core_diagnostics.h"
#include "core_event_journal.h"
#include "core_flow.h"

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


/* Pure firmware-core model self-tests. No operational scheduler or GPIO. */
static void vg_core_test_record(const char *category, const char *name,
    bool success, unsigned *passed, unsigned *total)
{
    ++*total;
    if (success) ++*passed;
    printf("%s %s: %s\n", category, name, success ? "PASS" : "FAIL");
}

#define VG_TEST(category, name, expr) do { \
    const bool ok = (expr); \
    vg_core_test_record(category, name, ok, &passed, &total); \
} while (0)

static void run_core_scheduler_selftest(void)
{
    unsigned passed = 0, total = 0;
    vg_scheduler_t s = {0};
    uint64_t skipped = 99;
    VG_TEST("SCHED_TEST", "ZERO_INITIALIZED_REJECTED",
        vg_scheduler_poll(&s, 99, &skipped) == VG_SCHED_INVALID && skipped == 99);
    VG_TEST("SCHED_TEST", "NULL_SCHED_REJECTED",
        vg_scheduler_poll(NULL, 100, &skipped) == VG_SCHED_INVALID);
    VG_TEST("SCHED_TEST", "ZERO_INTERVAL_REJECTED",
        !vg_scheduler_init(&s, 0, 100) && !s.initialized);
    VG_TEST("SCHED_TEST", "INIT", vg_scheduler_init(&s, 10, 100));
    VG_TEST("SCHED_TEST", "INITIAL_WAIT",
        vg_scheduler_poll(&s, 99, &skipped) == VG_SCHED_WAIT && skipped == 0);
    VG_TEST("SCHED_TEST", "EXACT_DUE",
        vg_scheduler_poll(&s, 100, &skipped) == VG_SCHED_DUE && skipped == 0);
    VG_TEST("SCHED_TEST", "NEXT_DEADLINE", s.next_due_ms == 110);
    VG_TEST("SCHED_TEST", "WAIT_NO_SPIN",
        vg_scheduler_poll(&s, 105, &skipped) == VG_SCHED_WAIT && s.next_due_ms == 110);
    VG_TEST("SCHED_TEST", "SKIP_LATE_PERIODS",
        vg_scheduler_poll(&s, 132, &skipped) == VG_SCHED_DUE && skipped == 2 &&
        s.next_due_ms == 140);
    VG_TEST("SCHED_TEST", "TIME_REGRESSION_REJECTED",
        vg_scheduler_poll(&s, 131, &skipped) == VG_SCHED_TIME_REGRESSION &&
        s.next_due_ms == 140 && s.last_now_ms == 132);
    VG_TEST("SCHED_TEST", "DUE_AFTER_REGRESSION",
        vg_scheduler_poll(&s, 140, &skipped) == VG_SCHED_DUE && s.next_due_ms == 150);
    VG_TEST("SCHED_TEST", "NULL_SKIPPED_PTR",
        vg_scheduler_poll(&s, 149, NULL) == VG_SCHED_INVALID && s.last_now_ms == 140);
    vg_scheduler_t edge = {0};
    VG_TEST("SCHED_TEST", "EDGE_INIT",
        vg_scheduler_init(&edge, 5, UINT64_MAX - 1));
    VG_TEST("SCHED_TEST", "OVERFLOW_FINITE_DUE",
        vg_scheduler_poll(&edge, UINT64_MAX - 1, &skipped) == VG_SCHED_DUE &&
        edge.exhausted && skipped == 0);
    VG_TEST("SCHED_TEST", "EXHAUSTED_EXPLICIT",
        vg_scheduler_poll(&edge, UINT64_MAX, &skipped) == VG_SCHED_EXHAUSTED);
    VG_TEST("SCHED_TEST", "NULL_INIT_REJECTED",
        !vg_scheduler_init(NULL, 1, 0));
    printf("CORE_SCHEDULER_SELFTEST: %s (%u/%u)\n",
        passed == total ? "PASS" : "FAIL", passed, total);
}

static void run_core_diagnostics_selftest(void)
{
    unsigned passed = 0, total = 0;
    vg_diagnostic_t d = {0};
    vg_measurement_t valid = {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 5.0f};
    vg_measurement_t missing = {VG_SOURCE_SIMULATION, VG_QUALITY_MISSING, false, 0.0f};
    vg_measurement_t stale = {VG_SOURCE_SIMULATION, VG_QUALITY_STALE, true, 5.0f};
    vg_measurement_t invalid = {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, NAN};
    VG_TEST("DIAG_TEST", "ZERO_UNKNOWN", d.health == VG_DIAG_UNKNOWN && !d.has_observation);
    VG_TEST("DIAG_TEST", "NULL_STATE_REJECTED",
        vg_diagnostic_observe(NULL, &valid, 1) == VG_DIAG_REJECTED);
    VG_TEST("DIAG_TEST", "NULL_MEASUREMENT_REJECTED",
        vg_diagnostic_observe(&d, NULL, 1) == VG_DIAG_REJECTED);
    VG_TEST("DIAG_TEST", "FIRST_VALID_GOOD",
        vg_diagnostic_observe(&d, &valid, 10) == VG_DIAG_GOOD);
    VG_TEST("DIAG_TEST", "HEALTHY_STATE",
        d.health == VG_DIAG_HEALTHY && d.consecutive_failures == 0 &&
        d.source_mode == VG_SOURCE_SIMULATION);
    VG_TEST("DIAG_TEST", "MISSING_FAULT_STARTED",
        vg_diagnostic_observe(&d, &missing, 20) == VG_DIAG_FAULT_STARTED &&
        d.health == VG_DIAG_FAULT && d.consecutive_failures == 1);
    VG_TEST("DIAG_TEST", "STALE_FAULT_CONTINUING",
        vg_diagnostic_observe(&d, &stale, 30) == VG_DIAG_FAULT_CONTINUING &&
        d.consecutive_failures == 2);
    VG_TEST("DIAG_TEST", "NAN_FAULT_CONTINUING",
        vg_diagnostic_observe(&d, &invalid, 40) == VG_DIAG_FAULT_CONTINUING &&
        d.consecutive_failures == 3);
    VG_TEST("DIAG_TEST", "RECOVERY",
        vg_diagnostic_observe(&d, &valid, 50) == VG_DIAG_RECOVERED &&
        d.health == VG_DIAG_HEALTHY && d.consecutive_failures == 0);
    VG_TEST("DIAG_TEST", "REPEATED_VALID_GOOD",
        vg_diagnostic_observe(&d, &valid, 60) == VG_DIAG_GOOD);
    VG_TEST("DIAG_TEST", "BACKWARDS_TIME_REJECTED",
        vg_diagnostic_observe(&d, &missing, 59) == VG_DIAG_REJECTED &&
        d.health == VG_DIAG_HEALTHY && d.last_observed_ms == 60);
    vg_measurement_t bench = {VG_SOURCE_BENCH_TEST, VG_QUALITY_VALID, true, 4.0f};
    VG_TEST("DIAG_TEST", "MODE_SWITCH_REJECTED",
        vg_diagnostic_observe(&d, &bench, 61) == VG_DIAG_REJECTED &&
        d.source_mode == VG_SOURCE_SIMULATION);
    vg_measurement_t physical = {VG_SOURCE_PHYSICAL, VG_QUALITY_VALID, true, 4.0f};
    VG_TEST("DIAG_TEST", "PHYSICAL_REJECTED",
        vg_diagnostic_observe(&d, &physical, 61) == VG_DIAG_REJECTED);
    vg_measurement_t unknown = {VG_SOURCE_UNKNOWN, VG_QUALITY_VALID, true, 4.0f};
    VG_TEST("DIAG_TEST", "UNKNOWN_MODE_REJECTED",
        vg_diagnostic_observe(&d, &unknown, 61) == VG_DIAG_REJECTED);
    vg_diagnostic_t fresh = {0};
    VG_TEST("DIAG_TEST", "FIRST_MISSING_IS_FAULT",
        vg_diagnostic_observe(&fresh, &missing, 0) == VG_DIAG_FAULT_STARTED);
    fresh.consecutive_failures = UINT32_MAX;
    VG_TEST("DIAG_TEST", "FAILURE_COUNTER_SATURATES",
        vg_diagnostic_observe(&fresh, &missing, 1) == VG_DIAG_FAULT_CONTINUING &&
        fresh.consecutive_failures == UINT32_MAX);
    VG_TEST("DIAG_TEST", "FIRST_BENCH_SUPPORTED",
        vg_diagnostic_observe(&(vg_diagnostic_t){0}, &bench, 1) == VG_DIAG_GOOD);
    VG_TEST("DIAG_TEST", "MISSING_IS_NOT_NUMERIC_ZERO",
        vg_diagnostic_observe(&d, &missing, 60) == VG_DIAG_FAULT_STARTED &&
        d.health == VG_DIAG_FAULT);
    VG_TEST("DIAG_TEST", "SAME_TIMESTAMP_ALLOWED",
        vg_diagnostic_observe(&d, &valid, 60) == VG_DIAG_RECOVERED);
    printf("CORE_DIAGNOSTICS_SELFTEST: %s (%u/%u)\n",
        passed == total ? "PASS" : "FAIL", passed, total);
}

static void run_core_journal_selftest(void)
{
    unsigned passed = 0, total = 0;
    vg_event_journal_t journal = {0};
    uint64_t output = 999;
    vg_journal_event_t event = {0};
    VG_TEST("JOURNAL_TEST", "ZERO_UNINITIALIZED_REJECTED",
        !vg_journal_append(&journal, 0, 2, VG_SOURCE_SIMULATION,
            VG_EVENT_FAULT, 10, &output) && output == 999);
    VG_TEST("JOURNAL_TEST", "NULL_INIT_REJECTED", !vg_journal_init(NULL));
    VG_TEST("JOURNAL_TEST", "INIT", vg_journal_init(&journal));
    VG_TEST("JOURNAL_TEST", "FIRST_EVENT",
        vg_journal_append(&journal, 3, 2, VG_SOURCE_SIMULATION,
            VG_EVENT_ALARM_RAISED, 10, &output) && output == 1 && journal.count == 1);
    VG_TEST("JOURNAL_TEST", "READ_FIRST",
        vg_journal_read(&journal, 0, &event) && event.event_id == 1 &&
        event.linked_alarm_id == 3 && event.source_id == 2 &&
        event.source_mode == VG_SOURCE_SIMULATION && event.occurred_at_ms == 10);
    VG_TEST("JOURNAL_TEST", "INVALID_MODE_REJECTED",
        !vg_journal_append(&journal, 0, 2, VG_SOURCE_UNKNOWN,
            VG_EVENT_FAULT, 11, &output) && journal.count == 1);
    VG_TEST("JOURNAL_TEST", "PHYSICAL_REJECTED",
        !vg_journal_append(&journal, 0, 2, VG_SOURCE_PHYSICAL,
            VG_EVENT_FAULT, 11, &output) && journal.count == 1);
    VG_TEST("JOURNAL_TEST", "ZERO_SOURCE_REJECTED",
        !vg_journal_append(&journal, 0, 0, VG_SOURCE_SIMULATION,
            VG_EVENT_FAULT, 11, &output));
    VG_TEST("JOURNAL_TEST", "UNKNOWN_EVENT_REJECTED",
        !vg_journal_append(&journal, 0, 2, VG_SOURCE_SIMULATION,
            VG_EVENT_UNKNOWN, 11, &output));
    VG_TEST("JOURNAL_TEST", "TIME_REGRESSION_REJECTED",
        !vg_journal_append(&journal, 0, 2, VG_SOURCE_SIMULATION,
            VG_EVENT_FAULT, 9, &output));
    VG_TEST("JOURNAL_TEST", "NULL_OUTPUT_REJECTED",
        !vg_journal_append(&journal, 0, 2, VG_SOURCE_SIMULATION,
            VG_EVENT_FAULT, 11, NULL));
    VG_TEST("JOURNAL_TEST", "SECOND_EVENT_ID",
        vg_journal_append(&journal, 0, 2, VG_SOURCE_BENCH_TEST,
            VG_EVENT_FAULT, 10, &output) && output == 2 && journal.count == 2);
    VG_TEST("JOURNAL_TEST", "READ_OOB_REJECTED",
        !vg_journal_read(&journal, journal.count, &event));
    VG_TEST("JOURNAL_TEST", "NULL_READ_REJECTED",
        !vg_journal_read(&journal, 0, NULL));
    bool fill_ok = true;
    for (size_t i = journal.count; i < VG_JOURNAL_CAPACITY; ++i) {
        fill_ok &= vg_journal_append(&journal, 0, 2, VG_SOURCE_SIMULATION,
            VG_EVENT_FAULT, (uint64_t)(11 + i), &output);
    }
    VG_TEST("JOURNAL_TEST", "FILL_BOUNDED_CAPACITY",
        fill_ok && journal.count == VG_JOURNAL_CAPACITY);
    VG_TEST("JOURNAL_TEST", "FULL_REJECTS_NO_OVERWRITE",
        !vg_journal_append(&journal, 0, 2, VG_SOURCE_SIMULATION,
            VG_EVENT_FAULT, 40, &output) && journal.count == VG_JOURNAL_CAPACITY &&
        journal.rejected_full == 1 && journal.events[0].event_id == 1 &&
        journal.next_id == VG_JOURNAL_CAPACITY + 1);
    VG_TEST("JOURNAL_TEST", "FULL_COUNT_INCREASES",
        !vg_journal_append(&journal, 0, 2, VG_SOURCE_SIMULATION,
            VG_EVENT_FAULT, 41, &output) && journal.rejected_full == 2);
    vg_event_journal_t wrap = {0};
    (void)vg_journal_init(&wrap);
    wrap.next_id = UINT64_MAX;
    VG_TEST("JOURNAL_TEST", "ID_EXHAUSTION_REJECTED",
        !vg_journal_append(&wrap, 0, 2, VG_SOURCE_SIMULATION,
            VG_EVENT_FAULT, 0, &output));
    VG_TEST("JOURNAL_TEST", "BOOT_ZERO_TIMESTAMP_VALID",
        vg_journal_append(&(vg_event_journal_t){.initialized=true,.next_id=1},
            0, 2, VG_SOURCE_SIMULATION, VG_EVENT_FAULT, 0, &output) && output == 1);
    printf("CORE_JOURNAL_SELFTEST: %s (%u/%u)\n",
        passed == total ? "PASS" : "FAIL", passed, total);
}

#undef VG_TEST


/* Batch C2: deterministic, single-channel orchestration self-tests only. */
static void run_core_flow_selftest(void)
{
    unsigned passed = 0, total = 0;
#define FLOW_CHECK(name, expr) do { \
    const bool ok = (expr); \
    ++total; if (ok) ++passed; \
    printf("FLOW_TEST %s: %s\n", name, ok ? "PASS" : "FAIL"); \
} while (0)

    vg_core_flow_t flow = {0};
    vg_measurement_t good = {VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 42.0f};
    vg_measurement_t missing = {VG_SOURCE_SIMULATION, VG_QUALITY_MISSING, false, 0.0f};
    vg_measurement_t invalid = {VG_SOURCE_SIMULATION, VG_QUALITY_INVALID, true, 0.0f};
    uint64_t skipped = 999;
    vg_diag_result_t diagnostic = VG_DIAG_GOOD;
    FLOW_CHECK("ZERO_UNINITIALIZED", vg_flow_sample(&flow, &good, 10,
        &skipped, &diagnostic) == VG_FLOW_REJECTED && skipped == 999);
    FLOW_CHECK("NULL_INIT", !vg_flow_init(NULL, 4, VG_SOURCE_SIMULATION, 1, 2, 10, 10));
    FLOW_CHECK("BAD_INTERVAL", !vg_flow_init(&flow, 4, VG_SOURCE_SIMULATION, 1, 2, 0, 10));
    FLOW_CHECK("REJECT_PHYSICAL", !vg_flow_init(&flow, 4, VG_SOURCE_PHYSICAL, 1, 2, 10, 10));
    FLOW_CHECK("REJECT_UNKNOWN_MODE", !vg_flow_init(&flow, 4, VG_SOURCE_UNKNOWN, 1, 2, 10, 10));
    FLOW_CHECK("REJECT_ZERO_SOURCE", !vg_flow_init(&flow, 0, VG_SOURCE_SIMULATION, 1, 2, 10, 10));
    FLOW_CHECK("REJECT_ZERO_PRIORITY", !vg_flow_init(&flow, 4, VG_SOURCE_SIMULATION, 0, 2, 10, 10));
    FLOW_CHECK("REJECT_ZERO_REASON", !vg_flow_init(&flow, 4, VG_SOURCE_SIMULATION, 1, 0, 10, 10));
    FLOW_CHECK("INIT", vg_flow_init(&flow, 4, VG_SOURCE_SIMULATION, 1, 2, 10, 10));
    FLOW_CHECK("NULL_SAMPLE", vg_flow_sample(&flow, NULL, 10,
        &skipped, &diagnostic) == VG_FLOW_REJECTED);
    FLOW_CHECK("WAIT_WITHOUT_SAMPLE", vg_flow_sample(&flow, &missing, 5,
        &skipped, &diagnostic) == VG_FLOW_WAIT &&
        diagnostic == VG_DIAG_REJECTED && !flow.diagnostic.has_observation &&
        flow.journal.count == 0);
    FLOW_CHECK("FIRST_HEALTHY", vg_flow_sample(&flow, &good, 10,
        &skipped, &diagnostic) == VG_FLOW_PROCESSED &&
        diagnostic == VG_DIAG_GOOD && !flow.has_alarm && flow.journal.count == 0);
    FLOW_CHECK("NO_DUPLICATE_WHILE_WAIT", vg_flow_sample(&flow, &missing, 15,
        &skipped, &diagnostic) == VG_FLOW_WAIT && flow.journal.count == 0);
    FLOW_CHECK("MISSING_RAISES_ALARM", vg_flow_sample(&flow, &missing, 20,
        &skipped, &diagnostic) == VG_FLOW_PROCESSED &&
        diagnostic == VG_DIAG_FAULT_STARTED && flow.has_alarm &&
        flow.last_alarm.state == VG_ALARM_STATE_ACTIVE_UNACK &&
        flow.journal.count == 1 && flow.journal.events[0].type == VG_EVENT_ALARM_RAISED &&
        flow.journal.events[0].linked_alarm_id == flow.last_alarm.id);
    FLOW_CHECK("ACK_JOURNALED", vg_flow_acknowledge(&flow, 21) &&
        flow.journal.count == 2 && flow.journal.events[1].type == VG_EVENT_ALARM_ACK);
    FLOW_CHECK("ACK_DOES_NOT_CLEAR", flow.last_alarm.condition_active &&
        flow.last_alarm.state == VG_ALARM_STATE_ACTIVE_ACK);
    FLOW_CHECK("DUPLICATE_ACK_REJECTED", !vg_flow_acknowledge(&flow, 22) &&
        flow.journal.count == 2);
    FLOW_CHECK("EARLY_ACK_REJECTED", !vg_flow_acknowledge(&flow, 19) &&
        flow.journal.count == 2);
    FLOW_CHECK("FAULT_CONTINUING_NO_REPEAT_EVENT", vg_flow_sample(&flow, &invalid, 30,
        &skipped, &diagnostic) == VG_FLOW_PROCESSED &&
        diagnostic == VG_DIAG_FAULT_CONTINUING && flow.journal.count == 2);
    FLOW_CHECK("RECOVERY_CLEARS", vg_flow_sample(&flow, &good, 40,
        &skipped, &diagnostic) == VG_FLOW_PROCESSED &&
        diagnostic == VG_DIAG_RECOVERED && !flow.last_alarm.condition_active &&
        flow.last_alarm.state == VG_ALARM_STATE_CLEARED && flow.journal.count == 3 &&
        flow.journal.events[2].type == VG_EVENT_ALARM_CLEARED);
    FLOW_CHECK("ACK_AFTER_CLEAR_REJECTED", !vg_flow_acknowledge(&flow, 41));
    FLOW_CHECK("ANOTHER_FAULT_NEW_ID", vg_flow_sample(&flow, &missing, 50,
        &skipped, &diagnostic) == VG_FLOW_PROCESSED &&
        flow.last_alarm.id == 2 && flow.journal.count == 4 &&
        flow.journal.events[3].linked_alarm_id == 2);
    FLOW_CHECK("SKIP_LATE_PERIODS", vg_flow_sample(&flow, &missing, 90,
        &skipped, &diagnostic) == VG_FLOW_PROCESSED &&
        skipped == 3 && diagnostic == VG_DIAG_FAULT_CONTINUING);
    FLOW_CHECK("REGRESSION_NOT_APPLIED", vg_flow_sample(&flow, &good, 70,
        &skipped, &diagnostic) == VG_FLOW_TIME_REGRESSION &&
        flow.last_alarm.condition_active && flow.journal.count == 4);
    vg_measurement_t bench = {VG_SOURCE_BENCH_TEST, VG_QUALITY_VALID, true, 1.0f};
    FLOW_CHECK("SOURCE_MISMATCH_REJECTED", vg_flow_sample(&flow, &bench, 100,
        &skipped, &diagnostic) == VG_FLOW_REJECTED && flow.journal.count == 4);
    FLOW_CHECK("NULL_OUTPUT_REJECTED", vg_flow_sample(&flow, &good, 100,
        NULL, &diagnostic) == VG_FLOW_REJECTED);
    FLOW_CHECK("NULL_DIAG_REJECTED", vg_flow_sample(&flow, &good, 100,
        &skipped, NULL) == VG_FLOW_REJECTED);
    vg_core_flow_t bench_flow = {0};
    FLOW_CHECK("BENCH_MODE_ACCEPTED", vg_flow_init(&bench_flow, 7,
        VG_SOURCE_BENCH_TEST, 3, 9, 10, 10) &&
        vg_flow_sample(&bench_flow, &bench, 10, &skipped, &diagnostic) ==
        VG_FLOW_PROCESSED && bench_flow.diagnostic.health == VG_DIAG_HEALTHY);
    vg_core_flow_t tight = {0};
    (void)vg_flow_init(&tight, 5, VG_SOURCE_SIMULATION, 1, 2, 1, 0);
    FLOW_CHECK("FULL_PREP_FIRST", vg_flow_sample(&tight, &missing, 0,
        &skipped, &diagnostic) == VG_FLOW_PROCESSED && tight.journal.count == 1);
    /* Create seven valid events. The journal now has eight entries. */
    bool filled = true;
    for (uint64_t t = 1; t <= 7; ++t) {
        bool sample_ok = vg_flow_sample(&tight, (t % 2) ? &good : &missing, t,
            &skipped, &diagnostic) == VG_FLOW_PROCESSED;
        filled = filled && sample_ok;
    }
    FLOW_CHECK("JOURNAL_FILLED", filled && tight.journal.count == VG_JOURNAL_CAPACITY);
    const uint64_t old_deadline = tight.scheduler.next_due_ms;
    const uint64_t old_id = tight.last_alarm.id;
    const vg_diag_health_t old_health = tight.diagnostic.health;
    const size_t old_count = tight.journal.count;
    FLOW_CHECK("FULL_ROLLBACK", vg_flow_sample(&tight, &missing, 8,
        &skipped, &diagnostic) == VG_FLOW_JOURNAL_FULL &&
        tight.scheduler.next_due_ms == old_deadline &&
        tight.last_alarm.id == old_id && tight.diagnostic.health == old_health &&
        tight.journal.count == old_count && tight.alarm_ids.next_id == 5);
    FLOW_CHECK("FULL_RETRY_IDEMPOTENT", vg_flow_sample(&tight, &missing, 8,
        &skipped, &diagnostic) == VG_FLOW_JOURNAL_FULL &&
        tight.scheduler.next_due_ms == old_deadline && tight.journal.count == old_count);
    vg_core_flow_t ack_full = {0};
    (void)vg_flow_init(&ack_full, 8, VG_SOURCE_SIMULATION, 1, 2, 1, 10);
    (void)vg_flow_sample(&ack_full, &missing, 10, &skipped, &diagnostic);
    bool ack_setup = (ack_full.journal.count == 1 &&
        ack_full.last_alarm.state == VG_ALARM_STATE_ACTIVE_UNACK);
    uint64_t synthetic_id = 0;
    for (size_t i = 1; i < VG_JOURNAL_CAPACITY; ++i) {
        ack_setup = ack_setup && vg_journal_append(&ack_full.journal, 0, 8,
            VG_SOURCE_SIMULATION, VG_EVENT_FAULT, 10, &synthetic_id);
    }
    FLOW_CHECK("FULL_ACK_SETUP", ack_setup &&
        ack_full.journal.count == VG_JOURNAL_CAPACITY);
    FLOW_CHECK("FULL_ACK_ROLLBACK", !vg_flow_acknowledge(&ack_full, 11) &&
        ack_full.journal.count == VG_JOURNAL_CAPACITY &&
        ack_full.last_alarm.state == VG_ALARM_STATE_ACTIVE_UNACK &&
        !ack_full.last_alarm.acknowledged);
    FLOW_CHECK("NULL_ACK_REJECTED", !vg_flow_acknowledge(NULL, 99));
    FLOW_CHECK("NULL_FLOW_REJECTED", vg_flow_sample(NULL, &good, 10,
        &skipped, &diagnostic) == VG_FLOW_REJECTED);
    printf("CORE_FLOW_SELFTEST: %s (%u/%u)\n",
        passed == total ? "PASS" : "FAIL", passed, total);
#undef FLOW_CHECK
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
    run_core_scheduler_selftest();
    run_core_diagnostics_selftest();
    run_core_journal_selftest();
    run_core_flow_selftest();
}
