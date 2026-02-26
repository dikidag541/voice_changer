<?php
require __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

$apiKey = env('RUNPOD_API_KEY');

function runpod_query($query)
{
    global $apiKey;
    $response = Http::withHeaders([
        'Content-Type' => 'application/json',
    ])->post("https://api.runpod.io/graphql?api_key=$apiKey", [
        'query' => $query
    ]);
    return $response->json();
}

echo "🔍 Checking RunPod Status...\n";

// 1. Check Balance
$balanceRes = runpod_query('{ myself { balance hostBalance } }');
echo "Balance Info: " . json_encode($balanceRes) . "\n\n";

// 2. Check Pods (REST API)
$podsRes = Http::withHeaders(['Authorization' => "Bearer $apiKey"])->get("https://rest.runpod.io/v1/pods")->json();
echo "Pods Info: " . json_encode($podsRes) . "\n\n";

// 3. Check Network Volumes
$volumesRes = runpod_query('{ myself { networkVolumes { id name size dataCenterId } } }');
echo "Volumes Info: " . json_encode($volumesRes) . "\n\n";
