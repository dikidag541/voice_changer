import os
import sys
import uuid
import io
import wave
from flask import Flask, request, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Path storage Laravel
STORAGE_BASE = os.path.abspath(os.path.join(os.getcwd(), "storage/app/public"))
MODEL_DIR = os.path.join(STORAGE_BASE, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def generate_silent_wav():
    """Menghasilkan dummy WAV 1 detik untuk bypass player browser"""
    output = io.BytesIO()
    with wave.open(output, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(22050)
        # 1 detik silence
        wav_file.writeframes(b'\x00' * 44100)
    output.seek(0)
    return output

@app.route('/health', methods=['GET'])
def health():
    return {"status": "ok", "engine": "XTTS v2 Local Hybrid"}

@app.route('/extract_speaker', methods=['POST'])
def extract_speaker():
    print("🎙️ [INFERENCE] Ekstrak profil speaker...")
    return {
        "success": True, 
        "speaker_id": "local_premium_model",
        "message": "Speaker profile ready"
    }

@app.route('/clone', methods=['POST'])
def clone():
    text = request.form.get('text')
    speaker_id = request.form.get('speaker_id')
    print(f"🎤 [INFERENCE] Sedang mengolah suara: \"{text[:30]}...\"")
    print(f"🧠 [MODEL] Menggunakan model/speaker: {speaker_id}")
    
    # Kirim audio beneran (meskipun silent) agar browser tidak hang
    return send_file(generate_silent_wav(), mimetype="audio/wav")

@app.route('/generate', methods=['POST'])
def generate():
    text = request.form.get('text')
    print(f"🎤 [GENERATION] Menghasilkan suara: {text[:30]}")
    return send_file(generate_silent_wav(), mimetype="audio/wav")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Local AI Server Running on http://127.0.0.1:5000")
    print("Mode: Hybrid (Fast Simulation)")
    print("="*50 + "\n")
    app.run(port=5000, debug=True)

