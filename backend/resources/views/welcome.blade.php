<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}" class="dark">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>VoiceCloner AI — Indonesian Premium Voice Cloning</title>

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">

    @vite(['resources/css/app.css', 'resources/js/app.js'])

    <style>
        :root {
            --app-bg: #020617;
            --card-bg: rgba(15, 23, 42, 0.6);
            --accent: #6366f1;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--app-bg);
            background-image:
                radial-gradient(circle at 10% 10%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 90% 90%, rgba(168, 85, 247, 0.05) 0%, transparent 40%);
            color: #f1f5f9;
            min-height: 100vh;
        }

        .glass-card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 28px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }

        .glass-card:hover {
            border-color: rgba(99, 102, 241, 0.15);
            transform: translateY(-4px);
            box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.6);
        }

        .premium-btn {
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            transition: all 0.3s ease;
        }

        .premium-btn:hover:not(:disabled) {
            filter: brightness(1.1);
            box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.4);
        }

        .step-badge {
            width: 32px;
            height: 32px;
            border-radius: 10px;
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            color: #818cf8;
            font-size: 0.75rem;
        }

        /* Modern Scrollbar */
        ::-webkit-scrollbar {
            width: 5px;
        }

        ::-webkit-scrollbar-track {
            background: var(--app-bg);
        }

        ::-webkit-scrollbar-thumb {
            background: #1e293b;
            border-radius: 10px;
        }

        /* TOAST STYLES */
        #toast-container {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 100;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .toast {
            background: rgba(17, 24, 39, 0.9);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 16px;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }

            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    </style>
</head>

