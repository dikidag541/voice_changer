"""
Embedding Cache System
Cache speaker embeddings for faster inference
"""

import os
import json
import hashlib
import pickle
from pathlib import Path
import numpy as np


class EmbeddingCache:
    """
    Cache speaker embeddings to avoid recomputation
    """
    
    def __init__(self, cache_dir="cache/embeddings"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / "index.json"
        self.index = self._load_index()
    
    def _load_index(self):
        """Load cache index"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_index(self):
        """Save cache index"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def _get_audio_hash(self, audio_path):
        """Get hash of audio file for cache key"""
        with open(audio_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash
    
    def get(self, audio_path):
        """
        Get cached embedding for audio file
        
        Returns: embedding array or None if not cached
        """
        audio_hash = self._get_audio_hash(audio_path)
        
        if audio_hash in self.index:
            cache_file = self.cache_dir / f"{audio_hash}.pkl"
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
        
        return None
    
    def set(self, audio_path, embedding):
        """
        Cache embedding for audio file
        """
        audio_hash = self._get_audio_hash(audio_path)
        cache_file = self.cache_dir / f"{audio_hash}.pkl"
        
        # Save embedding
        with open(cache_file, 'wb') as f:
            pickle.dump(embedding, f)
        
        # Update index
        self.index[audio_hash] = {
            'audio_path': str(audio_path),
            'cache_file': str(cache_file),
            'shape': list(embedding.shape) if hasattr(embedding, 'shape') else None
        }
        self._save_index()
    
    def clear(self):
        """Clear all cached embeddings"""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        self.index = {}
        self._save_index()
    
    def stats(self):
        """Get cache statistics"""
        num_cached = len(self.index)
        total_size = sum(
            Path(info['cache_file']).stat().st_size 
            for info in self.index.values()
            if Path(info['cache_file']).exists()
        )
        
        return {
            'num_cached': num_cached,
            'total_size_mb': total_size / (1024 * 1024)
        }


if __name__ == '__main__':
    # Test cache
    cache = EmbeddingCache()
    print(f"Cache stats: {cache.stats()}")
