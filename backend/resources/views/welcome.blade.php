<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}" class="dark">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>VoiceCloner AI — Profesionally Simple</title>

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

    @vite(['resources/css/app.css', 'resources/js/app.js'])

    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #020617;
            /* Slate 950 */
            color: #f1f5f9;
            /* Slate 100 */
        }

        .card-clean {
            background-color: #0f172a;
            /* Slate 900 */
            border: 1px solid #1e293b;
            /* Slate 800 */
            border-radius: 12px;
        }

        .btn-solid {
            background-color: #4f46e5;
            /* Indigo 600 */
            transition: all 0.2s ease;
        }

        .btn-solid:hover:not(:disabled) {
            background-color: #4338ca;
            /* Indigo 700 */
        }

        .btn-outline {
            border: 1px solid #1e293b;
            background: transparent;
            transition: all 0.2s ease;
        }

        .btn-outline:hover {
            background: #1e293b;
        }

        /* Modern Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #020617;
        }

        ::-webkit-scrollbar-thumb {
            background: #1e293b;
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #334155;
        }
    </style>
</head>

<body class="antialiased">
    <div class="max-w-4xl mx-auto px-6 py-12">
        <!-- Brand & Nav -->
        <nav class="flex justify-between items-center mb-16">
            <div class="text-xl font-bold tracking-tight">VOICE<span class="text-indigo-500">CLONER</span></div>
            <div class="flex gap-6 text-sm font-medium text-slate-400">
                <a href="/debug" class="hover:text-white transition-colors">Debug</a>
                <a href="#" class="hover:text-white transition-colors">Documentation</a>
                <a href="#" class="hover:text-white transition-colors">Pricing</a>
            </div>
        </nav>

        <!-- Header -->
        <header class="mb-16">
            <h1 class="text-4xl md:text-5xl font-bold mb-6 tracking-tight text-white">
                Kloning Suara AI<br>Tanpa Batas.
            </h1>
            <p class="text-slate-400 text-lg max-w-xl leading-relaxed">
                Platform SaaS profesional untuk kloning suara Bahasa Indonesia. Rekam sekali, gunakan selamanya dengan teknologi XTTS v2.
            </p>
        </header>

        <main class="space-y-6">
            <!-- Step 1: Voice Setup -->
            <div class="card-clean p-8">
                <div class="flex items-center gap-3 mb-6">
                    <span class="w-8 h-8 rounded-lg bg-indigo-600/10 text-indigo-500 flex items-center justify-center font-bold text-sm">1</span>
                    <h2 class="text-lg font-semibold">Inisialisasi Profil Suara</h2>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Record Action -->
                    <button id="recordBtn" class="btn-outline p-6 rounded-xl flex flex-col items-center gap-3 group">
                        <div id="recordBtnCircle" class="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center group-hover:bg-red-600 transition-colors">
                            <svg id="micIcon" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                            </svg>
                            <div id="stopIcon" class="hidden w-4 h-4 bg-white rounded-sm"></div>
                        </div>
                        <span id="recordStatus" class="text-sm font-medium text-slate-300">Klik untuk Rekam</span>
                    </button>

                    <!-- Upload Action -->
                    <label for="fileUpload" class="btn-outline p-6 rounded-xl flex flex-col items-center gap-3 cursor-pointer group">
                        <div class="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center group-hover:bg-indigo-600 transition-colors">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                        </div>
                        <span id="uploadLabel" class="text-sm font-medium text-slate-300">Unggah File Audio</span>
                        <input type="file" id="fileUpload" class="hidden" accept="audio/*">
                    </label>
                </div>

                <!-- Preview Box -->
                <div id="previewContainer" class="hidden mt-6 p-4 bg-slate-950/50 rounded-lg border border-slate-800">
                    <div class="flex items-center gap-2 mb-3 text-xs font-bold text-indigo-400 uppercase tracking-widest">
                        <div class="w-2 h-2 rounded-full bg-indigo-500"></div>
                        Referensi Suara Terdeteksi
                    </div>
                    <audio id="audioPreview" controls class="w-full h-8 mb-4"></audio>
                    
                    <!-- PREMIUM FINE-TUNING SECTION -->
                    <div id="premiumSection" class="mt-4 p-4 rounded-xl bg-indigo-600/10 border border-indigo-500/20">
                        <div class="flex items-center justify-between mb-2">
                             <h3 class="text-sm font-bold text-white uppercase tracking-wider">Premium Fine-Tuning</h3>
                             <span class="text-[10px] font-bold bg-indigo-500 text-white px-2 py-0.5 rounded-full">Dataset Ready</span>
                        </div>
                        <p class="text-xs text-slate-400 mb-4">Gunakan audio 30 menit untuk hasil suara yang sangat natural.</p>
                        <button id="startTrainingBtn" class="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2">
                            <span>Mulai Latih Suara Premium (Fine-Tuning)</span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Step 2: Configuration -->
            <div id="step2" class="card-clean p-8 opacity-40 grayscale pointer-events-none transition-all duration-300">
                <div class="flex items-center gap-3 mb-6">
                    <span class="w-8 h-8 rounded-lg bg-indigo-600/10 text-indigo-500 flex items-center justify-center font-bold text-sm">2</span>
                    <h2 class="text-lg font-semibold">Teks & Konfigurasi</h2>
                </div>

                <div class="space-y-6">
                    <div>
                        <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Teks yang akan diucapkan</label>
                        <textarea id="textInput"
                            class="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-white placeholder-slate-700 focus:outline-none focus:border-indigo-500 transition-colors resize-none"
                            rows="4"
                            placeholder="Ketik kalimat Bahasa Indonesia di sini..."></textarea>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Kecepatan: <span id="speedValue" class="text-indigo-400">1.1x</span></label>
                            <input type="range" id="speedSelector" min="0.5" max="2.0" step="0.1" value="1.1" class="w-full accent-indigo-600">
                        </div>
                        <div class="flex items-end">
                            <button id="generateBtn" disabled class="btn-solid w-full py-3.5 rounded-xl font-bold flex items-center justify-center gap-2">
                                <span>Generate Voice</span>
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Step 3: Result -->
            <div id="resultSection" class="hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div class="card-clean p-8 border-indigo-500/30 ring-1 ring-indigo-500/20">
                    <div class="flex items-center justify-between mb-8">
                        <div class="flex items-center gap-3">
                            <span class="w-8 h-8 rounded-lg bg-emerald-600/10 text-emerald-500 flex items-center justify-center font-bold text-sm">3</span>
                            <h2 class="text-lg font-semibold">Hasil AI Audio</h2>
                        </div>
                        <span class="text-xs font-bold bg-emerald-500/10 text-emerald-500 px-2 py-1 rounded">READY</span>
                    </div>

                    <div class="space-y-6">
                        <audio id="finalAudio" controls class="w-full"></audio>
                        <a id="downloadBtn" href="#" download class="btn-outline w-full py-3.5 rounded-xl font-bold flex items-center justify-center gap-2">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                            </svg>
                            Unduh File WAV
                        </a>
                        <button onclick="window.location.reload()" class="w-full text-slate-500 hover:text-white text-xs font-medium transition-colors">Mulai Ulang</button>
                    </div>
                </div>
            </div>
        </main>

        <footer class="mt-24 text-center border-t border-slate-900 pt-8">
            <p class="text-slate-60s0 text-xs font-medium tracking-tight">
                &copy; {{ date('Y') }} VOICECLONER.AI — Built for Indonesian Creators.
            </p>
        </footer>
    </div>

    <!-- Script Tetap Sama (Logika Tidak Berubah) -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            let audioContext, processor, input, audioData = [],
                recording = false,
                stream, finalWavBlob, currentSpeakerId = null;

            const elements = {
                recordBtn: document.getElementById('recordBtn'),
                recordBtnCircle: document.getElementById('recordBtnCircle'),
                speedSelector: document.getElementById('speedSelector'),
                speedValue: document.getElementById('speedValue'),
                micIcon: document.getElementById('micIcon'),
                stopIcon: document.getElementById('stopIcon'),
                recordStatus: document.getElementById('recordStatus'),
                previewContainer: document.getElementById('previewContainer'),
                audioPreview: document.getElementById('audioPreview'),
                fileUpload: document.getElementById('fileUpload'),
                uploadLabel: document.getElementById('uploadLabel'),
                step2: document.getElementById('step2'),
                textInput: document.getElementById('textInput'),
                generateBtn: document.getElementById('generateBtn'),
                resultSection: document.getElementById('resultSection'),
                finalAudio: document.getElementById('finalAudio'),
                downloadBtn: document.getElementById('downloadBtn'),
                startTrainingBtn: document.getElementById('startTrainingBtn')
            };

            elements.speedSelector.addEventListener('input', () => elements.speedValue.textContent = elements.speedSelector.value + 'x');

            async function initializeVoiceProfile(blob) {
                elements.recordStatus.textContent = "Processing Profile...";
                const formData = new FormData();
                formData.append('audio', blob, 'ref.wav');

                try {
                    const response = await fetch('/api/initialize-voice', {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                        }
                    });

                    if (response.ok) {
                        const data = await response.json();
                        currentSpeakerId = data.speaker_id;
                        elements.recordStatus.textContent = "Profile Ready";
                        elements.step2.classList.remove('opacity-40', 'grayscale', 'pointer-events-none');
                        elements.generateBtn.disabled = false;
                    }
                } catch (err) {
                    console.error(err);
                    elements.recordStatus.textContent = "Local Mode Active";
                    elements.step2.classList.remove('opacity-40', 'grayscale', 'pointer-events-none');
                    elements.generateBtn.disabled = false;
                }
            }

            elements.recordBtn.addEventListener('click', async () => {
                if (!recording) {
                    stream = await navigator.mediaDevices.getUserMedia({
                        audio: true
                    });
                    audioContext = new(window.AudioContext || window.webkitAudioContext)();
                    input = audioContext.createMediaStreamSource(stream);
                    processor = audioContext.createScriptProcessor(4096, 1, 1);
                    audioData = [];
                    processor.onaudioprocess = (e) => recording && audioData.push(new Float32Array(e.inputBuffer.getChannelData(0)));
                    input.connect(processor);
                    processor.connect(audioContext.destination);
                    recording = true;
                    elements.micIcon.classList.add('hidden');
                    elements.stopIcon.classList.remove('hidden');
                    elements.recordBtnCircle.classList.add('bg-red-600', 'animate-pulse');
                    elements.recordStatus.textContent = "Recording...";
                } else {
                    recording = false;
                    elements.micIcon.classList.remove('hidden');
                    elements.stopIcon.classList.add('hidden');
                    elements.recordBtnCircle.classList.remove('bg-red-600', 'animate-pulse');
                    if (processor) processor.disconnect();
                    if (input) input.disconnect();
                    if (stream) stream.getTracks().forEach(t => t.stop());
                    const buffer = flattenArray(audioData);
                    finalWavBlob = encodeWAV(buffer, audioContext.sampleRate);
                    elements.audioPreview.src = URL.createObjectURL(finalWavBlob);
                    elements.previewContainer.classList.remove('hidden');
                    await initializeVoiceProfile(finalWavBlob);
                }
            });

            elements.fileUpload.addEventListener('change', async (e) => {
                if (e.target.files[0]) {
                    finalWavBlob = e.target.files[0];
                    elements.uploadLabel.textContent = finalWavBlob.name;
                    elements.audioPreview.src = URL.createObjectURL(finalWavBlob);
                    elements.previewContainer.classList.remove('hidden');
                    await initializeVoiceProfile(finalWavBlob);
                }
            });

            elements.startTrainingBtn.addEventListener('click', async () => {
                if (!finalWavBlob) return;

                elements.startTrainingBtn.disabled = true;
                const originalText = elements.startTrainingBtn.innerHTML;
                elements.startTrainingBtn.innerHTML = "Uploading & Starting Training...";

                const formData = new FormData();
                formData.append('audio', finalWavBlob);

                try {
                    const response = await fetch('/api/train', {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                        }
                    });

                    const data = await response.json();
                    if (response.ok) {
                        alert("Berhasil! Training telah dimulai di RunPod. Silakan cek dashboard RunPod Anda.");
                        elements.startTrainingBtn.innerHTML = "Training in Progress...";
                    } else {
                        alert("Error: " + (data.message || "Gagal memulai training"));
                        elements.startTrainingBtn.disabled = false;
                        elements.startTrainingBtn.innerHTML = originalText;
                    }
                } catch (err) {
                    console.error(err);
                    alert("Koneksi gagal");
                    elements.startTrainingBtn.disabled = false;
                    elements.startTrainingBtn.innerHTML = originalText;
                }
            });

            elements.generateBtn.addEventListener('click', async () => {
                const text = elements.textInput.value;
                if (!text) return;

                elements.generateBtn.disabled = true;
                elements.generateBtn.innerHTML = "Generating...";

                const formData = new FormData();
                if (currentSpeakerId) formData.append('speaker_id', currentSpeakerId);
                else formData.append('audio', finalWavBlob, 'ref.wav');
                formData.append('text', text);
                formData.append('speed', elements.speedSelector.value);

                try {
                    const response = await fetch('/api/clone-voice', {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                        }
                    });

                    if (response.ok) {
                        const blob = await response.blob();
                        const url = URL.createObjectURL(blob);
                        elements.finalAudio.src = url;
                        elements.downloadBtn.href = url;
                        elements.resultSection.classList.remove('hidden');
                        elements.resultSection.scrollIntoView({
                            behavior: 'smooth'
                        });
                    }
                } finally {
                    elements.generateBtn.disabled = false;
                    elements.generateBtn.innerHTML = "Generate Voice";
                }
            });

            function flattenArray(c) {
                let r = new Float32Array(c.length * 4096),
                    o = 0;
                for (let i = 0; i < c.length; i++) {
                    r.set(c[i], o);
                    o += c[i].length;
                }
                return r.slice(0, o);
            }

            function encodeWAV(s, sr) {
                const b = new ArrayBuffer(44 + s.length * 2),
                    v = new DataView(b);
                const w = (o, str) => {
                    for (let i = 0; i < str.length; i++) v.setUint8(o + i, str.charCodeAt(i));
                };
                w(0, 'RIFF');
                v.setUint32(4, 32 + s.length * 2, true);
                w(8, 'WAVE');
                w(12, 'fmt ');
                v.setUint32(16, 16, true);
                v.setUint16(20, 1, true);
                v.setUint16(22, 1, true);
                v.setUint32(24, sr, true);
                v.setUint32(28, sr * 2, true);
                v.setUint16(32, 2, true);
                v.setUint16(34, 16, true);
                w(36, 'data');
                v.setUint32(40, s.length * 2, true);
                for (let i = 0, o = 44; i < s.length; i++, o += 2) {
                    let smp = Math.max(-1, Math.min(1, s[i]));
                    v.setInt16(o, smp < 0 ? smp * 0x8000 : smp * 0x7FFF, true);
                }
                return new Blob([v], {
                    type: 'audio/wav'
                });
            }
        });
    </script>
</body>

</html>