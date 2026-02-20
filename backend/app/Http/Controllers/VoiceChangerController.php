<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Auth;

class VoiceChangerController extends Controller
{
    /**
     * Step 1: Voice Initialization
     * Upload audio dan ambil ID embedding dari Python
     */
    public function initializeVoice(Request $request)
    {
        $request->validate([
            'audio' => 'required|file|mimes:wav,mp3,m4a|max:35000',
        ]);

        $audio = $request->file('audio');
        $baseUrl = env('AI_GENERATE_URL', 'http://localhost:5000');

        try {
            $response = Http::timeout(60)->attach(
                'audio',
                file_get_contents($audio->getRealPath()),
                'ref.wav'
            )->post("{$baseUrl}/extract_speaker");

            if ($response->successful()) {
                $data = $response->json();
                return response()->json([
                    'success' => true,
                    'speaker_id' => $data['speaker_id'],
                    'message' => 'Profile suara berhasil diekstrak dan disimpan di server AI.'
                ]);
            }

            return response()->json(['error' => 'Gagal memproses suara: ' . $response->body()], 500);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Server AI Offline'], 500);
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
            'audio' => 'nullable|file|mimes:wav,mp3,m4a|max:35000', // Support fallback upload langsung
            'speed' => 'nullable|numeric|min:0.5|max:2.0',
        ]);

        $text = $request->input('text');
        $speakerId = $request->input('speaker_id');
        $speed = $request->input('speed', 1.0);
        $userId = Auth::check() ? Auth::id() : null;

        // Simpan data transaksi ke database
        $generationId = DB::table('voice_generations')->insertGetId([
            'user_id' => $userId,
            'input_text' => $text,
            'reference_audio_path' => $request->hasFile('audio') ? $request->file('audio')->store('references', 's3') : 'using_cached_speaker',
            'status' => 'processing',
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        $baseUrl = env('AI_GENERATE_URL', 'http://localhost:5000');

        try {
            $postData = [
                'text' => $text,
                'speed' => $speed,
                'speaker_id' => $speakerId
            ];

            $requestChain = Http::timeout(300);

            if ($request->hasFile('audio')) {
                $requestChain->attach(
                    'audio',
                    file_get_contents($request->file('audio')->getRealPath()),
                    'ref.wav'
                );
            }

            $response = $requestChain->post("{$baseUrl}/clone", $postData);

            if ($response->successful() && strlen($response->body()) > 0) {
                $filename = 'generated/' . uniqid() . '.wav';
                Storage::disk('s3')->put($filename, $response->body());

                // Update status sukses
                DB::table('voice_generations')->where('id', $generationId)->update([
                    'result_audio_path' => $filename,
                    'status' => 'completed',
                    'updated_at' => now(),
                ]);

                // Return both binary audio and persistent URL
                $fileUrl = Storage::disk('s3')->url($filename);

                return response($response->body(), 200)
                    ->header('Content-Type', 'audio/wav')
                    ->header('X-Voice-Engine', 'xtts-v2')
                    ->header('X-File-URL', $fileUrl);
            }

            $pythonError = $response->body() ?: 'Unknown AI error';
            DB::table('voice_generations')->where('id', $generationId)->update(['status' => 'failed']);

            return response()->json(['error' => 'AI Engine Error: ' . $pythonError], 500);
        } catch (\Exception $e) {
            return response()->json(['error' => 'AI Server Offline'], 500);
        }
    }

    public function startTraining(Request $request)
    {
        // Dataset path yang tadi kita upload ke R2
        $datasetPath = "datasets/my_voice/";
        $runpodService = new \App\Services\RunpodService();

        try {
            // Memanggil RunPod (Atau Local AI Server jika RunPod API Key kosong)
            $response = $runpodService->train([
                'user_id' => 'guest_admin',
                'audio_path' => $datasetPath,
                'model_name' => 'premium_voice_' . time()
            ]);

            return response()->json([
                'success' => true,
                'message' => 'Training Premium berhasil dipicu!',
                'data' => $response
            ]);
        } catch (\Exception $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
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
