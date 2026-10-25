<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});

Route::middleware('device.response.no-store')->group(function () {
    Route::get('/login', [\App\Http\Controllers\MonitoringSessionController::class, 'create'])->name('login');
    Route::post('/login', [\App\Http\Controllers\MonitoringSessionController::class, 'store'])->middleware('throttle:5,1');
    Route::post('/logout', [\App\Http\Controllers\MonitoringSessionController::class, 'destroy'])->middleware('auth:web')->name('logout');
    Route::middleware('auth:web')->get('/monitoring', \App\Http\Controllers\MonitoringController::class)->name('monitoring.index');
    Route::middleware('auth:web')->get('/monitoring/{device}', \App\Http\Controllers\MonitoringController::class)
        ->where('device', '[A-Za-z0-9._:-]{1,48}')->name('monitoring.device');
});
