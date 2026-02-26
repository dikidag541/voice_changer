<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Cache;

use App\Services\RunpodService;
use App\Services\StorageService;

class VoiceChangerController extends Controller
{
    protected $runpod;
    protected $storage;

    public function __construct(RunpodService $runpod, StorageService $storage)
    {
        $this->runpod = $runpod;
        $this->storage = $storage;
    }

    /**
     * Step 1: Voice Initialization
     * Upload audio dan ambil ID embedding dari Python
     */
    public function initializeVoice(Request $request)
    {
        ini_set('memory_limit', '1024M');
        $request->validate([
            'audio' => 'required|file|max:524288', // 512MB
        ]);

        $audio = $request->file('audio');

        // SIMPAN: Agar bisa dipakai buat training nanti
        $filename = $audio->store('references', 'public');
        Log::info("✅ STEP 1: File profile disimpan: $filename (" . round($audio->getSize() / 1024 / 1024, 2) . " MB)");

        $baseUrl = env('AI_GENERATE_URL', 'http://localhost:5000');

        try {
            // Streaming agar tidak crash saat file 300MB+
            $response = Http::timeout(600)->attach(
                'audio',
                fopen($audio->getRealPath(), 'r'),
                $audio->getClientOriginalName()
            )->post("{$baseUrl}/extract_speaker");

            if ($response->successful()) {
                $data = $response->json();
                return response()->json([
                    'success' => true,
                    'speaker_id' => $data['speaker_id'],
                    'message' => 'Profile suara berhasil diekstrak dan disimpan di server.'
                ]);
            }

            return response()->json(['error' => 'Gagal memproses suara: ' . $response->body()], 500);
        } catch (\Exception $e) {
            Log::error("❌ INITIALIZE ERROR: " . $e->getMessage());
            return response()->json(['error' => 'Server AI Offline / Timeout'], 500);
        }
    }

    /**
     * Step 2: Voice Generation
     * Menggunakan speaker_id yang sudah disimpan
     */
    public function clone(Request $request)
    {
        // Validasi input
        $request->validate([
            'text' => 'required|string|max:500',
            'speaker_id' => 'nullable|string', // ID dari Step 1
            'audio' => 'nullable|file|max:524288', // Support fallback upload langsung
            'speed' => 'nullable|numeric|min:0.5|max:2.0',
        ]);

        $text = $request->input('text');
        $speakerId = $request->input('speaker_id');
        $speed = $request->input('speed', 1.0);
        $userId = Auth::check() ? Auth::id() : null;

        // Simpan data transaksi ke database (Opsional jika DB belum siap)
        $generationId = null;
        try {
            $generationId = DB::table('voice_generations')->insertGetId([
                'user_id' => $userId,
                'input_text' => $text,
                'reference_audio_path' => $request->hasFile('audio') ? $request->file('audio')->store('references', 'public') : 'using_cached_speaker',
                'status' => 'processing',
                'created_at' => now(),
                'updated_at' => now(),
            ]);
        } catch (\Exception $e) {
            // Silently fail if DB not ready
        }

        $baseUrl = env('AI_GENERATE_URL', 'http://localhost:5000');

        try {
            $postData = [
                'text' => $text,
                'speed' => $speed,
                'speaker_id' => $speakerId
            ];

            $requestChain = Http::timeout(300);

            if ($request->hasFile('audio')) {
                // Streaming upload
                $requestChain->attach(
                    'audio',
                    fopen($request->file('audio')->getRealPath(), 'r'),
                    $request->file('audio')->getClientOriginalName()
                );
            }

            $response = $requestChain->post("{$baseUrl}/clone", $postData);

            if ($response->successful() && strlen($response->body()) > 0) {
                $filename = 'generated/' . uniqid() . '.wav';
                Storage::disk('public')->put($filename, $response->body());

                // Update status sukses ke DB
                if ($generationId) {
                    try {
                        DB::table('voice_generations')->where('id', $generationId)->update([
                            'result_audio_path' => $filename,
                            'status' => 'completed',
                            'updated_at' => now(),
                        ]);
                    } catch (\Exception $e) {
                    }
                }

                // Return both binary audio and persistent URL
                $fileUrl = asset('storage/' . $filename);

                return response($response->body(), 200)
                    ->header('Content-Type', 'audio/wav')
                    ->header('X-Voice-Engine', 'xtts-v2')
                    ->header('X-File-URL', $fileUrl);
            }

            $pythonError = $response->body() ?: 'Unknown AI error';
            if ($generationId) {
                try {
                    DB::table('voice_generations')->where('id', $generationId)->update(['status' => 'failed']);
                } catch (\Exception $e) {
                }
            }

            return response()->json(['error' => 'AI Engine Error: ' . $pythonError], 500);
        } catch (\Exception $e) {
            return response()->json(['error' => 'AI Server Offline'], 500);
        }
    }

