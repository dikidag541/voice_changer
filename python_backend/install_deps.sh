#!/bin/bash

# Quick setup script - Install only essential dependencies
echo "📦 Installing fine-tuning dependencies..."

cd python_backend

# Install in current environment (venv)
source venv/bin/activate

# Install essential packages
pip install openai-whisper noisereduce

echo "✅ Dependencies installed!"
