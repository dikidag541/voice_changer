"""
Smart Reference Selector
Automatically selects the best audio samples from dataset for voice cloning
"""

import os
import librosa
import numpy as np
from pathlib import Path
import csv


def calculate_audio_quality(audio_path):
    """
    Calculate quality metrics for an audio file
    Returns: quality_score (0-1, higher is better)
    """
    y, sr = librosa.load(audio_path, sr=22050)
    
    # 1. Signal-to-Noise Ratio (SNR) estimation
    rms = np.sqrt(np.mean(y**2))
    
    # 2. Spectral flatness (lower = more tonal, better for voice)
    spectral_flatness = np.mean(librosa.feature.spectral_flatness(y=y))
    
    # 3. Zero crossing rate (voice has moderate ZCR)
    zcr = np.mean(librosa.feature.zero_crossing_rate(y))
    
    # 4. Energy (prefer moderate energy, not too quiet or loud)
    energy = np.mean(librosa.feature.rms(y=y))
    
    # 5. Duration (prefer 2-8 seconds for reference)
    duration = len(y) / sr
    duration_score = 1.0 if 2 <= duration <= 8 else 0.5
    
    # Combine metrics into quality score
    quality_score = (
        (1 - spectral_flatness) * 0.3 +  # Lower flatness = better
        (1 - abs(zcr - 0.1)) * 0.2 +      # Moderate ZCR
        min(rms / 0.2, 1.0) * 0.3 +       # Good RMS level
        duration_score * 0.2
    )
    
    return quality_score


def select_best_references(dataset_dir, num_samples=5, min_duration=2.0, max_duration=10.0):
    """
    Select the best reference audio samples from dataset
    
    Args:
        dataset_dir: Path to dataset directory (contains wavs/ and metadata.csv)
        num_samples: Number of best samples to select
        min_duration: Minimum duration in seconds
        max_duration: Maximum duration in seconds
    
    Returns:
        List of (audio_path, quality_score, text) tuples
    """
    wavs_dir = Path(dataset_dir) / "wavs"
    metadata_path = Path(dataset_dir) / "metadata.csv"
    
    if not wavs_dir.exists():
        raise FileNotFoundError(f"wavs directory not found: {wavs_dir}")
    
    # Read metadata
    metadata = {}
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='|')
            for row in reader:
                if len(row) >= 2:
                    audio_file = row[0].replace('wavs/', '')
                    text = row[1]
                    metadata[audio_file] = text
    
    # Evaluate all audio files
    candidates = []
    
    for audio_file in wavs_dir.glob("*.wav"):
        try:
            # Check duration
            y, sr = librosa.load(audio_file, sr=None)
            duration = len(y) / sr
            
            if duration < min_duration or duration > max_duration:
                continue
            
            # Calculate quality
            quality_score = calculate_audio_quality(str(audio_file))
            
            # Get text
            text = metadata.get(audio_file.name, "")
            
            candidates.append((str(audio_file), quality_score, duration, text))
            
        except Exception as e:
            print(f"Error processing {audio_file}: {e}")
            continue
    
    # Sort by quality score (descending)
    candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N
    best_samples = candidates[:num_samples]
    
    return [(path, score, text) for path, score, dur, text in best_samples]


def create_reference_library(dataset_dir, output_dir, num_samples=10):
    """
    Create a library of best reference samples
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"🔍 Analyzing dataset: {dataset_dir}")
    print(f"   Selecting top {num_samples} references...")
    
    best_samples = select_best_references(dataset_dir, num_samples=num_samples)
    
    print(f"\n✅ Selected {len(best_samples)} best references:")
    
    # Copy best samples to reference library
    import shutil
    
    reference_info = []
    
    for i, (audio_path, quality_score, text) in enumerate(best_samples):
        # Copy to reference library
        dest_path = output_path / f"ref_{i:02d}.wav"
        shutil.copy(audio_path, dest_path)
        
        reference_info.append({
            'file': str(dest_path),
            'quality': quality_score,
            'text': text
        })
        
        print(f"   {i+1}. Quality: {quality_score:.3f} - {Path(audio_path).name}")
        if text:
            print(f"      Text: {text[:50]}...")
    
    # Save reference info
    import json
    with open(output_path / "references.json", 'w', encoding='utf-8') as f:
        json.dump(reference_info, f, indent=2, ensure_ascii=False)
    
    print(f"\n📂 Reference library created: {output_dir}")
    print(f"   - {len(best_samples)} audio files")
    print(f"   - references.json (metadata)")
    
    return reference_info


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Select best reference audio samples')
    parser.add_argument('--dataset', required=True, help='Dataset directory')
    parser.add_argument('--output', default='reference_library', help='Output directory')
    parser.add_argument('--num-samples', type=int, default=10, help='Number of samples to select')
    
    args = parser.parse_args()
    
    create_reference_library(args.dataset, args.output, args.num_samples)
