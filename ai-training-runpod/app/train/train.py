"""
XTTS v2 Fine-Tuning Script untuk Bahasa Indonesia
===================================================
Dijalankan di RunPod GPU. Menggabungkan struktur bersih dari user
dengan fitur optimasi Bahasa Indonesia dan Auto-Batching.
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

# Allowlist untuk PyTorch serialization safety
if hasattr(torch.serialization, 'add_safe_globals'):
    torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, XttsArgs, BaseDatasetConfig])


def download_base_model():
    """Download base XTTS v2 model menggunakan TTS ModelManager."""
    from TTS.utils.manage import ModelManager
    model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
    print(f"📦 Downloading base model: {model_name}")
    manager = ModelManager()
    model_path, _, _ = manager.download_model(model_name)
    print(f"✅ Model downloaded to: {model_path}")
    return model_path


def start_training(dataset_path, output_path, epochs=30, batch_size=4):
    """
    Fungsi utama fine-tuning XTTS v2 untuk Bahasa Indonesia di RunPod.
    """
    os.makedirs(output_path, exist_ok=True)
    
    # ── 1. CEK GPU & VRAM ───────────────────────────────────────────────────
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🖥️  Device: {device}")
    
    vram = 0
    if device == "cuda":
        vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        print(f"📟 VRAM: {vram:.2f} GB")
    else:
        print("⚠️  WARNING: Training di CPU akan sangat lambat!")

    # ── 2. DOWNLOAD BASE MODEL ──────────────────────────────────────────────
    model_dir = download_base_model()
    config_path = os.path.join(model_dir, "config.json")

    # ── 3. KONFIGURASI XTTS ──────────────────────────────────────────────────
    print(f"\n📦 Loading XTTS v2 config dari: {config_path}")
    config = XttsConfig()
    config.load_json(config_path)

    # ── 4. VALIDASI & BERSIHKAN DATASET ──────────────────────────────────────
    metadata_file = os.path.join(dataset_path, "metadata.csv")
    wavs_path = os.path.join(dataset_path, "wavs")

    if not os.path.exists(metadata_file):
        raise FileNotFoundError(f"❌ metadata.csv tidak ditemukan di {dataset_path}")
    
    print("🧹 Cleaning transcripts with Indonesian Cleaner...")
    with open(metadata_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if not line or "|" not in line:
            continue
        parts = line.split("|")
        # Format LJSpeech: ID|Teks|NormalTeks
        filename = parts[0]
        text = parts[1]
        
        # Hapus .wav jika ada di ID
        if filename.endswith(".wav"):
            filename = os.path.splitext(filename)[0]
            
        cleaned_text = clean_indonesian_for_xtts(text)
        # LJSpeech butuh 1 baris: id|transcription|normalized_transcription
        cleaned_lines.append(f"{filename}|{cleaned_text}|{cleaned_text}\n")

    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    print(f"✅ Dataset cleaned: {len(cleaned_lines)} samples ready.")

    # ── 5. OPTIMASI TRAINING (Auto-Batching) ────────────────────────────────
    # Sesuaikan batch_size otomatis dengan VRAM GPU
    auto_batch = batch_size if vram > 16 else (2 if vram > 8 else 1)
    auto_grad_accum = 1 if vram > 16 else (2 if vram > 8 else 8)

    training_args = TrainerArgs(
        epochs=epochs,
        batch_size=auto_batch,
        grad_accum_steps=auto_grad_accum,
        lr=5e-6,
        save_step=500,
        save_n_checkpoints=2,
        save_best_after=500,
        output_path=output_path,
        print_step=50,
        plot_step=100,
        mixed_precision=False, # Stable on various GPUs
    )

    # Dataset config
    config.languages = ["id"]
    dataset_config = BaseDatasetConfig(
        formatter="ljspeech",
        meta_file_train="metadata.csv",
        path=dataset_path,
        language="id"
    )
    config.datasets = [dataset_config]

    # ── 6. INISIALISASI MODEL ────────────────────────────────────────────────
    print("🧠 Initializing XTTS v2 Model...")
    model = Xtts.init_from_config(config)
    model.load_checkpoint(
        config,
        checkpoint_dir=model_dir,
        eval=False,
        use_deepspeed=False
    )
    model.to(device)

    # ── 7. COMPATIBILITY PATCHES ──────────────────────────────────────────────
    if not hasattr(model, "get_criterion"):
        model.get_criterion = lambda: torch.nn.L1Loss()
    
    if hasattr(model, "tokenizer"):
        if not hasattr(model.tokenizer, "text_to_ids"):
            model.tokenizer.text_to_ids = lambda x: model.tokenizer.encode(x, lang="en")
        if not hasattr(model.tokenizer, "print_logs"):
            model.tokenizer.print_logs = lambda x: None

    # Patch Speaker/Language managers
    for manager_name in ["speaker_manager", "language_manager"]:
        manager = getattr(model, manager_name, None)
        if manager is not None and not hasattr(manager, "save_ids_to_file"):
            manager.save_ids_to_file = lambda x: None

    # ── 8. START TRAINING ────────────────────────────────────────────────────
    print(f"\n🚀 Starting training...")
    print(f"   Epochs: {epochs} | Batch Size: {auto_batch} | Grad Accum: {auto_grad_accum}")
    print(f"   Output Path: {output_path}")
    print("=" * 60)

    trainer = Trainer(
        training_args,
        config,
        output_path=output_path,
        model=model,
        train_samples=None,
        eval_samples=None
    )

    try:
        trainer.fit()
        print("\n✅ TRAINING SELESAI!")
        return True
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Path default di RunPod
    D = "/workspace/voice-changer/ai-training-runpod"
    start_training(
        dataset_path=D,
        output_path=os.path.join(D, "out"),
        epochs=30
    )
