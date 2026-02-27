"""
XTTS v2 Fine-Tuning Script - TRIPLE SHIELD VERSION
==================================================
Dijalankan di RunPod. Fokus pada stabilitas maksimal & diagnosa.
"""

import os
import sys
import torch
import torch.serialization
import traceback
import wave
import shutil
import gc
from pathlib import Path
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts, XttsAudioConfig, XttsArgs
from TTS.tts.configs.shared_configs import BaseDatasetConfig
from trainer import Trainer, TrainerArgs
from TTS.tts.datasets import load_tts_samples
from app.core.indo_cleaner import clean_indonesian_for_xtts

# ── 🚨 MONKEY-PATCH sys.exit 🚨 ──────────────────────────────────────────
orig_exit = sys.exit
def patched_exit(code=None):
    print(f"\n🛑 [PIPELINE] sys.exit({code if code is not None else 0}) dipanggil.")
    message = "".join(traceback.format_stack())
    print(f"--- TRACEBACK BEGIN ---\n{message}\n--- TRACEBACK END ---")
    orig_exit(code)
sys.exit = patched_exit

# ── Force Single GPU ──────────────────────────────────────────────────────
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["USE_ACCELERATE"] = "0"
os.environ["WORLD_SIZE"] = "1"
os.environ["RANK"] = "0"
os.environ["MASTER_ADDR"] = "localhost"
os.environ["MASTER_PORT"] = "12355"

# ── Patch torch.load ──────────────────────────────────────────────────────
orig_load = torch.load
def patched_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return orig_load(*args, **kwargs)
torch.load = patched_load

if hasattr(torch.serialization, 'add_safe_globals'):
    torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, XttsArgs, BaseDatasetConfig])


def is_valid_wav(path):
    try:
        if os.path.basename(path).startswith("._"): return False
        with wave.open(path, 'rb') as f:
            return True
    except:
        return False


def download_base_model():
    from TTS.utils.manage import ModelManager
    model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
    print(f"📦 Downloading base model: {model_name}")
    manager = ModelManager()
    model_path, _, _ = manager.download_model(model_name)
    print(f"✅ Model downloaded to: {model_path}")
    return model_path


