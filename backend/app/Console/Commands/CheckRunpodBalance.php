<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;

class CheckRunpodBalance extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'runpod:balance';
    protected $description = 'Cek sisa saldo di RunPod';

    public function handle(\App\Services\RunpodService $runpod)
    {
        $this->info("💰 Mengecek saldo RunPod...");
        $data = $runpod->getBalance();

        if (isset($data['balance'])) {
            $balance = $data['balance'];
            $this->info("----------------------------");
            $this->info("Sisa Saldo: $" . number_format($balance, 2));
            $this->info("----------------------------");

            if ($balance < 5) {
                $this->error("⚠️ PERINGATAN: Saldo kritis! Segera Top Up agar sistem tidak mati.");
            } else {
                $this->warn("✅ Saldo aman untuk beberapa kali training.");
            }
        } else {
            $this->error("❌ Gagal mengambil data saldo. Periksa API Key di .env");
        }
    }
}
