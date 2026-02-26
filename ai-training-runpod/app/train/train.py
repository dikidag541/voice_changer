"""
XTTS v2 Fine-Tuning Script - HYPER-SAFETY VERSION
=================================================
Dijalankan di RunPod. Fokus pada stabilitas maksimal (1330 samples).
"""

import os
import sys
import torch
import torch.serialization
import traceback
import wave
from pathlib import Path
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts, XttsAudioConfig, XttsArgs
from TTS.tts.configs.shared_configs import BaseDatasetConfig
from trainer import Trainer, TrainerArgs
from app.core.indo_cleaner import clean_indonesian_for_xtts

# ── Force Single GPU Environment ──────────────────────────────────────────
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

# ── Patch torch.load untuk keamanan PyTorch 2.6+ ───────────────────────────
orig_load = torch.load
def patched_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return orig_load(*args, **kwargs)
torch.load = patched_load

if hasattr(torch.serialization, 'add_safe_globals'):
    torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, XttsArgs, BaseDatasetConfig])


def is_valid_wav(path):
    """Cek apakah file audio adalah WAV valid dan bisa dibaca."""
    try:
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

    # 3. CLEAN DATASET & INTENSIVE VALIDATION
    metadata_file = os.path.join(dataset_path, "metadata.csv")
    wavs_path = os.path.join(dataset_path, "wavs")
    print(f"🧹 Validating 1330 samples in: {metadata_file}")
    
    if not os.path.exists(metadata_file):
        print(f"❌ ERROR: metadata.csv tidak ditemukan!")
        return False

    with open(metadata_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    processed_lines = []
    skipped_count = 0
    for line in lines:
        parts = line.strip().split("|")
        if len(parts) < 2: continue
        
        filename_id = parts[0].replace(".wav", "")
        text = clean_indonesian_for_xtts(parts[1]).strip()
        
        if not text:
            skipped_count += 1
            continue

        wav_full_path = os.path.join(wavs_path, filename_id + ".wav")
        
        # VALIDASI FISIK & HEADER WAV
        if os.path.exists(wav_full_path) and is_valid_wav(wav_full_path):
            processed_lines.append(f"{filename_id}|{text}|{text}\n")
        else:
            skipped_count += 1

    if skipped_count > 0:
        print(f"⚠️  WARNING: Skip {skipped_count} file (tidak ada, teks kosong, atau corrupt).")
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.writelines(processed_lines)
    
    num_samples = len(processed_lines)
    print(f"✅ Dataset ready: {num_samples} samples.")
    if num_samples == 0:
        print("❌ ERROR: Tidak ada data valid untuk dilatih!")
        return False

    # 4. OPTIMASI CONFIG (Hyper-Safety Mode)
    config.languages = ["en"] # Proxy EN tetap
    
    # FORCE EVAL 0: Mencegah error 'ZeroDivisionError' atau crash saat iterasi pertama
    config.eval_split_size = 0.0
    
    config.epochs = epochs
    config.batch_size = 1 # Force 1 untuk stabilitas mutlak
    config.grad_acumm_steps = 1
    config.mixed_precision = False
    
    # MATIKAN SEMUA FITUR YANG BIKIN CRASH
    config.num_loader_workers = 0
    config.num_eval_loader_workers = 0
    config.test_sentences = [] # Jangan generate audio saat startup
    
    if hasattr(config, "model_args"):
        config.model_args.gpt_batch_size = 1
    
    config.lr = 5e-6
    config.save_step = 500
    config.print_step = 1
    
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
    
    if hasattr(model, "tokenizer"):
        if not hasattr(model.tokenizer, "text_to_ids"):
            model.tokenizer.text_to_ids = lambda x: model.tokenizer.encode(x, lang="en")
        if not hasattr(model.tokenizer, "print_logs"):
            model.tokenizer.print_logs = lambda x: None

    for manager_name in ["speaker_manager", "language_manager"]:
        manager = getattr(model, manager_name, None)
        if manager is not None:
            if not hasattr(manager, "save_ids_to_file"):
                manager.save_ids_to_file = lambda x: None
            if not hasattr(manager, "get_id_by_name"):
                manager.get_id_by_name = lambda x: 0

    # 7. START TRAINER
    print(f"🚀 Starting training (Hyper-Safety Active)...")
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
        traceback.print_exc()
        return False
    except SystemExit as e:
        print(f"\n⚠️ SystemExit DETECTED (Code {e.code if hasattr(e, 'code') else 'Unknown'}):")
        traceback.print_exc()
        # Jika SystemExit tapi tanpa traceback, coba debugging manual
        if not traceback.format_exc().strip() or "NoneType" in traceback.format_exc():
            print("   (Si mesin mati tanpa alasan jelas. Biasanya CUDA OOM atau DDP error.)")
        return False


if __name__ == "__main__":
    D = "/workspace/voice-changer/ai-training-runpod"
    start_training(dataset_path=D, output_path=os.path.join(D, "out"), epochs=30)
