"""
XTTS v2 Fine-Tuning Script untuk Bahasa Indonesia
===================================================
Dijalankan di RunPod GPU (RTX 4090 / RTX 3090).
"""

import os
import sys
import torch
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from trainer import Trainer, TrainerArgs
from app.core.indo_cleaner import clean_indonesian_for_xtts
import requests
from pathlib import Path

# ─── Patch torch.load untuk keamanan PyTorch 2.6+ ───────────────────────────
orig_load = torch.load
def patched_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return orig_load(*args, **kwargs)
torch.load = patched_load


def download_base_model():
    """
    Download XTTS v2 base model menggunakan built-in TTS downloader.
    Disimpan di ~/.local/share/tts/ secara otomatis.
    """
    from TTS.utils.manage import ModelManager
    model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
    print(f"📦 Downloading base model: {model_name}")
    manager = ModelManager()
    model_path, config_path, _ = manager.download_model(model_name)
    print(f"✅ Model downloaded to: {model_path}")
    return os.path.dirname(model_path)


def start_training(dataset_path, output_path, epochs=30, batch_size=4):
    """
    Fungsi utama untuk memulai fine-tuning XTTS v2 Bahasa Indonesia.

    Args:
        dataset_path (str): Folder berisi wavs/ dan metadata.csv
        output_path  (str): Folder tujuan menyimpan model hasil training
        epochs       (int): Jumlah epoch training (default: 30)
        batch_size   (int): Batch size (otomatis disesuaikan dengan VRAM)
    """
    wavs_path = os.path.join(dataset_path, "wavs")
    metadata_file = os.path.join(dataset_path, "metadata.csv")

    os.makedirs(output_path, exist_ok=True)

    # ── Cek GPU ──────────────────────────────────────────────────────────────
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🖥️  Device: {device}")
    if device == "cpu":
        print("   ⚠️ WARNING: Training di CPU akan sangat lambat!")
        vram = 0
    else:
        vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        print(f"📟 VRAM: {vram:.2f} GB")

    # ── Download / Temukan Base Model ─────────────────────────────────────────
    model_dir = download_base_model()

    config_path = os.path.join(model_dir, "config.json")
    if not os.path.exists(config_path):
        # Coba cari di path default TTS
        tts_home = os.path.expanduser(
            "~/.local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2"
        )
        config_path = os.path.join(tts_home, "config.json")
        model_dir = tts_home

    print(f"\n📦 Loading XTTS v2 base model dari: {model_dir}")
    config = XttsConfig()
    config.load_json(config_path)

    model = Xtts.init_from_config(config)
    model.load_checkpoint(
        config,
        checkpoint_dir=model_dir,
        eval=False,
        use_deepspeed=False
    )
    print("✅ Base model loaded!")

    # ── Validasi Dataset ──────────────────────────────────────────────────────
    print("\n📊 Preparing Indonesian dataset...")
    if not os.path.exists(metadata_file):
        raise FileNotFoundError(f"File {metadata_file} tidak ditemukan!")
    if not os.path.exists(wavs_path):
        raise FileNotFoundError(f"Folder {wavs_path} tidak ditemukan!")

    with open(metadata_file, 'r', encoding='utf-8') as f:
        num_samples = len(f.readlines())
    print(f"✅ Dataset: {num_samples} samples")

    # ── Bersihkan Transkrip ───────────────────────────────────────────────────
    print("🧹 Cleaning transcripts with Indonesian Cleaner...")
    with open(metadata_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if not line or "|" not in line:
            continue
        filename, text = line.split("|", 1)
        cleaned_text = clean_indonesian_for_xtts(text)
        cleaned_lines.append(f"{filename}|{cleaned_text}\n")

    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    print("✅ Transcripts cleaned.")

    # ── Konfigurasi Training ─────────────────────────────────────────────────
    # Sesuaikan batch_size otomatis dengan VRAM GPU
    auto_batch = batch_size if vram > 16 else (2 if vram > 8 else 1)
    auto_grad_accum = 1 if vram > 16 else (2 if vram > 8 else 4)

    training_args = TrainerArgs(
        epochs=epochs,
        batch_size=auto_batch,
        grad_accum_steps=auto_grad_accum,
        lr=5e-6,
        save_step=100,
        save_n_checkpoints=3,
        save_best_after=100,
        output_path=output_path,
        print_step=10,
        plot_step=100,
        mixed_precision=True,
        use_grad_scaler=True,
    )

    config.languages = ["id"]
    config.dataset_config = {
        "formatter": "ljspeech",
        "meta_file_train": metadata_file,
        "path": dataset_path,
        "language": "id"
    }

    # ── Mulai Training ────────────────────────────────────────────────────────
    print(f"\n🚀 Starting fine-tuning...")
    print(f"   Epochs     : {epochs}")
    print(f"   Batch Size : {auto_batch}")
    print(f"   Grad Accum : {auto_grad_accum}")
    print(f"   Device     : {device}")
    print("=" * 50)

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
        print("\n✅ Fine-tuning selesai!")
        return True
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")
        return False


if __name__ == "__main__":
    # Jalankan langsung (di RunPod terminal)
    start_training(
        dataset_path="/workspace/dataset",
        output_path="/workspace/output_model",
        epochs=30
    )

if __name__ == "__main__":
    # Jalankan langsung (di RunPod terminal)
    D = "/workspace/voice-changer/ai-training-runpod"
    start_training(
        dataset_path=D,
        output_path=os.path.join(D, "out"),
        epochs=30
    )
