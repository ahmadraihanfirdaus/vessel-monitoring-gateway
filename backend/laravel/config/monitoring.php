<?php

return [
    // Explicit SIMULATION 1.1 vocabulary only; no automatic OEM interpretation.
    'presentation_profile' => env('MONITORING_PRESENTATION_PROFILE'),
    // No assumed engineering thresholds. Unset/invalid policy renders UNKNOWN.
    'stale_after_seconds' => env('MONITORING_STALE_AFTER_SECONDS'),
    'offline_after_seconds' => env('MONITORING_OFFLINE_AFTER_SECONDS'),
    // Explicit channel assignments are presentation configuration, not inferred
    // from arbitrary wire names. All channels are always visible in Overview.
    'channel_sections' => [
        'safety' => [], 'propulsion' => [], 'navigation' => [], 'power' => [],
    ],
];
