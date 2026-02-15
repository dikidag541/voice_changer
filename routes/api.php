<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\VoiceChangerController;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

Route::post('/clone-voice', [VoiceChangerController::class, 'clone']);
Route::get('/voice-status/{id}', [VoiceChangerController::class, 'checkStatus']);
Route::get('/engine-status', [VoiceChangerController::class, 'engineStatus']);
