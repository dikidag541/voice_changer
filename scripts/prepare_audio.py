import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
import sys

# Konfigurasi Path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(base_dir, "myvoice.wav")
OUTPUT_DIR = os.path.join(base_dir, "backend", "storage", "app", "public", "dataset_training")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "wavs"), exist_ok=True)

print(f"🎬 Memproses audio: {INPUT_FILE}")

try:
    # Load audio
    audio = AudioSegment.from_file(INPUT_FILE)
    
    # Preprocessing: Convert to Mono and 22050Hz
    audio = audio.set_channels(1).set_frame_rate(22050)
    
    print("✂️ Memotong audio berdasarkan keheningan (silence)...")
    chunks = split_on_silence(
        audio,
        min_silence_len=500, # keheningan minimal 0.5 detik
        silence_thresh=audio.dBFS-14, # threshold volume
        keep_silence=200 # sisakan sedikit ruang
    )
    
    metadata = []
    
    for i, chunk in enumerate(chunks):
        # XTTS prefer potongan 2-10 detik
        if len(chunk) < 1000: # Abaikan potongan di bawah 1 detik
            continue
            
        filename = f"sample_{i:03d}.wav"
        filepath = os.path.join(OUTPUT_DIR, "wavs", filename)
        
        # Ekspor potongan
        chunk.export(filepath, format="wav")
        
        # Tambahkan ke metadata (sementara teks dikosongkan/dummy)
        # Idealnya di sini dipanggil Whisper AI untuk transkripsi
        metadata.append(f"wavs/{filename}|Transkrip suara ke-{i}")
        
        print(f"✅ Tersimpan: {filename} ({len(chunk)/1000:.2f}s)")

    # Simpan file metadata.csv
    with open(os.path.join(OUTPUT_DIR, "metadata.csv"), "w", encoding="utf-8") as f:
        f.write("\n".join(metadata))
        
    print(f"\n✨ Selesai! {len(chunks)} potongan tersimpan di {OUTPUT_DIR}")
    print("🚀 Siap di-upload ke Cloudflare R2 untuk training.")

except Exception as e:
    print(f"❌ Error: {str(e)}")
