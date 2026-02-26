<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\RunpodService;
use App\Services\StorageService;
use Illuminate\Support\Facades\Log;

class VoiceTrainingController extends Controller
{
    protected $runpod;
    protected $storage;

    public function __construct(RunpodService $runpod, StorageService $storage)
    {
        $this->runpod = $runpod;
        $this->storage = $storage;
    }

    /**
     * Trigger proses training otomatis via RunPod
     */
    public function store(Request $request)
    {
        $request->validate([
            'audio'      => 'required|file|mimes:wav,mp3,m4a|max:524288', // Naikkan ke 512MB
            'model_name' => 'nullable|string',
            'epochs'     => 'nullable|integer|min:1|max:500'
        ]);

        try {
            $userId    = $request->user()?->id ?? 1;
            $audioFile = $request->file('audio');

            // 1. Simpan sementara di lokal
            $tempPath      = $audioFile->store('temp_audio', 'public');
            $fullLocalPath = storage_path('app/public/' . $tempPath);

            // 2. Upload ke Cloudflare R2
            $cloudPath = "training/raw/{$userId}/" . time() . "_" . $audioFile->getClientOriginalName();
            Log::info("📤 Uploading audio to R2: {$cloudPath}");
            $this->storage->uploadToCloud($fullLocalPath, $cloudPath);

            // 3. Trigger training di RunPod
            Log::info("🚀 Triggering RunPod training for User {$userId}");
            $response = $this->runpod->train([
                'user_id'    => (string) $userId,
                'audio_path' => $cloudPath,
                'model_name' => $request->input('model_name', 'Premium_Voice'),
                'epochs'     => (int) $request->input('epochs', 30)
            ]);

            // 4. Hapus file lokal sementara
            @unlink($fullLocalPath);

            return response()->json([
                'success' => true,
                'message' => 'Training pipeline started successfully!',
                'data'    => $response
            ]);

        } catch (\Exception $e) {
            Log::error("❌ Training Error: " . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'Failed to start training: ' . $e->getMessage()
            ], 500);
        }
    }
}
