<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class RunpodService
{
    /**
     * Trigger training task on Runpod
     */
    public function train(array $params)
    {
        $apiKey = env('RUNPOD_API_KEY');
        $trainingUrl = env('AI_TRAINING_URL', 'http://127.0.0.1:8001/train');

        if (!$apiKey) {
            // Local Fallback (Ke worker lokal kita di port 8001)
            $response = Http::post($trainingUrl, $params);

            return [
                'status' => 'success',
                'mode' => 'local',
                'response' => $response->json(),
                'message' => 'Training started on local worker.'
            ];
        }

        // Request ke Runpod API
        $response = Http::withHeaders([
            'Authorization' => "Bearer $apiKey",
            'Content-Type' => 'application/json',
        ])->post($trainingUrl, [
            'input' => $params // Runpod Serverless biasanya membungkus dalam 'input'
        ]);

        return [
            'status' => 'success',
            'mode' => 'runpod',
            'response' => $response->json(),
            'message' => 'Training triggered on Runpod Cloud.'
        ];
    }

    /**
     * Alias for train method to match controller call
     */
    public function startTraining($userId, $localPath)
    {
        return $this->train([
            'user_id' => $userId,
            'audio_path' => $localPath,
            'model_name' => 'voice_' . $userId . '_' . time()
        ]);
    }
}
