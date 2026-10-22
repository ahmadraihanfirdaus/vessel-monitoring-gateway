<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});

// Phase 9 development-only dashboard; authenticated users only.
Route::middleware('auth')->get('/monitoring', function () {
    return view('monitoring.index');
});