def start_training(dataset_path, output_path, epochs=30, batch_size=2):
    os.makedirs(output_path, exist_ok=True)
    
    # 0. CLEAN VRAM
    gc.collect()
    torch.cuda.empty_cache()
    
    # 1. CEK DEVICE
    device = "cuda" if torch.cuda.is_available() else "cpu"
    vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3) if device == "cuda" else 0
    print(f"🖥\ufe0f  Device: {device} | VRAM: {vram:.2f} GB")

    # 2. LOAD CONFIG
    model_dir = download_base_model()
    config_path = os.path.join(model_dir, "config.json")
    config = XttsConfig()
    config.load_json(config_path)

    # 3. CLEAN DATASET (Strict Verification)
    metadata_file = os.path.join(dataset_path, "metadata.csv")
    wavs_path = os.path.join(dataset_path, "wavs")
    print(f"🧹 Validating samples in: {metadata_file}")
    
    if not os.path.exists(metadata_file):
        print(f"❌ ERROR: metadata.csv tidak ditemukan!")
        return False

    with open(metadata_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    processed_lines = []
    skipped_count = 0
    
    for line in lines:
        parts = line.strip().split("|")
        if len(parts) < 2: 
            skipped_count += 1
            continue
        
        raw_name = parts[0].strip()
        # Pastikan kita cari file audio yang benar-benar ada
        filename = raw_name if raw_name.endswith(".wav") else raw_name + ".wav"
        text = clean_indonesian_for_xtts(parts[1]).strip()
        
        if not text or filename.startswith("._"):
            skipped_count += 1
            continue

        wav_full_path = os.path.abspath(os.path.join(wavs_path, filename))
        
        if os.path.exists(wav_full_path) and is_valid_wav(wav_full_path):
            # Penting: LJSpeech mengharapkan: ID|Transcript|Transcript
            # Dan file harus ada di folder 'wavs/ID.wav'
            file_id = filename.replace(".wav", "")
            processed_lines.append(f"{file_id}|{text}|{text}\n")
        else:
            skipped_count += 1

    if skipped_count > 0:
        print(f"⚠️  WARNING: Skip {skipped_count} samples (Junk/Missing/Corrupt).")
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.writelines(processed_lines)
    
    num_samples = len(processed_lines)
    print(f"✅ Final Dataset: {num_samples} valid samples.")
    if num_samples < 5:
        print(f"❌ ERROR: Minimal 5 data valid diperlukan, hanya ada {num_samples}.")
        return False

    # 4. CONFIG SETTINGS (Ultimate Safety)
    config.languages = ["en"]
    # Gunakan integer untuk eval_split_size jika dataset kecil (<1000)
    config.eval_split_size = 8 
    
    config.epochs = epochs
    config.batch_size = batch_size
    config.grad_acumm_steps = 1
    config.mixed_precision = False
    
    config.num_loader_workers = 0
    config.num_eval_loader_workers = 0
    config.test_sentences = []
    config.use_weighted_sampler = False
    
    if hasattr(config, "model_args"):
        config.model_args.gpt_batch_size = batch_size
    
    config.lr = 5e-6
    config.save_step = 500
    config.print_step = 10
    
    dataset_config = BaseDatasetConfig(
        formatter="ljspeech",
        meta_file_train="metadata.csv",
        path=dataset_path,
        language="en"
    )
    config.datasets = [dataset_config]

    # 5. MODEL INIT
    print("🧠 Initializing XTTS v2 Model...")
    model = Xtts.init_from_config(config)
    model.load_checkpoint(config, checkpoint_dir=model_dir, eval=False, use_deepspeed=False)
    model.to(device)

    # 6. COMPATIBILITY PATCHES
    if not hasattr(model, "get_criterion"):
        model.get_criterion = lambda: torch.nn.L1Loss()
    
    if hasattr(model, "tokenizer") and not hasattr(model.tokenizer, "text_to_ids"):
        model.tokenizer.text_to_ids = lambda x: model.tokenizer.encode(x, lang="en")

    # Patch Speaker/Language Manager (Sering hilang di versi 0.22.0 saat training)
    for manager_name in ["speaker_manager", "language_manager"]:
        manager = getattr(model, manager_name, None)
        if manager is not None:
            if not hasattr(manager, "save_ids_to_file"):
                manager.save_ids_to_file = lambda x: None
            if not hasattr(manager, "get_id_by_name"):
                manager.get_id_by_name = lambda x: 0

    # 7. START TRAINER (Constructor-safe version)
    print(f"🚀 [TRIPLE SHIELD ON] Starting Trainer...")
    training_args = TrainerArgs(
        use_ddp=False,
        use_cuda=True,
        use_accelerate=False,
        dashboard_logger=None,  # Matikan logger eksternal (WandB/Tensorboard)
    )

    # 8. LOAD SAMPLES MANUALLY (Red Shield Check)
    print(f"📦 Loading TTS samples from {dataset_path}...")
    train_samples, eval_samples = load_tts_samples(
        dataset_config,
        eval_split=True,
        eval_split_max_size=None,
        eval_split_size=config.eval_split_size,
    )
    print(f"✅ Loaded {len(train_samples)} training and {len(eval_samples)} evaluation samples.")

    try:
        trainer = Trainer(
            training_args,  
            config,
            output_path=output_path,
            model=model,
            train_samples=train_samples,
            eval_samples=eval_samples
        )
        trainer.fit()
        print("\n✅ SUCCESS: Training Completed!")
        return True
    except Exception as e:
        print(f"\n❌ [PIPELINE] FATAL ERROR: {str(e)}")
        traceback.print_exc()
        return False
    except SystemExit as e:
        print(f"\n⚠️ SystemExit caught (Code {e.code if hasattr(e, 'code') else 'Unknown'})")
        return False


if __name__ == "__main__":
    D = "/workspace/voice-changer/ai-training-runpod"
    start_training(dataset_path=D, output_path=os.path.join(D, "out"), epochs=30)
