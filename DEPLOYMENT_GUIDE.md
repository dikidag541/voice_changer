# 🚀 VoiceCloner AI Deployment Guide

Dokumen ini panduan untuk melakukan setup aplikasi di server produksi (Hosting/VPS).

## 1. Persyaratan Server (Minimum)

Aplikasi AI membutuhkan sumber daya lebih besar dari web biasa:

- **OS**: Ubuntu 22.04 LTS (Direkomendasikan)
- **RAM**: Minimal 8GB (Direkomendasikan 16GB)
- **CPU**: 4 Core+
- **GPU (Opsional)**: NVIDIA GPU dengan VRAM 8GB+ (Sangat disarankan untuk kecepatan tinggi)
- **Disk**: 40GB+ (Untuk menyimpan model AI dan file audio)

## 2. Struktur Deployment

Aplikasi ini terdiri dari dua bagian yang harus jalan bersamaan:

1. **Frontend**: Laravel 11 + PHP 8.2+
2. **Backend AI**: Python 3.10+ (Flask API)

## 3. Langkah Instalasi Server

### Bagian A: Laravel (Port 80/443)

1. Clone repository ke server.
2. Jalankan `composer install` dan `npm install && npm run build`.
3. Atur `.env`:
    ```env
    APP_ENV=production
    APP_DEBUG=false
    AI_XTTS_URL=http://127.0.0.1:5000
    AI_GPTSOVITS_URL=http://127.0.0.1:5001
    ```
4. Jalankan migrasi: `php artisan migrate`.

### Bagian B: Backend AI (Python)

1. Install FFmpeg: `sudo apt install ffmpeg`.
2. Masuk ke folder `python_backend`.
3. Buat virtual environment: `python3 -m venv venv`.
4. Aktifkan venv: `source venv/bin/activate`.
5. Install library: `pip install -r requirements.txt`.
6. Download Model: `python download_gptsovits_models.py`.

## 4. Cara Menjalankan di Produksi

Gunakan **PM2** agar server AI otomatis restart jika mati:

```bash
# Jalankan XTTS Engine
pm2 start app.py --name "ai-xtts" --interpreter ./venv/bin/python

# Jalankan GPT-SoVITS Bridge
pm2 start app_gptsovits.py --name "ai-gsv-bridge" --interpreter ./venv/bin/python

# Jalankan GPT-SoVITS Core Engine
pm2 start "python GPT-SoVITS/api_v2.py" --name "ai-gsv-core"
```

## 5. Keamanan & Lisensi

- Pastikan folder `storage` dan `bootstrap/cache` memiliki izin tulis (`chmod -R 775`).
- Jangan ekspos port 5000, 5001, dan 9880 ke publik (Gunakan Firewall). Hanya biarkan Laravel yang mengaksesnya secara internal.
- Ingatlah ketentuan di halaman **Terms of Service** mengenai etika penggunaan AI.
