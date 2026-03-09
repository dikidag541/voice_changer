<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

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
    public function createPod($name = 'voice_changer_gpu')
    {
        $apiKey = env('RUNPOD_API_KEY');
        $gpus = [
            "NVIDIA GeForce RTX 4090",
            "NVIDIA RTX A4000",
            "NVIDIA A5000",
            "NVIDIA RTX 3090",
            "NVIDIA RTX 4000 SFF Ada Generation"
        ];

        foreach ($gpus as $gpu) {
            Log::info("Mencoba menyewa GPU: $gpu...");

            $vars = [
                'gpuTypeId' => $gpu,
                'name' => $name,
                'awsId' => env('AWS_ACCESS_KEY_ID', ''),
                'awsSecret' => env('AWS_SECRET_ACCESS_KEY', ''),
                'awsRegion' => env('AWS_DEFAULT_REGION', 'auto'),
                'awsBucket' => env('AWS_BUCKET', ''),
                'awsEndpoint' => env('AWS_ENDPOINT', ''),
                'awsUrl' => env('AWS_URL', ''),
                'runpodKey' => env('RUNPOD_API_KEY', ''),
                'coquiAgreed' => "1",
                'dockerArgs' => "bash -c 'echo \"[1/3] Syncing Codebase...\" && (if [ ! -d \"/workspace/voice-changer\" ]; then cd /workspace && git clone --depth 1 -b diki https://github.com/dikidag541/voice_changer voice-changer; else cd /workspace/voice-changer && git pull origin diki; fi) && cd /workspace/voice-changer/ai-training-runpod && if [ ! -f \"/workspace/venv/bin/uvicorn\" ]; then echo \"🆕 Setting up Clean Environment...\" && rm -rf /workspace/venv && apt-get update && apt-get install -y ffmpeg espeak-ng build-essential g++ python3-venv && python3 -m venv --system-site-packages /workspace/venv && /workspace/venv/bin/pip install --upgrade pip && /workspace/venv/bin/pip install --no-cache-dir -r requirements.txt && /workspace/venv/bin/pip install --no-cache-dir git+https://github.com/facebookresearch/fairseq.git@main; fi && echo \"[3/3] Starting Server...\" && set -e && /workspace/venv/bin/python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8888'"
            ];

            // json_encode setiap nilai agar aman dimasukkan ke dalam query string GraphQL
            $e = array_map(fn($v) => json_encode($v), $vars);

            $query = '
                mutation {
                  podFindAndDeployOnDemand(
                    input: {
                      cloudType: COMMUNITY,
                      gpuCount: 1,
                      gpuTypeId: ' . $e['gpuTypeId'] . ',
                      imageName: "runpod/pytorch:2.2.1-py3.10-cuda12.1.1-devel-ubuntu22.04",
                      containerDiskInGb: 30,
                      volumeInGb: 50,
                      volumeMountPath: "/workspace",
                      ports: "8888/http",
                      name: ' . $e['name'] . ',
                      env: [
                        { key: "AWS_ACCESS_KEY_ID", value: ' . $e['awsId'] . ' },
                        { key: "AWS_SECRET_ACCESS_KEY", value: ' . $e['awsSecret'] . ' },
                        { key: "AWS_DEFAULT_REGION", value: ' . $e['awsRegion'] . ' },
                        { key: "AWS_BUCKET", value: ' . $e['awsBucket'] . ' },
                        { key: "AWS_ENDPOINT", value: ' . $e['awsEndpoint'] . ' },
                        { key: "AWS_URL", value: ' . $e['awsUrl'] . ' },
                        { key: "RUNPOD_API_KEY", value: ' . $e['runpodKey'] . ' },
                        { key: "COQUI_TOS_AGREED", value: ' . $e['coquiAgreed'] . ' }
                      ],
                      dockerArgs: ' . $e['dockerArgs'] . '
                    }
                  ) {
                    id
                  }
                }
            ';

            $response = Http::withHeaders([
                'Content-Type' => 'application/json',
            ])->post("https://api.runpod.io/graphql?api_key=$apiKey", [
                'query' => $query,
            ]);

            $data = $response->json();

            if (isset($data['data']['podFindAndDeployOnDemand']['id'])) {
                Log::info("✅ Berhasil menyewa GPU: $gpu (Pod ID: " . $data['data']['podFindAndDeployOnDemand']['id'] . ")");
                return $data['data']['podFindAndDeployOnDemand'];
            }

            $errorMsg = json_encode($data['errors'] ?? $data);
            if (str_contains($errorMsg, 'SUPPLY_CONSTRAINT')) {
                Log::warning("⚠️ GPU $gpu Out of Stock, mencoba tipe lain...");
                continue;
            }

            // If there's an error but not SUPPLY_CONSTRAINT, return it immediately
            return ['error' => 'Gagal membuat pod via GraphQL', 'details' => $data];
        }

        return ['error' => 'Semua tipe GPU sedang Out of Stock. Silakan coba lagi nanti.'];
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
