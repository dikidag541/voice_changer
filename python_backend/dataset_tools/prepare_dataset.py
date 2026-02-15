"""
Dataset Preparation Tool for XTTS Fine-Tuning
Processes audio files and generates metadata for training
"""

import os
import sys
import argparse
import librosa
import soundfile as sf
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json

try:
    import noisereduce as nr
    NOISEREDUCE_AVAILABLE = True
except ImportError:
    NOISEREDUCE_AVAILABLE = False
    print("⚠️  noisereduce not installed. Skipping noise reduction.")

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️  whisper not installed. Manual transcription required.")


def preprocess_audio(input_path, output_path, target_sr=22050):
    """
    Advanced audio preprocessing for optimal XTTS training
    """
    print(f"  📝 Processing: {os.path.basename(input_path)}")
    
    # Load audio
    y, sr = librosa.load(input_path, sr=target_sr, mono=True)
    
    # 1. Noise reduction (if available)
    if NOISEREDUCE_AVAILABLE:
        y = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
    
    # 2. Trim silence
    y, _ = librosa.effects.trim(y, top_db=20, frame_length=2048, hop_length=512)
    
    # 3. RMS normalization
    rms = np.sqrt(np.mean(y**2))
    if rms > 0:
        target_rms = 0.1
        y = y * (target_rms / rms)
    
    # 4. Final normalization
    y = librosa.util.normalize(y) * 0.95
    
    # Save
    sf.write(output_path, y, target_sr, format='WAV', subtype='PCM_16')
    
    duration = len(y) / target_sr
    return duration


def split_audio_by_silence(audio_path, output_dir, min_duration=1.0, max_duration=15.0):
    """
    Split long audio into smaller chunks based on silence
    """
    print(f"\n🔪 Splitting audio into chunks...")
    
    y, sr = librosa.load(audio_path, sr=22050, mono=True)
    
    # Detect non-silent intervals
    intervals = librosa.effects.split(y, top_db=25, frame_length=2048, hop_length=512)
    
    chunks = []
    chunk_idx = 0
    
    for start, end in intervals:
        duration = (end - start) / sr
        
        # Skip too short segments
        if duration < min_duration:
            continue
        
        # Split if too long
        if duration > max_duration:
            # Split into smaller pieces
            num_splits = int(np.ceil(duration / max_duration))
            split_length = (end - start) // num_splits
            
            for i in range(num_splits):
                split_start = start + i * split_length
                split_end = min(start + (i + 1) * split_length, end)
                
                chunk = y[split_start:split_end]
                chunk_path = os.path.join(output_dir, f"chunk_{chunk_idx:04d}.wav")
                sf.write(chunk_path, chunk, sr, format='WAV', subtype='PCM_16')
                chunks.append(chunk_path)
                chunk_idx += 1
        else:
            chunk = y[start:end]
            chunk_path = os.path.join(output_dir, f"chunk_{chunk_idx:04d}.wav")
            sf.write(chunk_path, chunk, sr, format='WAV', subtype='PCM_16')
            chunks.append(chunk_path)
            chunk_idx += 1
    
    print(f"  ✅ Created {len(chunks)} chunks")
    return chunks


def transcribe_audio(audio_path, model_size='medium', language='id'):
    """
    Transcribe audio using Whisper
    """
    if not WHISPER_AVAILABLE:
        return None
    
    try:
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path, language=language, fp16=False)
        return result['text'].strip()
    except Exception as e:
        print(f"  ❌ Transcription failed: {e}")
        return None


