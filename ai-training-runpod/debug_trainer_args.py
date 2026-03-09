import os
import sys
import torch
import traceback
from TTS.tts.configs.xtts_config import XttsConfig
from trainer import TrainerArgs, Trainer

# Mock dependencies
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def test_trainer_args():
    print("🧪 Testing TrainerArgs initialization...")
    try:
        args = TrainerArgs(
            restore_path=None,
            project_name="test",
            run_name="test_run",
            output_path="/tmp/test_out",
            use_ddp=False,
            use_accelerate=False,
            dashboard_logger=None,
        )
        print("✅ TrainerArgs initialized successfully!")
        return True
    except TypeError as e:
        print(f"❌ TrainerArgs FAILED: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = test_trainer_args()
    if not success:
        sys.exit(1)
