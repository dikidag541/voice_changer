<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\RunpodService;

class VoiceTrainingController extends Controller
{
    protected $runpod;

    public function __construct(RunpodService $runpod)
    {
        $this->runpod = $runpod;
    }

    public function store(Request $request)
    {
        $request->validate(['audio' => 'required|file|mimes:wav,mp3,m4a|max:50000']);

        $userId = $request->user()?->id ?? 'guest';
        $file = $request->file('audio');

        // 1. Upload ke S3 (Cloudflare R2)
        // Simpan di folder raw_audio dengan nama unik
        $path = $file->storeAs(
            "raw_audio/{$userId}",
            time() . '_' . $file->getClientOriginalName(),
            's3'
        );

        // 2. Trigger Runpod dengan path remote S3
        $this->runpod->startTraining($userId, $path);

        return response()->json([
            'status' => 'success',
            'message' => 'Training started automatically on RunPod.',
            'remote_path' => $path
        ]);
    }
}
