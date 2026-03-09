import os
from pydub import AudioSegment
from pydub.silence import split_on_silence

def split_long_audio(input_dir="raw_audio", output_dir="wavs"):
    """
    Memotong audio panjang (30 menit) menjadi segmen-segmen pendek
    untuk training XTTS v2.
    """
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("=" * 60)
    print("SPLIT AUDIO UNTUK TRAINING XTTS v2")
    print("=" * 60)
    print(f"Input folder: {input_dir}/")
    print(f"Output folder: {output_dir}/")
    print()
    
    if not os.path.exists(input_dir):
        print(f"❌ ERROR: Folder '{input_dir}' tidak ditemukan!")
        print(f"\nBuat folder dan masukkan file audio 30 menit Anda:")
        print(f"  python_backend/xtts/training/raw_audio/your_audio.wav")
        return

    files = [f for f in os.listdir(input_dir) if f.endswith((".wav", ".mp3", ".m4a"))]
    
    if not files:
        print(f"❌ Folder '{input_dir}' kosong!")
        print("\nMasukkan file audio Anda (WAV/MP3/M4A)")
        return

    total_segments = 0
    
    for filename in files:
        path = os.path.join(input_dir, filename)
        print(f"📂 Processing: {filename}")
        
        # Load audio
        if filename.endswith(".wav"):
            audio = AudioSegment.from_wav(path)
        elif filename.endswith(".mp3"):
            audio = AudioSegment.from_mp3(path)
        elif filename.endswith(".m4a"):
            audio = AudioSegment.from_file(path, "m4a")
        
        duration_sec = len(audio) / 1000
        print(f"   Durasi: {duration_sec:.1f} detik ({duration_sec/60:.1f} menit)")
        
        # Potong berdasarkan silence
        print(f"   Memotong berdasarkan jeda/silence...")
        chunks = split_on_silence(
            audio,
            min_silence_len=400,   # Minimal 0.4 detik sunyi
            silence_thresh=-40,    # Ambang batas suara sunyi (dB)
            keep_silence=250       # Sisakan sedikit jeda
        )
        
        print(f"   Ditemukan {len(chunks)} segmen")
        
        # Export chunks yang durasi 3-12 detik (optimal untuk XTTS)
        segment_count = 0
        for i, chunk in enumerate(chunks):
            chunk_duration = len(chunk) / 1000
            
            # Filter: hanya ambil yang 3-12 detik
            if 3 <= chunk_duration <= 12:
                # Normalize audio (volume konsisten)
                chunk = chunk.normalize()
                
                # Convert to 24000Hz mono (requirement XTTS)
                chunk = chunk.set_frame_rate(24000)
                chunk = chunk.set_channels(1)
                
                # Generate filename
                base_name = os.path.splitext(filename)[0]
                chunk_name = f"{base_name}_seg{segment_count:03d}.wav"
                output_path = os.path.join(output_dir, chunk_name)
                
                # Export
                chunk.export(output_path, format="wav")
                segment_count += 1
                total_segments += 1
                
                print(f"   ✓ {chunk_name} ({chunk_duration:.1f}s)")

        print(f"   Total segmen valid: {segment_count}")
        print()

    print("=" * 60)
    print(f"✅ SELESAI!")
    print(f"   Total segmen: {total_segments} file")
    print(f"   Lokasi: {output_dir}/")
    print()
    print("NEXT STEPS:")
    print("1. Cek file di folder 'wavs/'")
    print("2. Jalankan: python auto_transcribe.py")
    print("   (atau buat metadata.csv manual)")
    print("3. Jalankan training: python train.py")
    print("=" * 60)

if __name__ == "__main__":
    split_long_audio()
