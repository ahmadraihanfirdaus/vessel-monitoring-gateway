<?php

use Illuminate\Support\Facades\Route;

Route::middleware('device.response.no-store')->group(function () {
    // A project entry, independent of user-controlled redirect/query values.
    // The existing monitoring auth/grant boundary owns access to actual data.
    Route::get('/', static fn () => redirect()->route('monitoring.index'))->name('monitoring.entry');
    Route::get('/login', [\App\Http\Controllers\MonitoringSessionController::class, 'create'])->name('login');
    Route::post('/login', [\App\Http\Controllers\MonitoringSessionController::class, 'store'])->middleware('throttle:5,1');
    Route::post('/logout', [\App\Http\Controllers\MonitoringSessionController::class, 'destroy'])->middleware('auth:web')->name('logout');
    Route::middleware('auth:web')->get('/monitoring', \App\Http\Controllers\MonitoringController::class)->name('monitoring.index');
    Route::middleware('auth:web')->get('/monitoring/{device}', \App\Http\Controllers\MonitoringController::class)
        ->where('device', '[A-Za-z0-9._:-]{1,48}')->name('monitoring.device');
});
