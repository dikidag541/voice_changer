import os
import sys

# Tambahkan path venv agar bisa import datasets jika dijalankan manual
venv_path = os.path.join(os.getcwd(), "python_backend", "venv", "lib", "python3.11", "site-packages")
sys.path.append(venv_path)

from datasets import load_dataset
import soundfile as sf

def extract():
    output_dir = os.path.abspath(os.path.join(os.getcwd(), "python_backend", "references_sampel"))
    os.makedirs(output_dir, exist_ok=True)

    print(f"📥 Menghubungkan ke dataset 'agufsamudra/tts-indo' (Streaming mode)...")
    try:
        dataset = load_dataset("agufsamudra/tts-indo", split="train", streaming=True)
        
        print("🎙️ Mencari 5 sampel suara panjang (>= 8 detik) - Scanning 5000 data...")
        count = 0
        limit = 5000 
        for i, example in enumerate(dataset):
            if i > limit:
                break
                
            audio_data = example['audio']['array']
            sampling_rate = example['audio']['sampling_rate']
            duration = len(audio_data) / sampling_rate
            
            # Kita butuh minimal 8 detik agar XTTS bisa meniru dengan MIRIP
            if duration >= 8.0:
                count += 1
                file_name = f"sampel_panjang_{count}.wav"
                file_path = os.path.join(output_dir, file_name)
                
                sf.write(file_path, audio_data, sampling_rate)
                print(f"✅ [{count}/5] Tersimpan: {file_name} ({duration:.2f} detik)")
                
                if count >= 5:
                    break
                    
        if count == 0:
            print("⚠️ Tidak ditemukan sampel data > 8 detik. Mengambil 10 sampel pertama dan menggabungnya...")
            # Plan B: Gabung 10 sampel pertama (biasanya speaker sama)
            combined = []
            it = iter(dataset)
            for _ in range(12):
                ex = next(it)
                combined.extend(ex['audio']['array'])
            sf.write(os.path.join(output_dir, "sampel_gabungan_pro.wav"), np.array(combined), 16000)
            print(f"✅ Tersimpan: sampel_gabungan_pro.wav")
        else:
            print(f"\n✨ Selesai! Gunakan file 'sampel_panjang_X.wav' agar suara lebih MIRIP.")
            print(f"⚠️ Jika suara di dalam file ini adalah orang yang sama, hasil cloning akan sangat MIRIP.")
        
    except Exception as e:
        print(f"❌ Error saat mengambil dataset: {e}")

if __name__ == "__main__":
    extract()
