"""
XTTS v2 Fine-Tuning Script - BLACK BOX DEBUGGER
===============================================
Dijalankan di RunPod. Fokus pada membongkar 'SystemExit' misterius.
"""

import os
import sys
import torch
import torch.serialization
import traceback
import wave
import shutil
from pathlib import Path
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts, XttsAudioConfig, XttsArgs
from TTS.tts.configs.shared_configs import BaseDatasetConfig
from trainer import Trainer, TrainerArgs
from app.core.indo_cleaner import clean_indonesian_for_xtts

# ── 🚨 MONKEY-PATCH sys.exit 🚨 ──────────────────────────────────────────
# Biar tahu siapa yang manggil kill-switch
orig_exit = sys.exit
def patched_exit(code=None):
    print(f"\n🛑 [STOP] sys.exit({code}) DIPANGGIL OLEH:")
    traceback.print_stack()
    orig_exit(code)
sys.exit = patched_exit

# ── Force Single GPU ──────────────────────────────────────────────────────
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
os.environ["WORLD_SIZE"] = "1"
os.environ["RANK"] = "0"
os.environ["MASTER_ADDR"] = "localhost"
os.environ["MASTER_PORT"] = "12355"

# ── Patch torch.load untuk keamanan ───────────────────────────────────────
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
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3) if device == "cuda" else 0
    print(f"🖥️  Device: {device} | VRAM: {vram:.2f} GB")

    model_dir = download_base_model()
    config_path = os.path.join(model_dir, "config.json")
    config = XttsConfig()
    config.load_json(config_path)

    # 3. CLEAN DATASET (Sudah terbukti sukses nge-filter junk Mac)
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
    
    for i, line in enumerate(lines):
        parts = line.strip().split("|")
        if len(parts) < 2: 
            skipped_count += 1
            continue
        
        raw_name = parts[0].strip()
        filename_id = raw_name.replace(".wav", "")
        text = clean_indonesian_for_xtts(parts[1]).strip()
        
        if not text or raw_name.startswith("._"):
            skipped_count += 1
            continue

        # Gunakan path absolut untuk verifikasi
        wav_full_path = os.path.abspath(os.path.join(wavs_path, filename_id + ".wav"))
        exists = os.path.exists(wav_full_path)
        valid = is_valid_wav(wav_full_path) if exists else False

        if exists and valid:
            # XTTS format: filename|text|text
            processed_lines.append(f"{filename_id}.wav|{text}|{text}\n")
        else:
            skipped_count += 1

    if skipped_count > 0:
        print(f"⚠️  WARNING: Skip {skipped_count} samples (Junk/Missing/Corrupt).")
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.writelines(processed_lines)
    
    num_samples = len(processed_lines)
    print(f"✅ Dataset: {num_samples} valid samples.")
    if num_samples == 0:
        print("❌ ERROR: Tidak ada data valid sama sekali!")
        return False

    # 4. CONFIG SETTINGS
    config.languages = ["en"]
    config.eval_split_size = 0.01
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
    config.save_step = 1000
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
    
    if hasattr(model, "tokenizer") and not hasattr(model.tokenizer, "text_to_ids"):
        model.tokenizer.text_to_ids = lambda x: model.tokenizer.encode(x, lang="en")

    # 7. START TRAINER (Simplified for Stability)
    print(f"🚀 [DEBUGGER ON] Starting Trainer...")
    training_args = TrainerArgs(
        run_name="finetune_voice",
        project_name="xtts_finetune",
        dashboard_logger="tensorboard",
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
        print("\n✅ SUCCESS: Training Completed!")
        return True
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        traceback.print_exc()
        return False
    except SystemExit as e:
        # Pengecekan monkey-patch tadi harusnya sudah print trace duluan
        print(f"\n⚠️ SystemExit caught (Code {e.code})")
        return False


if __name__ == "__main__":
    D = "/workspace/voice-changer/ai-training-runpod"
    start_training(dataset_path=D, output_path=os.path.join(D, "out"), epochs=30)