def generate_metadata(audio_files, transcriptions, output_path):
    """
    Generate metadata.csv for XTTS training
    Format: audio_path|text|text_normalized
    """
    print(f"\n📝 Generating metadata.csv...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for audio_file, text in zip(audio_files, transcriptions):
            if text:
                # Relative path from dataset root
                rel_path = os.path.basename(audio_file)
                # XTTS will auto-normalize, so we use same text for both
                f.write(f"wavs/{rel_path}|{text}|{text}\n")
    
    print(f"  ✅ Metadata saved to {output_path}")


def validate_dataset(dataset_dir):
    """
    Validate dataset quality
    """
    print(f"\n🔍 Validating dataset...")
    
    wavs_dir = os.path.join(dataset_dir, 'wavs')
    metadata_path = os.path.join(dataset_dir, 'metadata.csv')
    
    if not os.path.exists(metadata_path):
        print("  ❌ metadata.csv not found!")
        return False
    
    # Read metadata
    with open(metadata_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total_duration = 0
    issues = []
    
    for i, line in enumerate(lines):
        parts = line.strip().split('|')
        if len(parts) != 3:
            issues.append(f"Line {i+1}: Invalid format")
            continue
        
        audio_path = os.path.join(dataset_dir, parts[0])
        if not os.path.exists(audio_path):
            issues.append(f"Line {i+1}: Audio file not found: {parts[0]}")
            continue
        
        # Check duration
        y, sr = librosa.load(audio_path, sr=None)
        duration = len(y) / sr
        total_duration += duration
        
        if duration < 1.0:
            issues.append(f"Line {i+1}: Audio too short ({duration:.2f}s)")
        elif duration > 15.0:
            issues.append(f"Line {i+1}: Audio too long ({duration:.2f}s)")
    
    print(f"\n📊 Dataset Statistics:")
    print(f"  Total samples: {len(lines)}")
    print(f"  Total duration: {total_duration/60:.2f} minutes")
    print(f"  Average duration: {total_duration/len(lines):.2f} seconds")
    
    if issues:
        print(f"\n⚠️  Found {len(issues)} issues:")
        for issue in issues[:10]:  # Show first 10
            print(f"    - {issue}")
        if len(issues) > 10:
            print(f"    ... and {len(issues)-10} more")
        return False
    else:
        print(f"  ✅ Dataset validation passed!")
        return True


def main():
    parser = argparse.ArgumentParser(description='Prepare dataset for XTTS fine-tuning')
    parser.add_argument('--source', required=True, help='Source audio file (30 min)')
    parser.add_argument('--output', required=True, help='Output dataset directory')
    parser.add_argument('--split', action='store_true', help='Split audio into chunks')
    parser.add_argument('--transcribe', action='store_true', help='Auto-transcribe with Whisper')
    parser.add_argument('--whisper-model', default='medium', help='Whisper model size')
    parser.add_argument('--validate', action='store_true', help='Validate dataset after creation')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = args.output
    wavs_dir = os.path.join(output_dir, 'wavs')
    os.makedirs(wavs_dir, exist_ok=True)
    
    print("🎙️  XTTS Dataset Preparation Tool")
    print("=" * 50)
    
    # Check if source is a file or directory
    if os.path.isfile(args.source):
        # Single file - split it
        print(f"\n📁 Source: {args.source}")
        
        if args.split:
            audio_files = split_audio_by_silence(args.source, wavs_dir)
        else:
            # Just preprocess the whole file
            output_path = os.path.join(wavs_dir, 'audio_000.wav')
            preprocess_audio(args.source, output_path)
            audio_files = [output_path]
    
    else:
        # Directory - process all audio files
        print(f"\n📁 Source directory: {args.source}")
        audio_files = []
        
        for ext in ['*.wav', '*.mp3', '*.m4a', '*.flac']:
            audio_files.extend(Path(args.source).glob(ext))
        
        print(f"  Found {len(audio_files)} audio files")
        
        # Preprocess each file
        processed_files = []
        for i, audio_file in enumerate(tqdm(audio_files, desc="Processing")):
            output_path = os.path.join(wavs_dir, f'audio_{i:04d}.wav')
            preprocess_audio(str(audio_file), output_path)
            processed_files.append(output_path)
        
        audio_files = processed_files
    
    # Transcription
    transcriptions = []
    
    if args.transcribe and WHISPER_AVAILABLE:
        print(f"\n🎤 Transcribing with Whisper ({args.whisper_model})...")
        
        for audio_file in tqdm(audio_files, desc="Transcribing"):
            text = transcribe_audio(audio_file, model_size=args.whisper_model)
            transcriptions.append(text if text else "")
    else:
        print(f"\n⚠️  Transcription skipped. You'll need to manually edit metadata.csv")
        transcriptions = ["[EDIT THIS TEXT]"] * len(audio_files)
    
    # Generate metadata
    metadata_path = os.path.join(output_dir, 'metadata.csv')
    generate_metadata(audio_files, transcriptions, metadata_path)
    
    # Validation
    if args.validate:
        validate_dataset(output_dir)
    
    print(f"\n✨ Dataset preparation complete!")
    print(f"\n📂 Output directory: {output_dir}")
    print(f"   - wavs/ ({len(audio_files)} files)")
    print(f"   - metadata.csv")
    
    if not args.transcribe:
        print(f"\n⚠️  Next step: Edit {metadata_path} to add transcriptions")
    
    print(f"\n🚀 Ready for fine-tuning!")


if __name__ == '__main__':
    main()