    public function startTraining(Request $request)
    {
        try {
            Log::info("🚀 [ON-DEMAND] Memulai Pipeline Training...");

            // 1. CARI & VALIDASI FILE
            $audioFile = $request->file('audio') ?? $request->file('file');
            $localPath = null;
            $filename = null;

            if ($audioFile) {
                // Scenario A: User upload file baru
                $filename = 'upload_' . time() . '_' . $audioFile->getClientOriginalName();
                $tempPath = $audioFile->storeAs('references', $filename, 'public');
                $localPath = storage_path('app/public/' . $tempPath);
                Log::info("📁 Menggunakan file upload baru: $filename");
            } else {
                // Scenario B: Gunakan default suara-30menit.wav
                $filename = 'suara-30menit.wav';
                $localPath = storage_path('app/public/references/' . $filename);

                if (!file_exists($localPath)) {
                    return response()->json(['error' => "File default $filename tidak ditemukan. Silakan upload file audio."], 422);
                }
                Log::info("📁 Menggunakan file default: $filename");
            }

            // 2. UPLOAD KE CLOUDFLARE R2
            $cloudPath = "training/raw/" . $filename;
            Log::info("☁️ [STEP 1] Mengunggah ke R2: $cloudPath");
            $this->storage->uploadToCloud($localPath, $cloudPath);

            // 3. SEWA GPU RTX 4090 (On-Demand)
            Log::info("🎮 [STEP 2] Memerintah RunPod untuk menyewa RTX 4090...");
            $podResponse = $this->runpod->createPod('training_' . time());

            if (!isset($podResponse['id'])) {
                return response()->json(['error' => 'Gagal menyewa GPU: ' . json_encode($podResponse)], 500);
            }

            // 4. SIMPAN METADATA UNTUK AUTO-TRIGGER
            Cache::put("pod_training_{$podResponse['id']}", [
                'audio_path' => $cloudPath,
                'user_id' => 'guest_admin',
                'epochs' => 100
            ], now()->addHour());

            return response()->json([
                'success' => true,
                'message' => 'Pipeline Berhasil Dimulai!',
                'pod_id' => $podResponse['id'],
                'file_used' => $filename,
                'instruction' => 'GPU sedang disiapkan. Proses training akan dimulai otomatis setelah Pod online.'
            ]);
        } catch (\Exception $e) {
            Log::error("❌ ERROR TRAINING: " . $e->getMessage());
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    public function listPods()
    {
        $pods = $this->runpod->listPods();
        return response()->json($pods);
    }

    public function trainingStatus(Request $request)
    {
        $podId = $request->get('pod_id');
        if (!$podId) {
            return response()->json(['error' => 'Missing pod_id'], 422);
        }

        $status = $this->runpod->getPodStatus($podId);

        // AUTO-TRIGGER: Jika pod sudah online tapi masih IDLE, suruh mulai training
        if (($status['status'] ?? '') === 'idle') {
            $data = Cache::get("pod_training_{$podId}");
            if ($data) {
                Log::info("🤖 [AUTO-TRIGGER] Pod $podId online. Memulai training...");
                $this->runpod->train([
                    'user_id' => $data['user_id'],
                    'audio_path' => $data['audio_path'],
                    'epochs' => $data['epochs'],
                    'model_name' => 'premium_voice'
                ], $podId); // Pass podId to use dynamic URL

                // Beri respon 'starting' agar UI tahu ini sedang diproses
                $status['status'] = 'running';
                $status['message'] = 'Memulai mesin training...';
                $status['progress_percent'] = 5;
            }
        }

        return response()->json($status);
    }

    public function terminatePod(Request $request)
    {
        $podId = $request->get('pod_id');
        if (!$podId) {
            return response()->json(['error' => 'Missing pod_id'], 422);
        }

        $response = $this->runpod->deletePod($podId);
        return response()->json(['success' => true, 'response' => $response]);
    }

    public function getBalance()
    {
        return response()->json($this->runpod->getBalance());
    }

    public function engineStatus()
    {
        $engines = [
            'xtts' => [
                'url' => env('AI_GENERATE_URL', 'http://127.0.0.1:5000'),
                'name' => 'XTTS v2',
                'quality' => 'Optimization: Indonesian'
            ]
        ];

        $results = [];
        foreach ($engines as $key => $info) {
            try {
                $status = Http::timeout(2)->get("{$info['url']}/health");
                $results[$key] = array_merge($info, [
                    'available' => $status->successful(),
                    'port' => parse_url($info['url'], PHP_URL_PORT),
                    'details' => $status->json()
                ]);
            } catch (\Exception $e) {
                $results[$key] = array_merge($info, [
                    'available' => false,
                    'port' => parse_url($info['url'], PHP_URL_PORT)
                ]);
            }
        }

        return response()->json(['engines' => $results]);
    }
}
