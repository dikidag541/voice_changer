"""
Standalone XTTS Fine-Tuning Script for Mac M2
Bypasses Gradio UI and runs training directly
"""

import os
import sys
import torch

# CRITICAL FIX: Patch torch.load for PyTorch 2.6+ compatibility
# This allows loading XTTS checkpoints which use custom classes
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    # Force weights_only=False to allow loading custom classes
    kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpt_train import train_gpt

def main():
    print("🚀 Starting XTTS Fine-Tuning for Indonesian...")
    print("Device: Mac M2 (MPS)")
    print("")
    
    # Get absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    
    # Configuration - use absolute paths
    DATASET_PATH = os.path.join(backend_dir, "finetune/datasets/indonesian_voice")
    OUTPUT_PATH = os.path.join(backend_dir, "finetune/output/indonesian_xtts_m2")
    LANGUAGE = "en"  # Use English for Indonesian (best phonetic match)
    NUM_EPOCHS = 10
    BATCH_SIZE = 2
    GRAD_ACCUM = 2
    MAX_AUDIO_LENGTH = 11 * 22050  # 11 seconds in samples
    
    # Metadata paths - absolute paths
    TRAIN_CSV = os.path.join(DATASET_PATH, "metadata.csv")
    EVAL_CSV = os.path.join(DATASET_PATH, "metadata.csv")  # Use same for now
    
    print("📊 Training Configuration:")
    print(f"   Dataset: {DATASET_PATH}")
    print(f"   Output: {OUTPUT_PATH}")
    print(f"   Train CSV: {TRAIN_CSV}")
    print(f"   Language: {LANGUAGE}")
    print(f"   Epochs: {NUM_EPOCHS}")
    print(f"   Batch Size: {BATCH_SIZE}")
    print(f"   Gradient Accumulation: {GRAD_ACCUM}")
    print(f"   Max Audio Length: {MAX_AUDIO_LENGTH / 22050:.1f}s")
    print("")
    
    # Create output directory
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    
    print("🔥 Starting training...")
    print("⏰ Estimated time: 6-8 hours")
    print("💡 Progress will be shown below. You can safely close terminal and training will continue.")
    print("")
    
    try:
        # Run training
        config_path, original_checkpoint, vocab_file, exp_path, speaker_wav = train_gpt(
            language=LANGUAGE,
            num_epochs=NUM_EPOCHS,
            batch_size=BATCH_SIZE,
            grad_acumm=GRAD_ACCUM,
            train_csv=TRAIN_CSV,
            eval_csv=EVAL_CSV,
            output_path=OUTPUT_PATH,
            max_audio_length=MAX_AUDIO_LENGTH
        )
        
        print("")
        print("✅ Fine-tuning complete!")
        print(f"📂 Model saved to: {exp_path}")
        print(f"📄 Config: {config_path}")
        print(f"📄 Vocab: {vocab_file}")
        print(f"🎤 Speaker reference: {speaker_wav}")
        print("")
        print("Next steps:")
        print("1. Test the fine-tuned model")
        print("2. Compare quality with base model")
        print("3. Deploy to production")
        
        return 0
        
    except Exception as e:
        print("")
        print(f"❌ Training failed with error:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
