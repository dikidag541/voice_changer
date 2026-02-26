<<<<<<< HEAD
"""
XTTS v2 Fine-Tuning Script untuk Bahasa Indonesia
===================================================
Dijalankan di RunPod GPU (RTX 4090 / RTX 3090).
"""

=======
>>>>>>> teammate/main
import os
import sys
import torch
<<<<<<< HEAD
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from trainer import Trainer, TrainerArgs
from app.core.indo_cleaner import clean_indonesian_for_xtts
=======
import requests
from pathlib import Path
>>>>>>> teammate/main

# ─── Patch torch.load untuk keamanan PyTorch 2.6+ ───────────────────────────
orig_load = torch.load
def patched_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return orig_load(*args, **kwargs)
torch.load = patched_load

<<<<<<< HEAD

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
=======
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts, XttsAudioConfig, XttsArgs
from TTS.tts.configs.shared_configs import BaseDatasetConfig

# Allowlist untuk PyTorch serialization safety
if hasattr(torch.serialization, 'add_safe_globals'):
    torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, XttsArgs, BaseDatasetConfig])

try:
    from trainer import Trainer, TrainerArgs
except ImportError:
    os.system("pip install trainer")
    from trainer import Trainer, TrainerArgs


def run_training(dataset_dir, output_dir, epochs=100, batch_size=2):
    """
    Fine-tuning XTTS v2 — Pendekatan bersih ala kode teman (train_samples=None).
    Trainer handle dataset loading sendiri → menghindari semua collate_fn TypeError.
    """

    # ── 1. DOWNLOAD BASE MODEL (Disimpan permanen agar tidak redownload) ──────
    base_model_dir = "/workspace/base_xtts_v2"
    os.makedirs(base_model_dir, exist_ok=True)

    files_to_download = {
        "config.json":       "https://huggingface.co/coqui/XTTS-v2/raw/main/config.json",
        "model.pth":         "https://huggingface.co/coqui/XTTS-v2/resolve/main/model.pth",
        "vocab.json":        "https://huggingface.co/coqui/XTTS-v2/resolve/main/vocab.json",
        "speakers_xtts.pth": "https://huggingface.co/coqui/XTTS-v2/resolve/main/speakers_xtts.pth",
    }
    for filename, url in files_to_download.items():
        dest = os.path.join(base_model_dir, filename)
        if not os.path.exists(dest):
            print(f"📥 Downloading {filename} to permanent storage...")
            r = requests.get(url, stream=True)
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

    # ── 2. SIAPKAN STRUKTUR DATASET (dataset_dir/wavs/) ───────────────────────
    # LJSpeech formatter mengharapkan: path/wavs/*.wav + metadata.csv di root path
    metadata_path = os.path.join(dataset_dir, "metadata.csv")
    wavs_dir = os.path.join(dataset_dir, "wavs")

    # Pindahkan audio ke subfolder wavs/ jika belum ada
    os.makedirs(wavs_dir, exist_ok=True)
    if os.path.exists(metadata_path):
        # Cek apakah ada .wav di root yang perlu dipindah ke wavs/
        wav_files_in_root = [f for f in os.listdir(dataset_dir) if f.endswith(".wav")]
        if wav_files_in_root:
            print(f"� Memindahkan {len(wav_files_in_root)} file .wav ke subfolder wavs/...")
            for wav_file in wav_files_in_root:
                src = os.path.join(dataset_dir, wav_file)
                dst = os.path.join(wavs_dir, wav_file)
                if not os.path.exists(dst):
                    os.rename(src, dst)

    # ── 2.5 AUTO-FIX METADATA (Hapus .wav di kolom ID jika ada) ──────────────
    if os.path.exists(metadata_path):
        print("🛠️ Checking metadata format...")
        with open(metadata_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        fixed_lines = []
        needs_fix = False
        for line in lines:
            parts = line.strip().split("|")
            if len(parts) >= 1 and parts[0].endswith(".wav"):
                parts[0] = os.path.splitext(parts[0])[0]
                fixed_lines.append("|".join(parts))
                needs_fix = True
            else:
                fixed_lines.append(line.strip())
        if needs_fix:
            print("🔧 Fixing metadata: Removing .wav from audio IDs...")
            with open(metadata_path, "w", encoding="utf-8") as f:
                f.write("\n".join(fixed_lines) + "\n")

    # Log jumlah sample
    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            num_samples = len([l for l in f.readlines() if l.strip()])
        print(f"✅ Dataset siap: {num_samples} file")

    # ── 3. KONFIGURASI XTTS ───────────────────────────────────────────────────
    config_path = os.path.join(base_model_dir, "config.json")
    cfg = XttsConfig()
    cfg.load_json(config_path)

    # Dataset config — path ke PARENT dir, formatter ljspeech cari wavs/ sendiri
    d_cfg = BaseDatasetConfig(
        formatter="ljspeech",
        meta_file_train="metadata.csv",  # relatif terhadap path
        path=dataset_dir,                # parent dir (berisi wavs/ dan metadata.csv)
        language="en",                   # 'id' tidak tersedia di tokenizer XTTS v2
    )
    cfg.datasets = [d_cfg]

    # Parameter training
    cfg.epochs = epochs
    cfg.batch_size = batch_size
    cfg.eval_batch_size = max(1, batch_size // 2)
    cfg.num_loader_workers = 4
    cfg.grad_acumm_steps = 4           # Effective batch = batch_size * 4
    cfg.lr = 5e-6                       # Learning rate konservatif
    cfg.save_step = 1000
    cfg.print_step = 50
    cfg.mixed_precision = False

    # Matikan fitur yang tidak diperlukan (mencegah mapping TypeError)
    cfg.use_d_vector_file = False
    cfg.use_phonemes = False
    cfg.use_language_embedding = False

    # Uji kalimat saat evaluasi
    cfg.test_sentences = [
        "Halo, ini adalah suara buatan saya sendiri yang sedang dilatih.",
        "Semoga hasil training hari ini sangat bagus dan memuaskan.",
        "Teknologi kecerdasan buatan sekarang benar-benar luar biasa.",
    ]

    # Patch model_args untuk kompatibilitas berbagai versi TTS
    if hasattr(cfg, "model_args") and cfg.model_args is not None:
        compat_patch = {
            "use_speaker_embedding":    True,
            "use_d_vector_file":        False,
            "use_gpt_eval":             False,
            "use_language_embedding":   False,
            "use_phonemes":             False,
            "use_conditioning_latents": True,
        }
        for var, val in compat_patch.items():
            if not hasattr(cfg.model_args, var):
                setattr(cfg.model_args, var, val)
                print(f"🔧 Patched model_args.{var} = {val}")

    # ── 4. INISIALISASI MODEL & LOAD CHECKPOINT ───────────────────────────────
    print("🧠 Initializing XTTS v2 Model...")
    model = Xtts.init_from_config(cfg)

    # Gunakan checkpoint_dir (sama dengan pendekatan teman yang berhasil)
    model.load_checkpoint(
        cfg,
        checkpoint_dir=base_model_dir,   # ← checkpoint_dir bukan checkpoint_path
        eval=False,
        strict=False,
    )
    model.to("cuda")

    # ── COMPATIBILITY PATCHES ─────────────────────────────────────────────────
    # Patch: get_criterion — diperlukan Trainer tapi tidak ada di Xtts versi ini
    if not hasattr(model, "get_criterion"):
        print("🔧 Patching model.get_criterion...")
        model.get_criterion = lambda: torch.nn.L1Loss()

    # Patch: tokenizer.text_to_ids — method lama yang tidak ada di VoiceBpeTokenizer baru
    if hasattr(model, "tokenizer"):
        if not hasattr(model.tokenizer, "text_to_ids"):
            print("🔧 Patching tokenizer.text_to_ids (lang=en)...")
            model.tokenizer.text_to_ids = lambda x: model.tokenizer.encode(x, lang="en")
        if not hasattr(model.tokenizer, "print_logs"):
            model.tokenizer.print_logs = lambda x: None

    # Patch: SpeakerManager.save_ids_to_file — method tidak ada di versi ini
    if hasattr(model, "speaker_manager") and model.speaker_manager is not None:
        if not hasattr(model.speaker_manager, "save_ids_to_file"):
            print("🔧 Patching speaker_manager.save_ids_to_file...")
            model.speaker_manager.save_ids_to_file = lambda x: None

    # Patch: LanguageManager.save_ids_to_file — method tidak ada di versi ini
    if hasattr(model, "language_manager") and model.language_manager is not None:
        if not hasattr(model.language_manager, "save_ids_to_file"):
            print("🔧 Patching language_manager.save_ids_to_file...")
            model.language_manager.save_ids_to_file = lambda x: None
    # ── END PATCHES ───────────────────────────────────────────────────────────


    # ── 5. TRAINER — train_samples=None agar Trainer load sendiri ────────────
    print(f"🚀 Memulai proses training {epochs} Epoch...")
    trainer_args = TrainerArgs(
        restore_path=None,
        skip_train_epoch=False,
    )

    trainer = Trainer(
        trainer_args,
        cfg,
        output_path=output_dir,
        model=model,
        train_samples=None,   # ← Trainer handle dataset loading sendiri
        eval_samples=None,    # ← Menghindari collate_fn speaker/language TypeError
    )

    # ── 6. FIT ────────────────────────────────────────────────────────────────
    try:
        trainer.fit()
        print("✅ TRAINING SELESAI!")

        import glob
        run_folders = glob.glob(os.path.join(output_dir, "run-*"))
        if run_folders:
            latest_run = max(run_folders, key=os.path.getmtime)
            best_model = os.path.join(latest_run, "best_model.pth")
            if os.path.exists(best_model):
                return best_model

    except BaseException as e:
        print(f"❌ ERROR SAAT FIT (FATAL): {str(e)}")
        import traceback
        traceback.print_exc()
        raise e

    return os.path.join(output_dir, "best_model.pth")


if __name__ == "__main__":
    D = "/workspace/voice-changer/ai-training-runpod"
    run_training(D, os.path.join(D, "out"))
>>>>>>> teammate/main
