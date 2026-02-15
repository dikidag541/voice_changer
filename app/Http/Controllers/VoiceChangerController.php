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
     * Voice cloning dengan XTTS v2
     */
    /**
     * Voice cloning asynchronous via Queue API
     */
    public function clone(Request $request)
    {
        $request->validate([
            'audio' => 'required|file|max:35000',
            'text' => 'required|string|max:2000',
            'model_type' => 'nullable|string|in:fine-tuned,base',
        ]);

        $audio = $request->file('audio');
        $text = $request->input('text');
        $modelType = $request->input('model_type', 'fine-tuned');
        $userId = Auth::id();

        // 1. Catat di Database dengan status 'queued'
        $generationId = DB::table('voice_generations')->insertGetId([
            'user_id' => $userId,
            'input_text' => $text,
            'reference_audio_path' => $audio->store('references', 'public'),
            'status' => 'queued',
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        $baseUrl = env('AI_XTTS_URL', 'http://localhost:5002');

        try {
            // 2. Kirim ke Queue API Python
            $response = Http::timeout(30)->attach(
                'audio',
                file_get_contents($audio->getRealPath()),
                'ref.wav'
            )->post("{$baseUrl}/generate", [
                'text' => $text,
                'model_type' => $modelType,
            ]);

            if ($response->successful()) {
                $jobId = $response->json()['job_id'];

                // Update DB dengan job_id dari Python
                DB::table('voice_generations')->where('id', $generationId)->update([
                    'external_job_id' => $jobId,
                    'updated_at' => now(),
                ]);

                return response()->json([
                    'success' => true,
                    'generation_id' => $generationId,
                    'job_id' => $jobId,
                    'status' => 'queued'
                ], 202);
            }

            throw new \Exception($response->body() ?: 'Queue API Error');

        } catch (\Exception $e) {
            DB::table('voice_generations')->where('id', $generationId)->update([
                'status' => 'failed',
                'updated_at' => now(),
            ]);

            return response()->json(['error' => 'AI Server Error: ' . $e->getMessage()], 500);
        }
    }

    /**
     * Polling status dari Frontend
     */
    public function checkStatus($id)
    {
        $gen = DB::table('voice_generations')->where('id', $id)->first();
        if (!$gen) return response()->json(['error' => 'Not found'], 404);

        if ($gen->status === 'completed') {
            return response()->json([
                'status' => 'completed',
                'audio_url' => Storage::disk('public')->url($gen->result_audio_path)
            ]);
        }

        if ($gen->status === 'failed') return response()->json(['status' => 'failed']);

        // Jika masih queued/processing, tanya ke Python
        $baseUrl = env('AI_XTTS_URL', 'http://localhost:5002');
        try {
            $response = Http::get("{$baseUrl}/status/{$gen->external_job_id}");
            $data = $response->json();

            if ($data['status'] === 'completed') {
                // DOWNLOAD FILE DARI PYTHON KE LARAVEL
                $audioContent = Http::get("{$baseUrl}/download/{$gen->external_job_id}")->body();
                $filename = 'generated/' . $gen->external_job_id . '.wav';
                
                Storage::disk('public')->put($filename, $audioContent);

                DB::table('voice_generations')->where('id', $id)->update([
                    'status' => 'completed',
                    'result_audio_path' => $filename,
                    'updated_at' => now()
                ]);

                return response()->json([
                    'status' => 'completed',
                    'audio_url' => Storage::disk('public')->url($filename)
                ]);
            }

            return response()->json(['status' => $data['status']]);

        } catch (\Exception $e) {
            return response()->json(['status' => $gen->status, 'message' => 'Waiting for engine...']);
        }
    }

    public function engineStatus()
    {
        $url = env('AI_XTTS_URL', 'http://localhost:5002');
        try {
            $status = Http::timeout(2)->get("{$url}/health");
            return response()->json(['available' => $status->successful(), 'details' => $status->json()]);
        } catch (\Exception $e) {
            return response()->json(['available' => false]);
        }
    }
}