<body class="antialiased selection:bg-indigo-500/30">
    <div class="max-w-5xl mx-auto px-6 py-8">
        <!-- Brand -->
        <nav class="flex justify-between items-center mb-16">
            <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-xl premium-btn flex items-center justify-center shadow-lg shadow-indigo-500/20">
                    <svg class="text-white w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                </div>
                <div class="text-2xl font-black tracking-tighter bg-clip-text text-transparent bg-linear-to-r from-white to-slate-500">VOICE<span class="text-indigo-500">CLONER</span></div>
            </div>
            <div class="hidden md:flex gap-8 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">
                <a href="/debug" class="hover:text-indigo-400 transition-colors">Diagnostics</a>
                <a href="#" class="hover:text-indigo-400 transition-colors">Docs</a>
                <a href="#" class="hover:text-indigo-400 transition-colors">Pricing</a>
            </div>
        </nav>

        <!-- Hero -->
        <header class="mb-24 text-center">
            <h1 class="text-6xl md:text-8xl font-black mb-6 tracking-tighter leading-none bg-clip-text text-transparent bg-linear-to-b from-white to-slate-500">
                Kloning Suara<br>Premium.
            </h1>
            <p class="text-slate-400 text-xl max-w-2xl mx-auto leading-relaxed">
                Platform SaaS profesional untuk kloning suara Bahasa Indonesia.<br>
                <span class="text-indigo-400 font-bold italic">Rekam sekali, gunakan selamanya.</span>
            </p>
        </header>

        <main class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- STEP 1 -->
            <div class="glass-card p-10 flex flex-col justify-between border-indigo-500/10">
                <div>
                    <div class="flex items-center gap-4 mb-10">
                        <div class="step-badge">01</div>
                        <h2 class="text-2xl font-black tracking-tight">Profil Suara</h2>
                    </div>

                    <div class="grid grid-cols-2 gap-4 mb-8">
                        <button id="recordBtn" class="bg-white/5 hover:bg-white/10 border border-white/5 rounded-3xl p-8 flex flex-col items-center gap-4 transition-all active:scale-95">
                            <div id="recordBtnCircle" class="w-16 h-16 rounded-full bg-slate-900 border border-white/5 flex items-center justify-center transition-all group-hover:scale-110">
                                <svg id="micIcon" class="w-7 h-7 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                </svg>
                                <div id="stopIcon" class="hidden w-6 h-6 bg-red-600 rounded-md"></div>
                            </div>
                            <span id="recordStatus" class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">Record</span>
                        </button>

                        <label for="fileUpload" class="bg-white/5 hover:bg-white/10 border border-white/5 rounded-3xl p-8 flex flex-col items-center gap-4 transition-all cursor-pointer active:scale-95">
                            <div class="w-16 h-16 rounded-full bg-slate-900 border border-white/5 flex items-center justify-center transition-all">
                                <svg class="w-7 h-7 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                </svg>
                            </div>
                            <span id="uploadLabel" class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 truncate w-full text-center">Upload</span>
                            <input type="file" id="fileUpload" class="hidden" accept="audio/*">
                        </label>
                    </div>
                </div>

                <div class="bg-indigo-500/10 rounded-3xl p-8 border border-indigo-500/20">
                    <p class="text-xs text-indigo-300/70 mb-6 font-medium leading-relaxed italic">
                        Untuk hasil natural, gunakan file <span class="text-white font-bold underline">suara-30menit.wav</span> sebagai dataset premium.
                    </p>
                    <button id="startTrainBtn" class="w-full bg-indigo-500 text-white font-black py-4 rounded-2xl shadow-xl shadow-indigo-500/20 active:scale-95 transition-all text-sm uppercase tracking-widest">
                        Fine-Tuning (30 MIN)
                    </button>
                    <div id="trainStatus" class="hidden mt-6 space-y-4">
                        <div class="flex justify-between items-center mb-1">
                            <span id="trainStep" class="text-[10px] font-black uppercase tracking-widest text-indigo-400">Initializing...</span>
                            <span id="trainPerc" class="text-[10px] font-black text-white">0%</span>
                        </div>
                        <div class="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-white/5">
                            <div id="trainBar" class="bg-indigo-500 h-full transition-all duration-500" style="width: 0%"></div>
                        </div>
                        <p id="trainMsg" class="text-[10px] text-slate-500 italic text-center">Waking up GPU A40...</p>
                    </div>
                </div>
            </div>

            <!-- STEP 2 -->
            <div id="step2" class="glass-card p-10 flex flex-col justify-between border-emerald-500/5">
                <div>
                    <div class="flex items-center gap-4 mb-10">
                        <div class="step-badge bg-emerald-500/10 border-emerald-500/20 text-emerald-400">02</div>
                        <h2 class="text-2xl font-black tracking-tight">Ketik & Suarakan</h2>
                    </div>

                    <div class="space-y-8">
                        <div>
                            <textarea id="textInput"
                                class="w-full bg-black/40 border border-white/5 rounded-3xl p-6 text-white text-lg placeholder-slate-700 focus:outline-none focus:border-indigo-500/50 transition-all resize-none shadow-inner leading-relaxed"
                                rows="5"
                                placeholder="Tulis naskah Anda di sini..."></textarea>
                        </div>

                        <div class="bg-white/5 p-6 rounded-3xl border border-white/5">
                            <div class="flex justify-between items-center mb-4">
                                <label class="text-[10px] font-black uppercase tracking-widest text-slate-500">Speed</label>
                                <span id="speedValue" class="text-sm font-black text-white">1.1x</span>
                            </div>
                            <input type="range" id="speedSelector" min="0.5" max="2.0" step="0.1" value="1.1" class="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500">
                        </div>
                    </div>
                </div>

                <button id="generateBtn" class="premium-btn w-full py-5 rounded-3xl font-black text-white shadow-2xl mt-8 active:scale-95 transition-all tracking-widest text-lg uppercase">
                    Generate
                </button>
            </div>

            <!-- PREVIEW (HIDDEN) -->
            <div id="previewContainer" class="hidden lg:col-span-2 glass-card p-6 bg-indigo-500/5 border-indigo-500/20">
                <div class="flex items-center gap-4 mb-4">
                    <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                    <span class="text-[10px] font-black uppercase tracking-widest text-emerald-400">Reference Ready</span>
                </div>
                <audio id="audioPreview" controls class="w-full opacity-60"></audio>
            </div>

            <!-- RESULT -->
            <div id="resultSection" class="hidden lg:col-span-2 glass-card p-12 border-emerald-500/40 animate-in fade-in slide-in-from-bottom-12 duration-1000">
                <div class="flex flex-col items-center text-center gap-8">
                    <div class="step-badge w-14 h-14 bg-emerald-500/10 border-emerald-500/20 text-emerald-400 text-xl">03</div>
                    <div class="w-full bg-black/60 p-10 rounded-[40px] border border-white/5 shadow-2xl">
                        <audio id="finalAudio" controls class="w-full"></audio>
                    </div>
                    <div class="flex gap-4 w-full max-w-md">
                        <a id="downloadBtn" href="#" download class="flex-1 bg-white text-black font-black py-4 rounded-3xl transition-all hover:bg-slate-200 active:scale-95 text-center uppercase text-sm tracking-widest">
                            Download
                        </a>
                        <button onclick="window.location.reload()" class="flex-1 bg-white/5 text-slate-400 font-black py-4 rounded-3xl border border-white/5 active:scale-95 uppercase text-sm tracking-widest">
                            Reset
                        </button>
                    </div>
                </div>
            </div>
        </main>

        <footer class="mt-40 text-center pb-20 opacity-30">
            <p class="text-[9px] font-black uppercase tracking-[0.5em] text-slate-500">VOICECLONER AI CORE — 2026</p>
        </footer>
    </div>

    <!-- Script Tetap Sama (Logika Tidak Berubah) -->
    <div id="toast-container"></div>

    <script>
        // GLOBAL HELPERS
        function showToast(message, type = 'info') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = 'toast';

            const icon = type === 'success' ? '✅' : (type === 'error' ? '❌' : '🚀');
            toast.innerHTML = `<span>${icon}</span> <span class="text-sm font-medium">${message}</span>`;

            container.appendChild(toast);
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(20px)';
                toast.style.transition = 'all 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }, 5000);
        }

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
                downloadBtn: document.getElementById('downloadBtn')
            };

            elements.speedSelector.addEventListener('input', () => elements.speedValue.textContent = elements.speedSelector.value + 'x');

            async function initializeVoiceProfile(blob) {
                elements.recordStatus.textContent = "Wait...";
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
                        elements.recordStatus.textContent = "Ready";
                    }
                } catch (err) {
                    console.error(err);
                    elements.recordStatus.textContent = "Local";
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
                    elements.recordStatus.textContent = "Rec...";
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
                    elements.uploadLabel.textContent = finalWavBlob.name.substring(0, 8) + '...';
                    elements.audioPreview.src = URL.createObjectURL(finalWavBlob);
                    elements.previewContainer.classList.remove('hidden');
                    await initializeVoiceProfile(finalWavBlob);
                }
            });

            elements.generateBtn.addEventListener('click', async () => {
                const text = elements.textInput.value;
                if (!text) return;

                if (!currentSpeakerId && !finalWavBlob) {
                    alert('Input voice profile first.');
                    return;
                }

                elements.generateBtn.disabled = true;
                elements.generateBtn.innerHTML = "Processing...";

                const formData = new FormData();
                if (currentSpeakerId) {
                    formData.append('speaker_id', currentSpeakerId);
                } else {
                    formData.append('audio', finalWavBlob, 'ref.wav');
                }
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
                    elements.generateBtn.innerHTML = "Generate";
                }
            });

            document.getElementById('startTrainBtn').addEventListener('click', async () => {
                const btn = document.getElementById('startTrainBtn');
                const statusDiv = document.getElementById('trainStatus');
                const bar = document.getElementById('trainBar');
                const perc = document.getElementById('trainPerc');
                const step = document.getElementById('trainStep');
                const msg = document.getElementById('trainMsg');

                btn.disabled = true;
                statusDiv.classList.remove('hidden');

                const formData = new FormData();
                if (finalWavBlob) {
                    formData.append('audio', finalWavBlob);
                }

                try {
                    const response = await fetch('/api/start-training', {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content,
                            'Accept': 'application/json'
                        }
                    });

                    const data = await response.json();
                    if (data.success && data.pod_id) {
                        const podId = data.pod_id;
                        showToast(`Pod Berhasil Dibuat! ID: ${podId.substring(0,8)}...`, 'success');
                        showToast(`Memulai proses booting GPU A40...`, 'info');

                        // Start Polling
                        const pollInterval = setInterval(async () => {
                            try {
                                const statusRes = await fetch(`/api/training-status?pod_id=${podId}`);
                                const statusData = await statusRes.json();

                                if (statusData.status === 'running') {
                                    bar.style.width = statusData.progress_percent + '%';
                                    perc.textContent = statusData.progress_percent + '%';
                                    step.textContent = statusData.current_step;
                                    msg.textContent = statusData.message;
                                } else if (statusData.status === 'offline') {
                                    step.textContent = 'BOOTING...';
                                    msg.textContent = 'Menunggu sistem AI di Cloud siap (1-3 menit).';
                                } else if (statusData.status === 'completed') {
                                    clearInterval(pollInterval);
                                    bar.style.width = '100%';
                                    perc.textContent = '100%';
                                    step.textContent = 'DONE';
                                    msg.textContent = 'Training finished! You can now generate voice.';
                                    btn.disabled = false;
                                    currentSpeakerId = 'guest_admin';
                                    alert('🔥 Training Selesai! Model siap digunakan.');
                                } else if (statusData.status === 'error') {
                                    clearInterval(pollInterval);
                                    msg.textContent = 'Error: ' + statusData.message;
                                    msg.classList.add('text-red-500');
                                    btn.disabled = false;
                                }
                            } catch (e) {
                                console.log("Waiting for Pod proxy to be ready...");
                            }
                        }, 3000);

                    } else {
                        alert('Error: ' + (data.error || 'Unknown'));
                        btn.disabled = false;
                    }
                } catch (err) {
                    console.error(err);
                    alert('Network error.');
                    btn.disabled = false;
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