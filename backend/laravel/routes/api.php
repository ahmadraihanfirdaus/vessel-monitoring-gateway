<?php

use App\Http\Controllers\Api\TelemetryIngestController;
use Illuminate\Support\Facades\Route;

Route::post('/v1/telemetry', TelemetryIngestController::class)
    ->middleware([
        'telemetry.payload.size',
        'device.auth',
    ]);

Route::post('/v1/events', \App\Http\Controllers\Api\EventIngestController::class)
    ->middleware([
        'telemetry.payload.size',
        'device.auth',
    ]);

Route::get('/v1/device/state', \App\Http\Controllers\Api\DeviceStateController::class)
    ->middleware('device.auth');

Route::get('/v1/device/history', \App\Http\Controllers\Api\DeviceHistoryController::class)
    ->middleware('device.auth');

Route::get('/v1/device/health', \App\Http\Controllers\Api\DeviceHealthController::class)
    ->middleware('device.auth');
