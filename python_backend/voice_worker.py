import os
import torch
import uuid
import time
import sys
from redis import Redis
import rq
from rq import Worker, Queue
from TTS.api import TTS
from indo_cleaner import clean_indonesian_for_xtts

# --- CONFIGURATION ---
backend_dir = os.path.dirname(os.path.abspath(__file__))
# 1. Fine-tuned model (Premium)
ft_model_dir = os.path.join(backend_dir, "finetune/output/indonesian_xtts_m2_v4/run/training/GPT_XTTS_FT-February-15-2026_12+32PM-1e3657d")
# 2. Base model (Zero-shot) - Standard XTTS v2
base_model_name = "tts_models/multilingual/multi-dataset/xtts_v2"

output_folder = os.path.join(backend_dir, "generated_audio")
os.makedirs(output_folder, exist_ok=True)

# Patch torch.load for compatibility
orig_load = torch.load
def patched_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return orig_load(*args, **kwargs)
torch.load = patched_load

# Determine optimal device
device = "cpu" 
print(f"🚀 [INIT] Sultan Optimization Engine Active on {device}")

# Cache models inside the worker process to avoid reloading every job
tts_ft = None
tts_base = None

def get_tts_engine(model_type="fine-tuned"):
    global tts_ft, tts_base
    try:
        if model_type == "fine-tuned":
            if tts_ft is None:
                print("💎 Loading Fine-tuned Sultan Model (Premium)...")
                tts_ft = TTS(model_path=ft_model_dir, config_path=os.path.join(ft_model_dir, "config.json"), gpu=False).to(device)
            return tts_ft
        else:
            if tts_base is None:
                print("🐣 Loading Base Zero-Shot Model (Original XTTS v2)...")
                tts_base = TTS(base_model_name, gpu=False).to(device)
            return tts_base
    except Exception as e:
        print(f"❌ Error loading {model_type} engine: {str(e)}")
        raise e

def process_voice_job(text, reference_wav_path, job_id, model_type="fine-tuned"):
    """
    Synthesize audio using either the fine-tuned or zero-shot model.
    """
    try:
        output_filename = f"voice_{job_id}.wav"
        output_path = os.path.join(output_folder, output_filename)
        
        print(f"🎙️ [JOB {job_id}] [{model_type}] Synthesizing: {text[:50]}...")
        start_time = time.time()
        
        # Get requested engine
        tts = get_tts_engine(model_type)
        
        # Clean and normalize Indonesian text for KBBI compliance
        cleaned_text = clean_indonesian_for_xtts(text)
        
        # Use 'en' (English) to match your fine-tuning training language.
        # This ensures the model weights are used correctly.
        tts.tts_to_file(
            text=cleaned_text,
            file_path=output_path,
            speaker_wav=reference_wav_path,
            language="en",
            speed=1.0,
            # Similarity & Quality Parameters
            gpt_cond_len=18,       # Maximum focus on voice character
            temperature=0.7,       # Balanced for fine-tuned models
            top_k=50,              # Standard filtering
            top_p=0.85,            # Better diversity for 'en' bridge
            repetition_penalty=2.5 # Prevent stuttering
        )
        
        end_time = time.time()
        print(f"✅ [JOB {job_id}] Success! ({model_type}) Time: {end_time - start_time:.2f}s")
        return {
            "status": "completed", 
            "output_path": output_path, 
            "filename": output_filename, 
            "model_used": model_type,
            "phonetic_bridge": "en",
            "clean_text": cleaned_text
        }
        
    except Exception as e:
        print(f"❌ [JOB {job_id}] Error: {str(e)}")
        return {"status": "failed", "error": str(e)}

if __name__ == '__main__':
    # Initial load of fine-tuned model to keep it warm
    try:
        get_tts_engine("fine-tuned")
    except:
        pass
        
    redis_conn = Redis()
    listen = ['voice_jobs']
    
    print("👷 Worker starting... Monitoring 'voice_jobs' queue.")
    worker = Worker(listen, connection=redis_conn)
    worker.work()
