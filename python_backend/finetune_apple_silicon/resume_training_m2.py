"""
Resume XTTS Fine-Tuning for Mac M2
Starts from Epoch 6 checkpoint (best_model_1986.pth)
"""

import os
import sys
import torch

# CRITICAL FIX: Patch torch.load for PyTorch 2.6+ compatibility
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpt_train import train_gpt

def main():
    print("🚀 Resuming XTTS Fine-Tuning for Indonesian...")
    print("Target: Milestone Epoch 7-10")
    print("Device: Mac M2 (MPS)")
    print("")
    
    # Get absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    
    # Checkpoint to resume from (Epoch 8 Best Model)
    CUSTOM_CHECKPOINT = os.path.join(backend_dir, "finetune/output/indonesian_xtts_m2_v3/run/training/GPT_XTTS_FT-February-15-2026_09+23AM-1e3657d/best_model_331.pth")
    
    if not os.path.exists(CUSTOM_CHECKPOINT):
        print(f"❌ Checkpoint not found: {CUSTOM_CHECKPOINT}")
        return 1
        
    # Configuration - use absolute paths
    DATASET_PATH = os.path.join(backend_dir, "finetune/datasets/indonesian_voice")
    OUTPUT_PATH = os.path.join(backend_dir, "finetune/output/indonesian_xtts_m2_v4")
    LANGUAGE = "en"  
    NUM_EPOCHS = 2 # Remaining epochs: 9, 10
    BATCH_SIZE = 2
    GRAD_ACCUM = 2
    MAX_AUDIO_LENGTH = 11 * 22050
    
    # Metadata paths
    TRAIN_CSV = os.path.join(DATASET_PATH, "metadata.csv")
    EVAL_CSV = os.path.join(DATASET_PATH, "metadata.csv")
    
    print("📊 Recovery Configuration:")
    print(f"   Base Checkpoint: {CUSTOM_CHECKPOINT}")
    print(f"   Output: {OUTPUT_PATH}")
    print(f"   Remaining Epochs: {NUM_EPOCHS}")
    print("")
    
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    
    print("🔥 Starting recovery training...")
    
    try:
        train_gpt(
            language=LANGUAGE,
            num_epochs=NUM_EPOCHS,
            batch_size=BATCH_SIZE,
            grad_acumm=GRAD_ACCUM,
            train_csv=TRAIN_CSV,
            eval_csv=EVAL_CSV,
            output_path=OUTPUT_PATH,
            max_audio_length=MAX_AUDIO_LENGTH,
            custom_checkpoint=CUSTOM_CHECKPOINT
        )
        
        print("")
        print("✅ Recovery training complete!")
        return 0
        
    except Exception as e:
        print("")
        print(f"❌ Recovery failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
