#!/bin/bash

# Fine-Tuning XTTS v2 for Indonesian on Mac M2
# Using Apple Silicon optimized fork

echo "🚀 Starting XTTS Fine-Tuning for Indonesian..."
echo "Device: Mac M2 (MPS)"
echo "Dataset: 661 samples, 18.03 minutes"
echo ""

# Activate virtual environment
cd /Users/dikiferdianto/Voice-Changer/voice-changer/python_backend
source venv/bin/activate

# Navigate to Apple Silicon fine-tuning directory
cd finetune_apple_silicon

# Training parameters optimized for Mac M2
DATASET_PATH="../finetune/datasets/indonesian_voice"
OUTPUT_PATH="../finetune/output/indonesian_xtts_m2"
NUM_EPOCHS=10
BATCH_SIZE=2  # Conservative for 16GB RAM
GRAD_ACCUM=2  # Effective batch size = 4
MAX_AUDIO_LENGTH=11

echo "📊 Training Configuration:"
echo "   Dataset: $DATASET_PATH"
echo "   Output: $OUTPUT_PATH"
echo "   Epochs: $NUM_EPOCHS"
echo "   Batch Size: $BATCH_SIZE"
echo "   Gradient Accumulation: $GRAD_ACCUM"
echo "   Max Audio Length: ${MAX_AUDIO_LENGTH}s"
echo ""

# Create output directory
mkdir -p "$OUTPUT_PATH"

# Run fine-tuning
echo "🔥 Starting fine-tuning..."
echo "⏰ Estimated time: 6-8 hours"
echo "💡 Training will run overnight. You can monitor progress in terminal."
echo ""

python3 train_standalone.py

echo ""
echo "✅ Fine-tuning complete!"
echo "📂 Model saved to: $OUTPUT_PATH"
echo ""
echo "Next steps:"
echo "1. Test the fine-tuned model"
echo "2. Compare quality with base model"
echo "3. Deploy to production"
