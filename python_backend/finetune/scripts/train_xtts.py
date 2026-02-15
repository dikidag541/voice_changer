"""
XTTS v2 Fine-Tuning Script
Optimized for Mac M2 (MPS) with Indonesian Dataset
"""

import os
import sys
import torch
import argparse
from pathlib import Path

# Patch torch.load untuk keamanan dan kompatibilitas
orig_load = torch.load
def patched_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return orig_load(*args, **kwargs)
torch.load = patched_load

# Check MPS availability
if torch.backends.mps.is_available():
    device = "mps"
    print("✅ MPS (Metal Performance Shaders) detected!")
elif torch.cuda.is_available():
    device = "cuda"
    print("✅ CUDA GPU detected!")
else:
    device = "cpu"
    print("⚠️  Using CPU (this will be slow)")

print(f"🔧 Device: {device}")

from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from trainer import Trainer, TrainerArgs
from TTS.config.shared_configs import BaseDatasetConfig


def setup_config(dataset_path, output_path, language='id', batch_size=4):
    """
    Setup XTTS training configuration
    Optimized for Mac M2 with limited VRAM
    """
    
    # Dataset config
    dataset_config = BaseDatasetConfig(
        formatter="ljspeech",
        meta_file_train="metadata.csv",
        path=dataset_path,
        language=language,
    )
    
    # Main config
    config = XttsConfig()
    
    # Model settings
    config.model_args.gpt_batch_size = batch_size  # Reduced for M2
    config.model_args.gpt_max_audio_length = 255995  # ~11 seconds
    config.model_args.gpt_max_text_length = 200
    
    # Training settings - Optimized for M2
    config.run_name = "xtts_indonesian_m2"
    config.epochs = 15
    config.batch_size = batch_size  # Small batch for M2
    config.grad_acumm_steps = 8  # Effective batch = 4*8 = 32
    config.save_step = 500
    config.print_step = 50
    config.lr = 5e-6  # Conservative learning rate
    config.num_loader_workers = 2  # Reduced for M2
    config.eval_split_size = 0.1
    
    # Output settings
    config.output_path = output_path
    config.datasets = [dataset_config]
    
    # Mixed precision for M2
    config.mixed_precision = False  # MPS doesn't support mixed precision yet
    
    # Optimizer
    config.optimizer = "AdamW"
    config.optimizer_params = {"betas": [0.9, 0.96], "eps": 1e-8, "weight_decay": 1e-2}
    
    return config


def main():
    parser = argparse.ArgumentParser(description='Fine-tune XTTS v2 for Indonesian')
    parser.add_argument('--dataset', required=True, help='Path to dataset directory')
    parser.add_argument('--output', default='finetune/output/indonesian_xtts', help='Output directory')
    parser.add_argument('--batch-size', type=int, default=4, help='Batch size (reduce if OOM)')
    parser.add_argument('--epochs', type=int, default=15, help='Number of epochs')
    parser.add_argument('--resume', help='Resume from checkpoint')
    parser.add_argument('--test-run', action='store_true', help='Test run (1 epoch)')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🎯 XTTS v2 Fine-Tuning for Indonesian")
    print("="*60)
    
    # Validate dataset
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"❌ Dataset not found: {args.dataset}")
        sys.exit(1)
    
    metadata_path = dataset_path / "metadata.csv"
    if not metadata_path.exists():
        print(f"❌ metadata.csv not found in {args.dataset}")
        sys.exit(1)
    
    wavs_dir = dataset_path / "wavs"
    if not wavs_dir.exists():
        print(f"❌ wavs/ directory not found in {args.dataset}")
        sys.exit(1)
    
    # Count samples
    with open(metadata_path, 'r') as f:
        num_samples = len(f.readlines())
    
    print(f"\n📊 Dataset Info:")
    print(f"   Path: {args.dataset}")
    print(f"   Samples: {num_samples}")
    print(f"   Device: {device}")
    print(f"   Batch size: {args.batch_size}")
    print(f"   Effective batch: {args.batch_size * 8}")
    
    if args.test_run:
        print(f"   ⚠️  TEST RUN MODE (1 epoch only)")
    
    # Setup config
    config = setup_config(
        dataset_path=str(dataset_path),
        output_path=args.output,
        batch_size=args.batch_size
    )
    
    if args.test_run:
        config.epochs = 1
        config.save_step = 50
    else:
        config.epochs = args.epochs
    
    # Initialize model
    print(f"\n🔧 Initializing XTTS model...")
    
    if args.resume:
        print(f"   Resuming from: {args.resume}")
        model = Xtts.init_from_config(config)
        model.load_checkpoint(config, checkpoint_path=args.resume, eval=False, strict=False)
    else:
        print(f"   Loading base XTTS v2 model...")
        # Use TTS API to get the model path (handles cache automatically)
        from TTS.utils.manage import ModelManager
        manager = ModelManager()
        model_path, _, _ = manager.download_model("tts_models/multilingual/multi-dataset/xtts_v2")
        
        print(f"   Model path: {model_path}")
        
        model = Xtts.init_from_config(config)
        # Load from downloaded model path
        model.load_checkpoint(
            config,
            checkpoint_dir=model_path,
            eval=False,
            strict=False
        )
    
    # Move to device
    model = model.to(device)
    
    # Trainer args
    trainer_args = TrainerArgs(
        restore_path=args.resume,
        skip_train_epoch=False,
    )
    
    # Initialize trainer
    print(f"\n🚀 Starting training...")
    print(f"   Output: {args.output}")
    print(f"   TensorBoard: tensorboard --logdir {args.output}")
    print(f"\n" + "="*60)
    
    trainer = Trainer(
        trainer_args,
        config,
        output_path=args.output,
        model=model,
        train_samples=None,
        eval_samples=None,
    )
    
    # Train!
    try:
        trainer.fit()
        print(f"\n✨ Training complete!")
        print(f"   Best model: {args.output}/best_model.pth")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Training interrupted by user")
        print(f"   Last checkpoint: {args.output}/checkpoint_*.pth")
        print(f"   Resume with: --resume {args.output}/checkpoint_*.pth")
    
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
