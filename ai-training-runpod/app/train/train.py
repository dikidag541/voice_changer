"""
XTTS v2 Fine-Tuning Script - ULTRA-ROBUST VERSION
=================================================
Dijalankan di RunPod. Fokus pada deteksi error "Silent Exit" dan validasi data.
"""

import os
import sys
import torch
import torch.serialization
import traceback
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

    # 3. CLEAN DATASET & STRICT VALIDATION
    metadata_file = os.path.join(dataset_path, "metadata.csv")
    wavs_path = os.path.join(dataset_path, "wavs")
    print(f"🧹 Processing metadata: {metadata_file}")
    
    if not os.path.exists(metadata_file):
        print(f"❌ ERROR: metadata.csv tidak ditemukan!")
        return False

    with open(metadata_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    processed_lines = []
    missing_count = 0
    for line in lines:
        parts = line.strip().split("|")
        if len(parts) < 2: continue
        
        filename_id = parts[0].replace(".wav", "")
        # LJSpeech butuh: ID|Transcription|NormalizedTranscription
        text = clean_indonesian_for_xtts(parts[1])
        
        # CEK FISIK FILE (Mencegah SystemExit: 1 di Trainer)
        if os.path.exists(os.path.join(wavs_path, filename_id + ".wav")):
            processed_lines.append(f"{filename_id}|{text}|{text}\n")
        else:
            missing_count += 1

    if missing_count > 0:
        print(f"⚠️  WARNING: {missing_count} file audio tidak ditemukan di folder wavs!")
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.writelines(processed_lines)
    
    num_samples = len(processed_lines)
    print(f"✅ Dataset ready: {num_samples} samples.")
    if num_samples == 0:
        print("❌ ERROR: Tidak ada data valid untuk dilatih!")
        return False

    # 4. OPTIMASI CONFIG (Proxy EN)
    config.languages = ["en"]
    is_tiny = num_samples < 20
    
    if is_tiny:
        auto_batch = 1
        auto_grad_accum = 1
        eval_split = 0.2 if num_samples > 1 else 0
        print(f"⚠️  Mode: ULTRA-SMALL. Batch: 1")
    else:
        auto_batch = batch_size if vram > 16 else (2 if vram > 8 else 1)
        auto_grad_accum = 1 if vram > 16 else 2
        eval_split = 0.1
        print(f"🚀 Mode: STANDARD. Batch: {auto_batch}")

    config.epochs = epochs
    config.batch_size = auto_batch
    config.grad_acumm_steps = auto_grad_accum
    config.eval_split_size = eval_split
    config.mixed_precision = False
    
    # CRITICAL: Matikan Worker Multiprocessing biar error beneran nongol
    config.num_loader_workers = 0
    config.num_eval_loader_workers = 0
    
    if hasattr(config, "model_args"):
        config.model_args.gpt_batch_size = auto_batch
    
    config.lr = 5e-6
    config.save_step = 250 if not is_tiny else 1000
    config.print_step = 10 if not is_tiny else 1
    
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
    print(f"🚀 Starting training (Proxy Lang: EN)...")
    training_args = TrainerArgs(
        dashboard_logger=None,
        project_name="xtts_fine_tuning"
    )

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
        print(f"\n❌ Error during training (Exception): {str(e)}")
        traceback.print_exc()
        return False
    except SystemExit as e:
        print(f"\n⚠️ SystemExit caught (Code {e.code if hasattr(e, 'code') else '1'}):")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    D = "/workspace/voice-changer/ai-training-runpod"
    start_training(dataset_path=D, output_path=os.path.join(D, "out"), epochs=30)
