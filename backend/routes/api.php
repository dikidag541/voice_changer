<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\VoiceChangerController;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

Route::middleware('auth:sanctum')->group(function () {
    Route::post('/initialize-voice', [VoiceChangerController::class, 'initializeVoice']);
    Route::post('/clone-voice', [VoiceChangerController::class, 'clone']);
    Route::post('/start-training', [VoiceChangerController::class, 'startTraining']);
    Route::get('/engine-status', [VoiceChangerController::class, 'engineStatus']);
    
    // Original SaaS Routes
    Route::post('/train', [\App\Http\Controllers\VoiceTrainingController::class, 'store']);
    Route::post('/generate', [\App\Http\Controllers\VoiceGenerateController::class, 'generate']);
});

Route::get('/characters', [\App\Http\Controllers\CharacterController::class, 'index']);
Route::get('/characters/{id}', [\App\Http\Controllers\CharacterController::class, 'show']);
