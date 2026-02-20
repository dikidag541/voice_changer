import modal
import os
import io

# Konfigurasi Container Modal
image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("ffmpeg")
    .pip_install(
        "TTS==0.22.0",
        "torch",
        "torchaudio",
        "librosa",
        "soundfile",
        "boto3",
        "python-dotenv"
    )
)

app = modal.App("voice-clone-saas")
volume = modal.Volume.from_name("xtts-model-cache", create_if_missing=True)

@app.cls(
    gpu="any", 
    image=image, 
    volumes={"/root/models": volume},
    secrets=[modal.Secret.from_name("s3-credentials")] # Anda perlu buat secret ini di Modal dashboard
)
class XTTSGenerator:
    def __enter__(self):
        from TTS.tts.configs.xtts_config import XttsConfig
        from TTS.tts.models.xtts import Xtts
        from TTS.utils.manage import ModelManager

        print("📦 Loading XTTS v2 Base Model...")
        self.device = "cuda"
        
        # Download base model XTTS v2
        model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        ModelManager().download_model(model_name)
        
        # Simpan instance model di memory container
        self.model = Xtts.init_from_config(XttsConfig().load_json(os.path.join(os.path.expanduser("~"), ".local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2/config.json")))
        self.model.load_checkpoint(
            checkpoint_dir=os.path.join(os.path.expanduser("~"), ".local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2/"),
            use_deepspeed=False
        )
        self.model.to(self.device)
        print("✅ Base Model Loaded.")

    @modal.method()
    def generate_voice(self, text, user_model_path=None, speaker_wav_path=None, speed=1.0):
        from services.s3_manager import S3Manager
        import tempfile
        
        # 1. Jika ada model khusus user, download dari S3
        if user_model_path:
            s3 = S3Manager()
            local_model_dir = f"/root/models/{user_model_path.replace('/', '_')}"
            s3.download_model_if_not_exists(user_model_path, local_model_dir)
            
            # Load custom weights ke model existing
            checkpoint_path = os.path.join(local_model_dir, "best_model.pth")
            if os.path.exists(checkpoint_path):
                self.model.load_checkpoint(checkpoint_dir=local_model_dir, use_deepspeed=False)

        # 2. Persiapkan Speaker Reference (Jika path S3 diberikan)
        local_speaker_path = "/root/models/default_speaker.wav" 
        if speaker_wav_path:
            s3 = S3Manager()
            local_speaker_path = f"/tmp/{os.path.basename(speaker_wav_path)}"
            s3.s3.download_file(s3.bucket, speaker_wav_path, local_speaker_path)

        # 3. Inference
        print(f"🎙️ Generating voice for: {text[:50]}...")
        outputs = self.model.synthesize(
            text,
            config=self.model.config,
            speaker_wav=local_speaker_path,
            language="id", # Set default ke Indonesia
            speed=speed
        )
        
        # Return binary audio data
        import io
        import soundfile as sf
        
        byte_io = io.BytesIO()
        sf.write(byte_io, outputs['wav'], 24000, format='WAV')
        byte_io.seek(0)
        
        return byte_io.read()
