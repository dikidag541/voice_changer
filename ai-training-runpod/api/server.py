import os
import sys
import uuid
import shutil
import torch
import io
import requests
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import soundfile as sf
import librosa
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from services.s3_manager import S3Manager
from services.local_storage_manager import LocalStorageManager
from app.preprocessing.split_audio import split_long_audio
from app.preprocessing.make_metadata import transcribe_with_whisper
from app.train.train import start_training
from app.post_process.rvc_infer import RVCInferencer

app = FastAPI(title="Runpod AI Training Worker")

s3 = S3Manager()
local_storage = LocalStorageManager()
rvc = RVCInferencer()

class XTTSInference:
    def __init__(self):
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self, model_dir=None):
        from TTS.tts.configs.xtts_config import XttsConfig
        from TTS.tts.models.xtts import Xtts
        from TTS.utils.manage import ModelManager

        if self.model is not None:
            return

        print("📦 Loading XTTS v2 for Inference...")
        if model_dir is None:
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
            ModelManager().download_model(model_name)
            model_dir = os.path.join(os.path.expanduser("~"), ".local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2/")
        
        config = XttsConfig()
        config.load_json(os.path.join(model_dir, "config.json"))
        self.model = Xtts.init_from_config(config)
        self.model.load_checkpoint(config, checkpoint_dir=model_dir, use_deepspeed=False)
        self.model.to(self.device)
        print("✅ XTTS Inference Ready.")

    def generate(self, text, speaker_wav, language="id", speed=1.0):
        if self.model is None:
            self.load_model()
        
        output = self.model.synthesize(
            text,
            config=self.model.config,
            speaker_wav=speaker_wav,
            language=language,
            speed=speed
        )
        return output['wav']

inference_engine = XTTSInference()

class TrainingRequest(BaseModel):
    user_id: str
    audio_path: str
    model_name: Optional[str] = "custom_voice"
    epochs: Optional[int] = 30

class CloneRequest(BaseModel):
    text: str
    speaker_id: Optional[str] = None
    rvc_model: Optional[str] = None
    speed: Optional[float] = 1.0

# Progress tracking
training_progress = {
    "status": "idle",
    "current_step": "none",
    "progress_percent": 0,
    "current_epoch": 0,
    "total_epochs": 0,
    "message": "Waiting for command..."
}

def terminate_self():
    """Mematikan Pod sendiri via API RunPod"""
    api_key = os.getenv("RUNPOD_API_KEY")
    pod_id = os.getenv("RUNPOD_POD_ID")
    
    if not api_key or not pod_id:
        print("⚠️ [SELF-TERMINATE] Gagal: API_KEY atau POD_ID tidak ditemukan.")
        return

    print(f"🛑 [SELF-TERMINATE] Menghentikan Pod {pod_id}...")
    
    url = f"https://api.runpod.io/graphql?api_key={api_key}"
    query = f"""
    mutation {{
      podTerminate(input: {{ podId: "{pod_id}" }})
    }}
    """
    try:
        requests.post(url, json={'query': query})
    except Exception as e:
        print(f"⚠️ [SELF-TERMINATE] Error: {e}")

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

        # 2. PREPROCESSING (ZIP extraction or Splitting)
        training_progress.update({
            "current_step": "preprocessing",
            "progress_percent": 30,
            "message": "Extracting or splitting audio..."
        })

        if local_raw_file.lower().endswith(".zip"):
            import zipfile
            print(f"📦 [PIPELINE] Extracting ZIP: {local_raw_file}")
            with zipfile.ZipFile(local_raw_file, 'r') as zip_ref:
                zip_ref.extractall(wavs_dir)
            
            # FLATTEN: Pindahkan semua .wav dari subfolder ke root wavs_dir
            print(f"🧹 [PIPELINE] Flattening ZIP structure...")
            for root, dirs, files in os.walk(wavs_dir, topdown=False):
                if root == wavs_dir: continue
                for f in files:
                    if f.lower().endswith(".wav"):
                        shutil.move(os.path.join(root, f), os.path.join(wavs_dir, f))
            print(f"✅ [PIPELINE] Extraction & Flatten complete.")
        else:
            print(f"✂️ [PIPELINE] Splitting long audio: {local_raw_file}")
            split_long_audio(input_dir=raw_audio_dir, output_dir=wavs_dir)

        # 3. TRANSCRIBE dengan Whisper
        training_progress.update({
            "progress_percent": 45,
            "message": "Transcribing audio with Whisper..."
        })
        metadata_path = os.path.join(base_work_dir, "metadata.csv")
        success_meta = transcribe_with_whisper(wavs_dir=wavs_dir, metadata_path=metadata_path, whisper_model="medium")

        if not success_meta or not os.path.exists(metadata_path):
             raise Exception(f"Gagal membuat metadata.csv! Pastikan ZIP berisi file .wav.")

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
        terminate_self()

    except Exception as e:
        training_progress.update({
            "status": "error",
            "message": f"Error: {str(e)}"
        })
        print(f"❌ [PIPELINE] ERROR: {str(e)}")
        # terminate_self()


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


