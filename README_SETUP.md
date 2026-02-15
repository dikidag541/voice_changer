# VoiceCloner AI (Laravel 11 + Python XTTS v2)

A premium voice changer application that functions like Filmora's voice cloning. Record your voice, type any text, and the AI will synthesizer it using your recorded voice profile.

## Prerequisites

- PHP 8.2+
- Composer
- Node.js & NPM
- Python 3.10+
- CUDA (Optional, but recommended for faster AI synthesis)

## Installation Steps

### 1. Setup Laravel Backend

```bash
composer install
npm install
php artisan key:generate
php artisan migrate
```

### 2. Setup Python AI Engine

Go to the `python_backend` directory and install the required AI models and libraries.

```bash
cd python_backend
pip install -r requirements.txt
```

_Note: The first time you run the Python script, it will download the XTTS v2 model (approx 1.5GB)._

## Running the Application

You need to run three processes simultaneously:

1. **Python AI Server:**
    ```bash
    cd python_backend
    python app.py
    ```
2. **Laravel Development Server:**
    ```bash
    php artisan serve
    ```
3. **Vite Development Server (for Tailwind):**
    ```bash
    npm run dev
    ```

## How to Use

1. **Record**: Click the red microphone button and speak for 5-10 seconds.
2. **Script**: Once recorded, the text input will unlock. Type what you want the voice to say.
3. **Generate**: Click "Generate AI Voice". The synthesis takes a few seconds (depending on your GPU/CPU).
4. **Result**: Play or download the generated WAV file.

## Tech Stack

- **Frontend**: Laravel Blade, Tailwind CSS v4, Web Audio API.
- **Backend**: Laravel 11.
- **AI Engine**: Python Flask, Coqui XTTS v2 (SOTA Voice Cloning).
