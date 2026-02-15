#!/bin/bash

# Monitor dataset preparation progress
# Run this in a separate terminal to check progress

echo "📊 Dataset Preparation Progress Monitor"
echo "========================================"
echo ""

DATASET_DIR="python_backend/finetune/datasets/indonesian_voice"

while true; do
    clear
    echo "📊 Dataset Preparation Progress Monitor"
    echo "========================================"
    echo ""
    
    # Count processed files
    if [ -d "$DATASET_DIR/wavs" ]; then
        CHUNK_COUNT=$(ls -1 $DATASET_DIR/wavs/*.wav 2>/dev/null | wc -l | tr -d ' ')
        echo "✅ Audio chunks created: $CHUNK_COUNT"
    else
        echo "⏳ Waiting for chunks to be created..."
    fi
    
    # Check metadata
    if [ -f "$DATASET_DIR/metadata.csv" ]; then
        TRANSCRIBED=$(wc -l < $DATASET_DIR/metadata.csv | tr -d ' ')
        echo "📝 Transcriptions completed: $TRANSCRIBED"
        
        if [ "$TRANSCRIBED" -gt 0 ]; then
            PERCENT=$((TRANSCRIBED * 100 / CHUNK_COUNT))
            echo "📈 Progress: $PERCENT%"
        fi
    else
        echo "⏳ Waiting for transcriptions..."
    fi
    
    echo ""
    echo "Press Ctrl+C to stop monitoring"
    
    sleep 5
done
