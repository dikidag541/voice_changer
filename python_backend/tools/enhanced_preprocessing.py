"""
Enhanced Audio Preprocessing Module
Advanced preprocessing for optimal XTTS voice cloning quality
"""

import librosa
import soundfile as sf
import numpy as np
from scipy import signal

try:
    import noisereduce as nr
    NOISEREDUCE_AVAILABLE = True
except ImportError:
    NOISEREDUCE_AVAILABLE = False


class AudioPreprocessor:
    """
    Advanced audio preprocessing for XTTS
    """
    
    def __init__(self, target_sr=22050):
        self.target_sr = target_sr
    
    def preprocess(self, audio_path, output_path=None):
        """
        Apply full preprocessing pipeline
        
        Returns: preprocessed audio array, sample rate
        """
        # Load audio
        y, sr = librosa.load(audio_path, sr=self.target_sr, mono=True)
        
        # Pipeline
        y = self._remove_noise(y, sr)
        y = self._trim_silence(y, sr)
        y = self._normalize_rms(y)
        y = self._apply_compression(y)
        y = self._highpass_filter(y, sr)
        y = self._final_normalize(y)
        
        # Save if output path provided
        if output_path:
            sf.write(output_path, y, sr, format='WAV', subtype='PCM_16')
        
        return y, sr
    
    def _remove_noise(self, y, sr):
        """Noise reduction"""
        if NOISEREDUCE_AVAILABLE:
            try:
                y = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.8, stationary=True)
            except:
                pass  # Skip if fails
        return y
    
    def _trim_silence(self, y, sr):
        """Aggressive silence trimming"""
        y, _ = librosa.effects.trim(
            y, 
            top_db=20,  # More aggressive
            frame_length=2048,
            hop_length=512
        )
        return y
    
    def _normalize_rms(self, y):
        """RMS normalization for consistent volume"""
        rms = np.sqrt(np.mean(y**2))
        if rms > 0:
            target_rms = 0.1
            y = y * (target_rms / rms)
        return y
    
    def _apply_compression(self, y):
        """Gentle compression for consistent dynamics"""
        # Soft knee compression
        threshold = 0.5
        ratio = 3.0
        
        y_compressed = np.where(
            np.abs(y) > threshold,
            np.sign(y) * (threshold + (np.abs(y) - threshold) / ratio),
            y
        )
        return y_compressed
    
    def _highpass_filter(self, y, sr):
        """Remove low-frequency rumble"""
        sos = signal.butter(10, 80, 'hp', fs=sr, output='sos')
        y_filtered = signal.sosfilt(sos, y)
        return y_filtered
    
    def _final_normalize(self, y):
        """Final peak normalization"""
        y = librosa.util.normalize(y) * 0.95
        return y


class ParameterOptimizer:
    """
    Auto-tune XTTS parameters for best quality
    """
    
    # Preset configurations
    PRESETS = {
        'max_similarity': {
            'temperature': 0.35,
            'speed': 0.85,
            'repetition_penalty': 7.0,
            'length_penalty': 1.2,
            'top_k': 30,
            'top_p': 0.7
        },
        'natural': {
            'temperature': 0.65,
            'speed': 1.0,
            'repetition_penalty': 3.0,
            'length_penalty': 1.0,
            'top_k': 50,
            'top_p': 0.85
        },
        'fast': {
            'temperature': 0.75,
            'speed': 1.1,
            'repetition_penalty': 2.0,
            'length_penalty': 0.9,
            'top_k': 40,
            'top_p': 0.9
        },
        'indonesian_optimized': {
            'temperature': 0.45,  # Conservative for accuracy
            'speed': 0.90,  # Slightly slower for clarity
            'repetition_penalty': 5.0,  # Reduce repetition
            'length_penalty': 1.1,  # Encourage complete sentences
            'top_k': 35,
            'top_p': 0.75
        }
    }
    
    @classmethod
    def get_preset(cls, preset_name='indonesian_optimized'):
        """Get parameter preset"""
        return cls.PRESETS.get(preset_name, cls.PRESETS['indonesian_optimized'])
    
    @classmethod
    def optimize_for_text(cls, text, base_preset='indonesian_optimized'):
        """
        Optimize parameters based on text characteristics
        """
        params = cls.PRESETS[base_preset].copy()
        
        # Adjust based on text length
        text_length = len(text)
        
        if text_length < 50:
            # Short text - more conservative
            params['temperature'] = max(0.3, params['temperature'] - 0.1)
        elif text_length > 200:
            # Long text - slightly more creative
            params['temperature'] = min(0.7, params['temperature'] + 0.1)
        
        # Adjust speed for very long text
        if text_length > 300:
            params['speed'] = min(1.0, params['speed'] + 0.05)
        
        return params


def get_best_reference(reference_library_path, text_length=None):
    """
    Select best reference audio from library
    
    Args:
        reference_library_path: Path to reference library directory
        text_length: Optional text length to match reference duration
    
    Returns:
        Path to best reference audio
    """
    import json
    from pathlib import Path
    
    ref_path = Path(reference_library_path)
    references_json = ref_path / "references.json"
    
    if not references_json.exists():
        # Fallback: return first .wav file
        wav_files = list(ref_path.glob("*.wav"))
        if wav_files:
            return str(wav_files[0])
        return None
    
    # Load reference metadata
    with open(references_json, 'r') as f:
        references = json.load(f)
    
    if not references:
        return None
    
    # If text_length provided, try to match duration
    if text_length:
        # Estimate desired duration (rough: 10 chars per second)
        target_duration = text_length / 10
        
        # Find reference with closest duration
        best_ref = min(
            references,
            key=lambda r: abs(len(r.get('text', '')) / 10 - target_duration)
        )
    else:
        # Just use highest quality
        best_ref = max(references, key=lambda r: r.get('quality', 0))
    
    return best_ref['file']


if __name__ == '__main__':
    # Test preprocessing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_preprocessing.py <input_audio>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = input_file.replace('.wav', '_enhanced.wav')
    
    print(f"Processing: {input_file}")
    
    preprocessor = AudioPreprocessor()
    y, sr = preprocessor.preprocess(input_file, output_file)
    
    print(f"✅ Enhanced audio saved: {output_file}")
    print(f"   Duration: {len(y)/sr:.2f}s")
    print(f"   RMS: {np.sqrt(np.mean(y**2)):.4f}")
