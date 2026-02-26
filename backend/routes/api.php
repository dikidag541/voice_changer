<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\VoiceChangerController;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

// Public routes
Route::get('/characters', [\App\Http\Controllers\CharacterController::class, 'index']);
Route::get('/characters/{id}', [\App\Http\Controllers\CharacterController::class, 'show']);
Route::get('/engine-status', [VoiceChangerController::class, 'engineStatus']);
Route::get('/balance', [VoiceChangerController::class, 'getBalance']);

// Training & Generation (Public for testing)
Route::post('/initialize-voice', [VoiceChangerController::class, 'initializeVoice']);
Route::post('/clone-voice', [VoiceChangerController::class, 'clone']);
Route::post('/start-training', [VoiceChangerController::class, 'startTraining']);
Route::get('/training-status', [VoiceChangerController::class, 'trainingStatus']);
Route::get('/list-pods', [VoiceChangerController::class, 'listPods']);
Route::post('/terminate-pod', [VoiceChangerController::class, 'terminatePod']);
Route::post('/train', [\App\Http\Controllers\VoiceTrainingController::class, 'store']);
Route::post('/generate', [\App\Http\Controllers\VoiceGenerateController::class, 'generate']);

// Protected routes (User only)
Route::middleware('auth:sanctum')->group(function () {
    // Tambahkan route yang benar-benar butuh login di sini nanti
});
