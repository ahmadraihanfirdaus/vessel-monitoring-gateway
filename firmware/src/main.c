
#include <stdio.h>

#include "core_types.h"

/*
 * Compile-time checks for firmware core data types.
 *
 * These checks do not verify sensor acquisition,
 * alarms, telemetry, or physical integration.
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

void app_main(void)
{
    puts("Development scaffold only; "
         "monitoring and alarms are not implemented.");
}
