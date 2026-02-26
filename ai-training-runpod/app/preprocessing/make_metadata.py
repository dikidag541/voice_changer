import os
import sys
import whisper
import warnings
warnings.filterwarnings("ignore")


def transcribe_with_whisper(wavs_dir="wavs", metadata_path="metadata.csv", whisper_model="medium"):
    """
    Auto transcribe audio files menggunakan OpenAI Whisper.
    Jauh lebih akurat untuk Bahasa Indonesia dibanding Google SR (~95%+ vs 70-80%).
    
    Args:
        wavs_dir      (str): Folder berisi file .wav hasil split
        metadata_path (str): Path output file metadata.csv
        whisper_model (str): Model Whisper ('base', 'small', 'medium', 'large', 'large-v3')
                             Gunakan 'large-v3' untuk akurasi maksimal
                             Gunakan 'medium' jika VRAM < 8GB
    """
    if not os.path.exists(wavs_dir):
        print(f"❌ ERROR: Folder '{wavs_dir}' tidak ditemukan!")
        print("\nJalankan dulu: split_audio.py")
        return False

    print("=" * 60)
    print("AUTO TRANSCRIBE DENGAN WHISPER (Bahasa Indonesia)")
    print("=" * 60)
    print(f"Input folder  : {wavs_dir}/")
    print(f"Output file   : {metadata_path}")
    print(f"Whisper Model : {whisper_model}")
    print()
    print("⚠️  CATATAN:")
    print("   - Whisper large-v3 ~akurasi 95%+ untuk Bahasa Indonesia")
    print("   - Tetap review manual setelah selesai!")
    print()

    # Load Whisper model
    print(f"📦 Loading Whisper model '{whisper_model}'...")
    model = whisper.load_model(whisper_model)
    print("✅ Model loaded!\n")

    files = sorted([f for f in os.listdir(wavs_dir) if f.endswith(".wav")])
    if not files:
        print(f"❌ Folder '{wavs_dir}' kosong! Tidak ada file .wav")
        return False

    print(f"📊 Ditemukan {len(files)} file audio")
    print("🎤 Mulai transcribe...\n")

    results = []
    success_count = 0
    error_count = 0

    for i, filename in enumerate(files):
        path = os.path.join(wavs_dir, filename)
        print(f"[{i+1}/{len(files)}] {filename}... ", end="", flush=True)

        try:
            result = model.transcribe(
                path,
                language="id",       # Force Indonesian
                task="transcribe",
                fp16=False           # Lebih stabil di berbagai GPU
            )
            text = result["text"].strip()
            # Hapus karakter pipe agar tidak rusak format CSV
            text = text.replace("|", "").replace("\n", " ")

            if text:
                results.append(f"{filename}|{text}")
                success_count += 1
                preview = text[:60] + "..." if len(text) > 60 else text
                print(f"✓ {preview}")
            else:
                results.append(f"{filename}|[KOSONG]")
                error_count += 1
                print("✗ Teks kosong")

        except Exception as e:
            results.append(f"{filename}|[ERROR]")
            error_count += 1
            print(f"✗ Error: {e}")

    # Tulis ke metadata.csv
    with open(metadata_path, "w", encoding="utf-8") as f:
        for line in results:
            f.write(line + "\n")

    print()
    print("=" * 60)
    print(f"✅ SELESAI!")
    print(f"   Total file   : {len(files)}")
    print(f"   Berhasil     : {success_count}")
    print(f"   Error/Kosong : {error_count}")
    print(f"   File output  : {metadata_path}")
    print()
    print("⚠️  LANGKAH SELANJUTNYA:")
    print("   1. Buka metadata.csv")
    print("   2. Review SEMUA transkrip (terutama angka & nama)")
    print("   3. Pastikan 100% akurat sebelum training")
    print("   4. Jalankan: python app/train/train.py")
    print("=" * 60)
    return True


if __name__ == "__main__":
    # Jalankan langsung dengan model default large-v3
    # Ganti ke 'medium' jika VRAM kamu < 8GB
    transcribe_with_whisper(
        wavs_dir="wavs",
        metadata_path="metadata.csv",
        whisper_model="large-v3"
    )
