# Quick Fix: Manual Transcription Template

Karena Whisper model corrupt, kamu bisa:

## Option 1: Fix Whisper & Retry (Recommended)

```bash
# Stop current process (Ctrl+C di terminal yang running)

# Clear corrupt cache
rm -rf ~/.cache/whisper/

# Retry with smaller model (faster, lebih stable)
cd python_backend
source venv/bin/activate
python3 dataset_tools/prepare_dataset.py \
  --source ../temp_audio/myvoice.wav \
  --output finetune/datasets/indonesian_voice \
  --split \
  --transcribe \
  --whisper-model small \
  --validate
```

**Pros:** Fully automated
**Cons:** Masih butuh 20-30 menit
**Accuracy:** 85-90%

---

## Option 2: Skip Transcription (Manual Edit)

```bash
# Stop current process

# Generate metadata WITHOUT transcription
cd python_backend
source venv/bin/activate
python3 -c "
import os
from pathlib import Path

wavs_dir = 'finetune/datasets/indonesian_voice/wavs'
metadata_path = 'finetune/datasets/indonesian_voice/metadata.csv'

wav_files = sorted(Path(wavs_dir).glob('*.wav'))

with open(metadata_path, 'w', encoding='utf-8') as f:
    for wav_file in wav_files:
        rel_path = f'wavs/{wav_file.name}'
        # Placeholder text - EDIT THIS LATER
        text = '[EDIT: Tulis apa yang diucapkan di audio ini]'
        f.write(f'{rel_path}|{text}|{text}\n')

print(f'✅ Created metadata.csv with {len(wav_files)} entries')
print(f'⚠️  You need to manually edit the transcriptions')
"
```

**Pros:** Cepat (1 menit)
**Cons:** Kamu harus edit 665 baris manual (LAMA!)
**Not recommended** kecuali kamu punya transcription dari sumber lain

---

## Option 3: Use Smaller Dataset (FASTEST)

Kalau mau cepat, pakai audio yang lebih pendek (5-10 menit):

```bash
# Extract first 10 minutes only
cd python_backend
source venv/bin/activate
python3 -c "
import librosa
import soundfile as sf

y, sr = librosa.load('../temp_audio/myvoice.wav', sr=22050)
duration_samples = 10 * 60 * sr  # 10 minutes
y_short = y[:duration_samples]

sf.write('../temp_audio/myvoice_10min.wav', y_short, sr)
print('✅ Created 10-minute version')
"

# Then prepare with small model
python3 dataset_tools/prepare_dataset.py \
  --source ../temp_audio/myvoice_10min.wav \
  --output finetune/datasets/indonesian_voice_10min \
  --split \
  --transcribe \
  --whisper-model small \
  --validate
```

**Pros:** Selesai dalam 10-15 menit, masih bagus untuk training
**Cons:** Dataset lebih kecil (tapi 10 menit masih cukup!)

---

## My Recommendation

**Pakai Option 3** (10 menit dataset dengan small model):
- ✅ Cepat (15 menit total)
- ✅ Stable (small model jarang error)
- ✅ Cukup untuk hasil bagus
- ✅ Bisa upgrade nanti kalau mau

Mau saya jalankan Option 3?