@app.post("/clone")
async def clone_voice(request: CloneRequest):
    """Endpoint untuk Generasi Suara + RVC (Opsi B)"""
    try:
        # 1. Persiapkan Speaker Reference
        local_speaker_path = "/workspace/default_speaker.wav"
        if request.speaker_id and request.speaker_id != "using_cached_speaker":
            # Jika speaker_id adalah path S3
            if "/" in str(request.speaker_id) or str(request.speaker_id).endswith(".wav"):
                local_speaker_path = f"/tmp/{os.path.basename(request.speaker_id)}"
                if not os.path.exists(local_speaker_path):
                    print(f"📥 [CLONE] Downloading speaker: {request.speaker_id}")
                    try:
                        s3.s3.download_file(s3.bucket, request.speaker_id, local_speaker_path)
                    except Exception as e:
                        print(f"⚠️ Gagal download speaker, pake fallback: {e}")
                        local_speaker_path = "/workspace/default_speaker.wav"

        # 2. XTTS Generation
        print(f"🗣\ufe0f [CLONE] Generating XTTS base for: {request.text[:30]}...")
        xtts_wav = inference_engine.generate(
            text=request.text,
            speaker_wav=local_speaker_path,
            language="id",
            speed=request.speed
        )

        final_wav = xtts_wav

        # 3. RVC Post-Processing (Optional)
        if request.rvc_model:
            local_rvc_path = None
            if "/" in str(request.rvc_model):
                local_rvc_path = f"/workspace/models/rvc/{os.path.basename(request.rvc_model)}"
                if not os.path.exists(local_rvc_path):
                    print(f"📥 [RVC] Downloading model: {request.rvc_model}")
                    os.makedirs(os.path.dirname(local_rvc_path), exist_ok=True)
                    try:
                        s3.s3.download_file(s3.bucket, request.rvc_model, local_rvc_path)
                    except Exception as e:
                        print(f"⚠️ Gagal download RVC: {e}")
                        local_rvc_path = None
            else:
                local_rvc_path = f"/workspace/models/rvc/{request.rvc_model}"
                if not os.path.exists(local_rvc_path): local_rvc_path = None

            if local_rvc_path:
                print(f"✨ [RVC] Applying texture from {local_rvc_path}...")
                final_wav = rvc.infer(
                    audio=xtts_wav,
                    model_path=local_rvc_path
                )

        # 4. Return as Streaming Response
        from fastapi.responses import Response
        byte_io = io.BytesIO()
        sf.write(byte_io, final_wav, 24000, format='WAV')
        byte_io.seek(0)
        
        return Response(content=byte_io.read(), media_type="audio/wav")

    except Exception as e:
        print(f"❌ [CLONE] Error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
