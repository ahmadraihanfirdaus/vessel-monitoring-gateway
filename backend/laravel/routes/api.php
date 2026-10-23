<?php

use App\Http\Controllers\Api\TelemetryIngestController;
use Illuminate\Support\Facades\Route;

Route::post('/v1/telemetry', TelemetryIngestController::class)
    ->middleware([
        'device.response.no-store',
        'telemetry.payload.size',
        'device.auth',
    ]);

Route::post('/v1/events', \App\Http\Controllers\Api\EventIngestController::class)
    ->middleware([
        'device.response.no-store',
        'telemetry.payload.size',
        'device.auth',
    ]);

Route::get('/v1/device/state', \App\Http\Controllers\Api\DeviceStateController::class)
    ->middleware(['device.response.no-store', 'device.auth']);

Route::get('/v1/device/history', \App\Http\Controllers\Api\DeviceHistoryController::class)
    ->middleware(['device.response.no-store', 'device.auth']);

Route::get('/v1/device/health', \App\Http\Controllers\Api\DeviceHealthController::class)
    ->middleware(['device.response.no-store', 'device.auth']);
