<?php

use App\Http\Controllers\Api\TelemetryIngestController;
use Illuminate\Support\Facades\Route;

Route::post('/v1/telemetry', TelemetryIngestController::class)
    ->middleware([
        'telemetry.payload.size',
        'device.auth',
    ]);
