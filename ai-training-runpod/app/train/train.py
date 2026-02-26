"""
XTTS v2 Fine-Tuning Script - ROBUST VERSION
===========================================
Dijalankan di RunPod. Fokus pada stabilitas dataset kecil (6 s/d 100 sample).
"""

import os
import sys
import torch
import torch.serialization
from pathlib import Path
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts, XttsAudioConfig, XttsArgs
from TTS.tts.configs.shared_configs import BaseDatasetConfig
from trainer import Trainer, TrainerArgs
from app.core.indo_cleaner import clean_indonesian_for_xtts

# ── Patch torch.load untuk keamanan PyTorch 2.6+ ───────────────────────────
orig_load = torch.load
def patched_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return orig_load(*args, **kwargs)
torch.load = patched_load

if hasattr(torch.serialization, 'add_safe_globals'):
    torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, XttsArgs, BaseDatasetConfig])


def download_base_model():
    from TTS.utils.manage import ModelManager
    model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
    print(f"📦 Downloading base model: {model_name}")
    manager = ModelManager()
    model_path, _, _ = manager.download_model(model_name)
    print(f"✅ Model downloaded to: {model_path}")
    return model_path


def start_training(dataset_path, output_path, epochs=30, batch_size=4):
    os.makedirs(output_path, exist_ok=True)
    
    # 1. CEK DEVICE
    device = "cuda" if torch.cuda.is_available() else "cpu"
    vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3) if device == "cuda" else 0
    print(f"🖥️  Device: {device} | VRAM: {vram:.2f} GB")

    # 2. LOAD CONFIG
    model_dir = download_base_model()
    config_path = os.path.join(model_dir, "config.json")
    config = XttsConfig()
    config.load_json(config_path)

    # 3. CLEAN DATASET & SPLIT
    metadata_file = os.path.join(dataset_path, "metadata.csv")
    print(f"🧹 Cleaning metadata: {metadata_file}")
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    processed_lines = []
    for line in lines:
        parts = line.strip().split("|")
        if len(parts) < 2: continue
        filename = parts[0].replace(".wav", "")
        text = clean_indonesian_for_xtts(parts[1])
        processed_lines.append(f"{filename}|{text}|{text}\n")

    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.writelines(processed_lines)
    
    num_samples = len(processed_lines)
    print(f"✅ Dataset ready: {num_samples} samples.")

    # 4. OPTIMASI CONFIG (Ultra-Tiny Dataset)
    # Pakai 'en' sebagai proxy total untuk kestabilan latin tokenizer
    config.languages = ["en"]
    
    # Force minimal 1 sample untuk eval jika memungkinkan
    eval_split_size = 0.2 if num_samples > 2 else 0
    
    config.epochs = epochs
    config.batch_size = 1 # Force batch 1 untuk stabilitas A4000
    config.grad_acumm_steps = 1
    config.eval_split_size = eval_split_size
    config.mixed_precision = False
    
    if hasattr(config, "model_args"):
        config.model_args.gpt_batch_size = 1
    
    # Defaults
    config.lr = 5e-6
    config.save_step = 1000 # Kita bakal selesai jauh sebelum ini, tapi biar gak spam save
    config.print_step = 1
    config.plot_step = 100
    
    dataset_config = BaseDatasetConfig(
        formatter="ljspeech",
        meta_file_train="metadata.csv",
        path=dataset_path,
        language="en" # Proxy
    )
    config.datasets = [dataset_config]

    # 5. MODEL INIT
    print("🧠 Initializing XTTS v2 Model...")
    model = Xtts.init_from_config(config)
    model.load_checkpoint(config, checkpoint_dir=model_dir, eval=False, use_deepspeed=False)
    model.to(device)

    # 6. TRAINER
    print(f"🚀 Starting training (Proxy Lang: EN)...")
    training_args = TrainerArgs() # Kosongkan total

    try:
        trainer = Trainer(
            training_args,
            config,
            output_path=output_path,
            model=model,
            train_samples=None,
            eval_samples=None
        )
        trainer.fit()
        print("\n✅ TRAINING SELESAI!")
        return True
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    except SystemExit as e:
        print(f"\n⚠️ SystemExit caught: {e}")
        return False


if __name__ == "__main__":
    D = "/workspace/voice-changer/ai-training-runpod"
    start_training(dataset_path=D, output_path=os.path.join(D, "out"), epochs=30)
