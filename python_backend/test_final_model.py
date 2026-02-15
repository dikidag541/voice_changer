import os
import torch
import time
from TTS.api import TTS

# Configuration
backend_dir = "/Users/dikiferdianto/Voice-Changer/voice-changer/python_backend"
model_dir = os.path.join(backend_dir, "finetune/output/indonesian_xtts_m2_v4/run/training/GPT_XTTS_FT-February-15-2026_12+32PM-1e3657d")
checkpoint_path = os.path.join(model_dir, "best_model_662.pth")
config_path = os.path.join(model_dir, "config.json")
vocab_path = os.path.join(model_dir, "vocab.json") # Use vocab from base if not in folder, but check folder first
output_wav = os.path.join(backend_dir, "test_results/final_indo_test.wav")
reference_speaker = os.path.join(backend_dir, "finetune/datasets/indonesian_voice/wavs/chunk_0006.wav") # Using a 10s sample from dataset

os.makedirs(os.path.dirname(output_wav), exist_ok=True)

print("🚀 Loading Fine-Tuned Indonesian Model...")
device = "cpu" # Forced CPU to avoid MPS 'channels > 65536' error

try:
    # Initialize TTS with the fine-tuned checkpoint
    # gpu=False to avoid CUDA check, then .to(device) for MPS/CPU
    tts = TTS(model_path=model_dir, config_path=config_path, gpu=False).to(device)
    
    test_text = "Halo semuanya, nama saya adalah asisten suara pintar Indonesian. Saya sudah dilatih selama sepuluh epoch dan sekarang suara saya terdengar lebih jernih dan natural."
    
    print(f"🎙️ Generating speech: '{test_text}'")
    start_time = time.time()
    
    tts.tts_to_file(
        text=test_text,
        file_path=output_wav,
        speaker_wav=reference_speaker,
        language="en"
    )
    
    end_time = time.time()
    print(f"✅ Success! Test audio saved to: {output_wav}")
    print(f"⚡ Inference time: {end_time - start_time:.2f} seconds")

except Exception as e:
    print(f"❌ Error during testing: {str(e)}")
