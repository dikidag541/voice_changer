<!DOCTYPE html>
<html lang="en" class="dark">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SaaS Dashboard — VoiceCloner Cloud</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
    @vite(['resources/css/app.css', 'resources/js/app.js'])
    <style>
        :root {
            --app-bg: #030712;
            --card-bg: rgba(17, 24, 39, 0.7);
        }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--app-bg);
            background-image:
                radial-gradient(circle at 0% 0%, rgba(99, 102, 241, 0.1) 0%, transparent 40%),
                radial-gradient(circle at 100% 100%, rgba(168, 85, 247, 0.05) 0%, transparent 40%);
            color: #f1f5f9;
            min-height: 100vh;
        }

        .glass-card {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 24px;
        }

        .status-pill {
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.6rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .pulse-emerald {
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4);
            animation: pulse-emerald 2s infinite;
        }

        @keyframes pulse-emerald {
            0% {
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4);
            }

            70% {
                box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
            }

            100% {
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
            }
        }

        .step-node {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.7rem;
            z-index: 10;
        }
    </style>
</head>

<body class="p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
        <!-- TOP NAV -->
        <header class="flex justify-between items-center mb-10">
            <div class="flex items-center gap-4">
                <div class="w-10 h-10 rounded-xl bg-indigo-500 flex items-center justify-center font-bold text-lg shadow-lg shadow-indigo-500/20">V</div>
                <div>
                    <h1 class="text-xl font-bold tracking-tight">Cloud Console</h1>
                    <p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Real-time Infrastructure</p>
                </div>
            </div>
            <div class="flex items-center gap-4">
                <div class="glass-card px-4 py-2 flex flex-col items-end">
                    <span class="text-[9px] font-black text-slate-500 uppercase tracking-widest">Available Credit</span>
                    <span id="balance-value" class="text-emerald-400 font-bold tracking-tight">$0.00</span>
                </div>
                <a href="/" class="glass-card px-5 py-2.5 text-xs font-bold text-slate-300 hover:text-white transition-all flex items-center gap-2 active:scale-95">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                    </svg>
                    DASHBOARD
                </a>
            </div>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <!-- MAIN CONTENT -->
            <div class="lg:col-span-3 space-y-6">
                <!-- EXECUTION ENGINE -->
                <div class="glass-card p-8 bg-linear-to-br from-indigo-500/5 to-transparent">
                    <div class="flex justify-between items-center mb-8">
                        <div>
                            <h2 class="text-lg font-bold">Execution Engine</h2>
                            <p class="text-xs text-slate-500">XTTS v2 Premium fine-tuning architecture.</p>
                        </div>
                        <div id="ai-status-badge" class="status-pill bg-slate-800 text-slate-400">
                            <div class="w-1.5 h-1.5 rounded-full bg-slate-500"></div>
                            SCANNING
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="bg-black/30 p-5 rounded-3xl border border-white/5">
                            <span class="text-[9px] font-black text-indigo-400 uppercase tracking-widest block mb-2">Strategy</span>
                            <div class="flex items-center gap-3">
                                <div class="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_10px_#10b981]"></div>
                                <span class="text-sm font-bold text-white">Dynamic A40 Provisioning</span>
                            </div>
                        </div>
                        <div class="bg-black/30 p-5 rounded-3xl border border-white/5">
                            <span class="text-[9px] font-black text-indigo-400 uppercase tracking-widest block mb-2">Endpoint URL</span>
                            <code class="text-[10px] text-slate-400 font-mono block truncate">{{ env('AI_TRAINING_URL') }}</code>
                        </div>
                    </div>
                </div>

                <!-- CLOUD POD EXPLORER -->
                <div class="glass-card p-8">
                    <div class="flex justify-between items-center mb-8">
                        <h2 class="text-lg font-bold flex items-center gap-3">
                            Cloud Pod Explorer
                            <span id="pod-count" class="bg-indigo-500/10 text-indigo-400 text-[10px] px-2 py-0.5 rounded-lg border border-indigo-500/20">0 Active</span>
                        </h2>
                        <button onclick="updatePodList()" class="p-2 glass-card hover:bg-white/5 transition-colors">
                            <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                        </button>
                    </div>

                    <div id="pod-list" class="space-y-4">
                        <div class="flex flex-col items-center py-10 opacity-30">
                            <svg class="w-10 h-10 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                            </svg>
                            <p class="text-xs font-bold">Scanning RunPod API...</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- SIDEBAR -->
            <div class="space-y-6">
                <!-- AUTH STATUS -->
                <div class="glass-card p-6">
                    <h2 class="text-sm font-bold mb-6 text-slate-400 tracking-widest uppercase">Service Connectivity</h2>
                    <div class="space-y-3">
                        @foreach(['R2' => 'AWS_ACCESS_KEY_ID', 'RunPod' => 'RUNPOD_API_KEY', 'Modal' => 'MODAL_TOKEN_ID'] as $svc => $env)
                        <div class="flex items-center justify-between p-3 bg-white/5 rounded-2xl border border-white/5">
                            <span class="text-xs font-bold">{{ $svc }}</span>
                            <div class="flex items-center gap-2">
                                <span class="text-[8px] font-black {{ env($env) ? 'text-emerald-500' : 'text-slate-600' }}">{{ env($env) ? 'CONNECTED' : 'MISSING' }}</span>
                                <div class="w-1.5 h-1.5 rounded-full {{ env($env) ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-slate-700' }}"></div>
                            </div>
                        </div>
                        @endforeach
                    </div>
                </div>

                <!-- PIPELINE -->
                <div class="glass-card p-6 bg-indigo-500/5 border-indigo-500/20">
                    <h2 class="text-sm font-bold mb-6 text-indigo-400 tracking-widest uppercase">Pipeline Flow</h2>
                    <div class="space-y-6 relative">
                        <div class="absolute left-3 top-2 bottom-2 w-0.5 bg-slate-800"></div>
                        @foreach(['Upload to R2', 'Sewa A40', 'Auto-Training', 'Cleanup Pod'] as $i => $step)
                        <div class="flex items-center gap-4 relative z-10">
                            <div class="w-6 h-6 rounded-full {{ $i == 0 ? 'bg-indigo-500 shadow-lg shadow-indigo-500/40' : 'bg-slate-800' }} flex items-center justify-center text-[10px] font-bold">
                                {{ $i + 1 }}
                            </div>
                            <span class="text-xs font-medium {{ $i == 0 ? 'text-white' : 'text-slate-500' }}">{{ $step }}</span>
                        </div>
                        @endforeach
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- MODAL DELETE CONFIRMATION (REUSABLE) -->
    <script>
        async function checkHealth() {
            const badge = document.getElementById('ai-status-badge');
            try {
                const response = await fetch('/api/engine-status');
                const data = await response.json();
                if (data.engines.xtts.available) {
                    badge.innerHTML = '<div class="w-1.5 h-1.5 rounded-full bg-emerald-500 pulse-emerald"></div> ONLINE';
                    badge.className = "status-pill bg-emerald-500/10 text-emerald-500 border border-emerald-500/20";
                } else {
                    badge.innerHTML = '<div class="w-1.5 h-1.5 rounded-full bg-indigo-500"></div> STANDBY';
                    badge.className = "status-pill bg-indigo-400/10 text-indigo-400 border border-indigo-400/20";
                }
            } catch (err) {
                badge.innerHTML = '<div class="w-1.5 h-1.5 rounded-full bg-red-500"></div> DISCONNECTED';
                badge.className = "status-pill bg-red-500/10 text-red-500 border border-red-500/20";
            }
        }

        async function updateBalance() {
            try {
                const res = await fetch('/api/balance');
                const data = await res.json();
                if (data.balance !== undefined) {
                    document.getElementById('balance-value').textContent = '$' + data.balance.toFixed(2);
                }
            } catch (e) {}
        }

        async function terminatePod(podId) {
            if (!confirm(`Hentikan Pod ${podId}? Sesi training akan dibatalkan.`)) return;

            try {
                const res = await fetch('/api/terminate-pod', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': '{{ csrf_token() }}'
                    },
                    body: JSON.stringify({
                        pod_id: podId
                    })
                });
                const data = await res.json();
                if (data.success) {
                    updatePodList();
                    updateBalance();
                }
            } catch (e) {
                alert('Gagal menghentikan pod.');
            }
        }

        async function updatePodList() {
            const list = document.getElementById('pod-list');
            try {
                const res = await fetch('/api/list-pods');
                const pods = await res.json();

                document.getElementById('pod-count').textContent = pods.length + ' Active';

                if (pods.length === 0) {
                    list.innerHTML = `
                        <div class="flex flex-col items-center py-10 opacity-30">
                            <svg class="w-10 h-10 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                            <p class="text-xs font-bold italic">No active pods found.</p>
                        </div>
                    `;
                    return;
                }

                list.innerHTML = pods.map(pod => {
                    const status = pod.runtime ? pod.runtime.status : 'CREATED';
                    const isRunning = status === 'RUNNING';

                    return `
                        <div class="p-5 bg-white/5 rounded-3xl border border-white/5 flex items-center justify-between group hover:border-indigo-500/30 transition-all">
                            <div class="flex items-center gap-5">
                                <div class="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 border border-indigo-500/20">
                                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                                </div>
                                <div>
                                    <div class="flex items-center gap-2 mb-1">
                                        <h3 class="font-bold text-sm text-white">${pod.name}</h3>
                                        <span class="text-[8px] font-black font-mono px-1.5 py-0.5 rounded bg-black/40 text-slate-500 border border-white/5">${pod.id}</span>
                                    </div>
                                    <div class="flex items-center gap-4">
                                        <div class="flex items-center gap-1.5">
                                            <div class="w-1.5 h-1.5 rounded-full ${isRunning ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-amber-500'}"></div>
                                            <span class="text-[10px] font-bold text-slate-400 capitalize">${status.toLowerCase()}</span>
                                        </div>
                                        <div class="text-[10px] text-slate-600 font-bold">• ${pod.gpuName || pod.gpu_name || 'GPU Reserved'}</div>
                                    </div>
                                </div>
                            </div>
                            <div class="flex items-center gap-3">
                                ${isRunning ? `
                                    <a href="https://${pod.id}-8888.proxy.runpod.net" target="_blank" class="p-2.5 rounded-xl bg-white/5 hover:bg-indigo-500/10 text-indigo-400 border border-white/5 transition-all active:scale-95" title="Open Web Terminal">
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                                    </a>
                                ` : ''}
                                <button onclick="terminatePod('${pod.id}')" class="p-2.5 rounded-xl bg-red-500/5 hover:bg-red-500/10 text-red-500 border border-red-500/10 transition-all active:scale-95" title="Terminate Pod">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                                </button>
                            </div>
                        </div>
                    `;
                }).join('');
            } catch (e) {
                list.innerHTML = '<p class="text-xs text-red-500 text-center py-10 font-bold uppercase tracking-widest">Failed to sync with RunPod API.</p>';
            }
        }

        window.onload = () => {
            checkHealth();
            updateBalance();
            updatePodList();
            setInterval(updatePodList, 10000);
            setInterval(updateBalance, 30000);
        }
    </script>
</body>

</html>