import os
import sys
import uuid
import threading
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional

# Menambahkan directory parent dari script ini (ai-training-runpod) ke path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.s3_manager import S3Manager
from services.local_storage_manager import LocalStorageManager
from app.preprocessing.split_audio import split_long_audio
from app.preprocessing.make_metadata import transcribe_with_whisper
from app.train.train import start_training

app = FastAPI(title="Runpod AI Training Worker")

# Inisialisasi Manager (Hybrid)
# Jika API Key tidak ada, dia akan auto-fallback ke LocalStorageManager nanti
s3 = S3Manager()
local_storage = LocalStorageManager()

class TrainingRequest(BaseModel):
    user_id: str
    audio_path: str # Path di R2/S3 atau lokal
    model_name: Optional[str] = "custom_voice"

def run_training_pipeline(request: TrainingRequest):
    """Fungsi utama yang berjalan di background"""
    training_id = str(uuid.uuid4())[:8]
    work_dir = f"./temp_training_{training_id}"
    os.makedirs(work_dir, exist_ok=True)
    
    print(f"🛠️ [PIPELINE] Memulai proses training {training_id} untuk User {request.user_id}")
    
    try:
        # 1. DOWNLOAD DATASET
        # Cek apakah kita pakai mode S3 atau Lokal
        is_s3 = os.getenv("AWS_ACCESS_KEY_ID") is not None
        
        dataset_local_path = os.path.join(work_dir, "dataset.wav")
        
        if is_s3:
            s3.download_dataset("suara-cloning", request.audio_path, dataset_local_path)
        else:
            local_storage.download_dataset(None, request.audio_path, dataset_local_path)

        # 2. PREPROCESSING
        print("🔍 [PIPELINE] Memulai preprocessing...")
        raw_audio_dir = os.path.join(work_dir, "raw_audio")
        wavs_dir = os.path.join(work_dir, "wavs")
        metadata_path = os.path.join(work_dir, "metadata.csv")
        
        os.makedirs(raw_audio_dir, exist_ok=True)
        # Pindahkan dataset.wav ke raw_audio folder agar diproses split_audio.py
        os.rename(dataset_local_path, os.path.join(raw_audio_dir, "dataset.wav"))
        
        # Split Audio
        split_long_audio(input_dir=raw_audio_dir, output_dir=wavs_dir)
        
        # Transcribe
        transcribe_with_whisper(wavs_dir=wavs_dir, metadata_path=metadata_path, whisper_model="large-v3")

        # 3. START TRAINING
        print("🚀 [PIPELINE] Memulai XTTS Trainer...")
        output_model_dir = os.path.join(work_dir, "output")
        success = start_training(
            dataset_path=work_dir, # metadata.csv ada di work_dir, wavs ada di work_dir/wavs
            output_path=output_model_dir,
            epochs=30
        )
        
        if not success:
            raise Exception("Training failed!")

        # 4. UPLOAD HASIL
        # Ambil model terbaik dari folder output
        model_local_path = os.path.join(output_model_dir, "best_model.pth")
        config_local_path = os.path.join(output_model_dir, "config.json")
        
        # Path di R2
        model_remote_path = f"models/{request.user_id}/{request.model_name}.pth"
        config_remote_path = f"models/{request.user_id}/config.json"

        if is_s3:
            s3.upload_model(model_local_path, "suara-cloning", model_remote_path)
            if os.path.exists(config_local_path):
                s3.upload_model(config_local_path, "suara-cloning", config_remote_path)
        else:
            local_storage.upload_model(model_local_path, None, model_remote_path)
            
        print(f"✅ [PIPELINE] Training {training_id} selesai dan di-upload!")

    except Exception as e:
        print(f"❌ [PIPELINE] Error: {str(e)}")

@app.post("/train")
async def trigger_training(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Endpoint yang dipanggil oleh Laravel"""
    background_tasks.add_task(run_training_pipeline, request)
    return {
        "status": "processing",
        "message": f"Training session started for user {request.user_id}",
        "training_id": str(uuid.uuid4())[:8]
    }

@app.get("/health")
async def health():
    return {"status": "ok", "worker": "runpod-training"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
