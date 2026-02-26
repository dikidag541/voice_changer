import os
import sys
import uuid
import shutil
import torch
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

from services.s3_manager import S3Manager
from services.local_storage_manager import LocalStorageManager
from app.preprocessing.split_audio import split_long_audio
from app.preprocessing.make_metadata import transcribe_with_whisper
from app.train.train import start_training

app = FastAPI(title="Runpod AI Training Worker")

s3 = S3Manager()
local_storage = LocalStorageManager()

class TrainingRequest(BaseModel):
    user_id: str
    audio_path: str
    model_name: Optional[str] = "custom_voice"
    epochs: Optional[int] = 30

# Progress tracking
training_progress = {
    "status": "idle",
    "current_step": "none",
    "progress_percent": 0,
    "current_epoch": 0,
    "total_epochs": 0,
    "message": "Waiting for command..."
}

def run_training_pipeline(request: TrainingRequest):
    """Pipeline Training Otomatis"""
    global training_progress
    training_id = str(uuid.uuid4())[:8]

    training_progress.update({
        "status": "running",
        "current_step": "initializing",
        "progress_percent": 5,
        "total_epochs": request.epochs,
        "message": f"Initializing session {training_id}"
    })

    base_work_dir = f"/workspace/temp_training_{training_id}"
    raw_audio_dir = os.path.join(base_work_dir, "raw_audio")
    wavs_dir      = os.path.join(base_work_dir, "wavs")
    output_dir    = os.path.join(base_work_dir, "output")

    os.makedirs(raw_audio_dir, exist_ok=True)
    os.makedirs(wavs_dir,      exist_ok=True)
    os.makedirs(output_dir,    exist_ok=True)

    print(f"🛠️ [PIPELINE] Sesi {training_id} untuk User {request.user_id}")

    try:
        # 1. DOWNLOAD AUDIO DARI R2
        training_progress.update({
            "current_step": "downloading",
            "progress_percent": 15,
            "message": "Downloading audio from Cloud..."
        })

        is_s3 = bool(os.getenv("AWS_ACCESS_KEY_ID"))
        local_raw_file = os.path.join(raw_audio_dir, os.path.basename(request.audio_path))

        if is_s3:
            s3.s3.download_file(s3.bucket, request.audio_path, local_raw_file)
        else:
            shutil.copy(request.audio_path, local_raw_file)

        # 2. SPLIT AUDIO
        training_progress.update({
            "current_step": "preprocessing",
            "progress_percent": 30,
            "message": "Splitting audio into segments..."
        })
        split_long_audio(input_dir=raw_audio_dir, output_dir=wavs_dir)

        # 3. TRANSCRIBE dengan Whisper
        training_progress.update({
            "progress_percent": 45,
            "message": "Transcribing audio with Whisper..."
        })
        metadata_path = os.path.join(base_work_dir, "metadata.csv")
        transcribe_with_whisper(wavs_dir=wavs_dir, metadata_path=metadata_path, whisper_model="large-v3")

        # 4. TRAINING
        training_progress.update({
            "current_step": "training",
            "progress_percent": 50,
            "message": "Starting XTTS v2 Fine-Tuning..."
        })
        success = start_training(
            dataset_path=base_work_dir,
            output_path=output_dir,
            epochs=request.epochs
        )

        if not success:
            raise Exception("Training failed!")

        # 5. UPLOAD HASIL KE R2
        training_progress.update({
            "current_step": "uploading",
            "progress_percent": 90,
            "message": "Uploading model to Cloud..."
        })

        remote_model_dir = f"models/{request.user_id}/{request.model_name}"
        if is_s3:
            s3.upload_model(output_dir, s3.bucket, remote_model_dir)

        training_progress.update({
            "status": "completed",
            "current_step": "done",
            "progress_percent": 100,
            "message": "Training finished successfully!"
        })
        print(f"✅ [PIPELINE] Sesi {training_id} selesai!")

    except Exception as e:
        training_progress.update({
            "status": "error",
            "message": f"Error: {str(e)}"
        })
        print(f"❌ [PIPELINE] ERROR: {str(e)}")


@app.post("/train")
async def trigger_training(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Endpoint dipanggil oleh Laravel"""
    background_tasks.add_task(run_training_pipeline, request)
    return {
        "status": "processing",
        "message": "Training pipeline dimulai di background.",
        "user_id": request.user_id
    }


@app.get("/status")
async def get_status():
    """Monitoring training real-time"""
    return training_progress


@app.get("/health")
async def health():
    return {"status": "online", "gpu": torch.cuda.is_available()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
