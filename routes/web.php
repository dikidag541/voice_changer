<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});

Route::get('/debug', function () {
    return view('debug');
});

Route::get('/terms', function () {
    return view('terms');
});
