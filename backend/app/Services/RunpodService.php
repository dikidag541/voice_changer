<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class RunpodService
{
    /**
     * Trigger training on a Pod
     */
    public function train(array $params, $podId = null)
    {
        $apiKey = env('RUNPOD_API_KEY');

        // Pilih URL: Jika ada podId (Dynamic), gunakan proxy. Jika tidak (Static), gunakan .env
        $trainingUrl = $podId
            ? "https://{$podId}-8888.proxy.runpod.net/train"
            : env('AI_TRAINING_URL');

        $isProxy = str_contains($trainingUrl, 'proxy.runpod.net');

        if ($isProxy) {
            $response = Http::withHeaders([
                'Authorization' => "Bearer $apiKey",
                'Content-Type' => 'application/json',
            ])->post($trainingUrl, $params);
        } else {
            // Serverless API call
            $response = Http::withHeaders([
                'Authorization' => "Bearer $apiKey",
                'Content-Type' => 'application/json',
            ])->post($trainingUrl, [
                'input' => $params
            ]);
        }

        return $response->json();
    }

    /**
     * Create a new GPU Pod (RTX 4090) otomatis via GraphQL
     * Pindah ke GraphQL karena REST API v1 sering bermasalah dengan schema
     */
    public function createPod($name = 'voice_changer_A40')
    {
        $apiKey = env('RUNPOD_API_KEY');
        $query = '
            mutation {
              podFindAndDeployOnDemand(
                input: {
                  cloudType: SECURE,
                  gpuCount: 1,
                  gpuTypeId: "NVIDIA A40",
                  imageName: "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",
                  containerDiskInGb: 30,
                  volumeInGb: 100,
                  volumeMountPath: "/workspace",
                  ports: "8888/http",
                  name: "' . $name . '",
                  env: [
                    { key: "AWS_ACCESS_KEY_ID", value: "' . env('AWS_ACCESS_KEY_ID') . '" },
                    { key: "AWS_SECRET_ACCESS_KEY", value: "' . env('AWS_SECRET_ACCESS_KEY') . '" },
                    { key: "AWS_DEFAULT_REGION", value: "' . env('AWS_DEFAULT_REGION', 'auto') . '" },
                    { key: "AWS_BUCKET", value: "' . env('AWS_BUCKET') . '" },
                    { key: "AWS_ENDPOINT", value: "' . env('AWS_ENDPOINT') . '" },
                    { key: "AWS_URL", value: "' . env('AWS_URL') . '" }
                  ],
                  dockerArgs: "bash -c \'apt-get update && apt-get install -y ffmpeg git git-lfs && if [ ! -d \"/workspace/voice-changer\" ]; then cd /workspace && git clone --depth 1 -b diki https://github.com/dikidag541/voice_changer voice-changer; else cd /workspace/voice-changer && git pull origin diki; fi && cd /workspace/voice-changer/ai-training-runpod && pip install --no-cache-dir -r requirements.txt && python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8888\'"
                }
              ) {
                id
              }
            }
        ';

        $response = Http::withHeaders([
            'Content-Type' => 'application/json',
            'Authorization' => $apiKey,
        ])->post("https://api.runpod.io/graphql?api_key=$apiKey", [
            'query' => $query
        ]);

        $data = $response->json();

        if (isset($data['data']['podFindAndDeployOnDemand'])) {
            return $data['data']['podFindAndDeployOnDemand'];
        }

        return ['error' => 'Gagal membuat pod via GraphQL', 'details' => $data];
    }

    /**
     * Delete/Terminate Pod (Sangat Penting untuk Stop Tagihan Volume 100GB)
     */
    public function deletePod($podId)
    {
        return Http::withHeaders([
            'Authorization' => "Bearer " . env('RUNPOD_API_KEY')
        ])->delete("https://rest.runpod.io/v1/pods/$podId");
    }

    /**
     * Stop a Pod (Hanya mematikan GPU, disk tetap ditagih)
     */
    public function stopPod($podId)
    {
        return Http::withHeaders([
            'Authorization' => "Bearer " . env('RUNPOD_API_KEY')
        ])->post("https://rest.runpod.io/v1/pods/$podId/stop");
    }

    /**
     * Get real-time status from the pod's API
     */
    public function getPodStatus($podId)
    {
        $url = "https://{$podId}-8888.proxy.runpod.net/status";
        $apiKey = env('RUNPOD_API_KEY');

        try {
            $response = Http::withHeaders([
                'Authorization' => "Bearer $apiKey",
            ])->timeout(5)->get($url);

            return $response->json();
        } catch (\Exception $e) {
            return ['status' => 'offline', 'message' => 'Pod unreachable via proxy.'];
        }
    }

    /**
     * List Pods untuk mengecek status
     */
    public function listPods()
    {
        return Http::withHeaders([
            'Authorization' => "Bearer " . env('RUNPOD_API_KEY')
        ])->get("https://rest.runpod.io/v1/pods")->json();
    }

    /**
     * Cek Saldo RunPod (Menggunakan GraphQL API)
     */
    public function getBalance()
    {
        $apiKey = env('RUNPOD_API_KEY');
        // Mencoba beberapa field yang mungkin berisi saldo (RunPod API sering update)
        $query = 'query { myself { balance hostBalance id } }';

        try {
            $response = Http::withHeaders([
                'Content-Type' => 'application/json',
                'Authorization' => $apiKey, // Beberapa versi butuh header ini
            ])->post("https://api.runpod.io/graphql?api_key=$apiKey", [
                'query' => $query
            ]);

            $data = $response->json();

            // Ambil balance utama, jika tidak ada ambil hostBalance
            $balance = 0;
            if (isset($data['data']['myself']['balance'])) {
                $balance = (float) $data['data']['myself']['balance'];
            } elseif (isset($data['data']['myself']['hostBalance'])) {
                $balance = (float) $data['data']['myself']['hostBalance'];
            }

            return ['balance' => $balance, 'raw' => $data];
        } catch (\Exception $e) {
            return ['balance' => 0, 'error' => $e->getMessage()];
        }
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
