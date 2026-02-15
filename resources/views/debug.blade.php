<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Backend Debugger | VoiceChanger</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Outfit', sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
        }

        .glow {
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
        }

        .status-online {
            color: #10b981;
        }

        .status-offline {
            color: #ef4444;
        }

        .card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }

        .card:hover {
            border-color: rgba(59, 130, 246, 0.5);
            transform: translateY(-5px);
        }
    </style>
</head>

<body class="min-h-screen flex flex-col items-center pt-32 pb-12 px-4">
    @include('navbar')
    <div class="max-w-4xl w-full">
        <div class="flex items-center justify-between mb-12">
            <div>
                <h1 class="text-4xl font-bold bg-linear-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                    AI Backend Debugger
                </h1>
                <p class="text-slate-400 mt-2">Monitor status server cloning suara secara real-time</p>
            </div>
            <button onclick="refreshStatus()" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-full font-semibold transition-all shadow-lg active:scale-95">
                Refresh Status
            </button>
        </div>

        <div id="engine-container" class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Shimmer Loading -->
            <div class="card p-6 rounded-2xl animate-pulse h-48"></div>
            <div class="card p-6 rounded-2xl animate-pulse h-48"></div>
        </div>

        <div class="mt-12 card p-8 rounded-3xl">
            <h2 class="text-xl font-bold mb-4 flex items-center">
                <span class="w-3 h-3 bg-yellow-400 rounded-full mr-3"></span>
                System Diagnostics
            </h2>
            <div id="diagnostics" class="space-y-4 text-sm text-slate-300">
                <p>Silakan klik Refresh untuk memulai pengecekan server.</p>
            </div>
        </div>

        <div class="mt-8 text-center text-slate-500 text-xs">
            &copy; 2026 VoiceChanger Pro - Freelance Project Pandu
        </div>
    </div>

    <script>
        async function refreshStatus() {
            const container = document.getElementById('engine-container');
            const diagnostics = document.getElementById('diagnostics');

            try {
                const response = await fetch('/api/engine-status');
                const data = await response.json();

                container.innerHTML = '';
                diagnostics.innerHTML = `<p class="text-blue-400">[${new_timestamp()}] Pengetesan server dimulai...</p>`;

                const engines = data.engines;
                for (const [key, engine] of Object.entries(engines)) {
                    const isOnline = engine.available;
                    const statusClass = isOnline ? 'status-online' : 'status-offline';
                    const statusText = isOnline ? 'ONLINE' : 'OFFLINE';
                    const icon = isOnline ? '🟢' : '🔴';

                    container.innerHTML += `
                        <div class="card p-6 rounded-2xl relative overflow-hidden ${isOnline ? 'glow' : ''}">
                            <div class="flex justify-between items-start mb-4">
                                <span class="text-xs font-bold px-2 py-1 rounded bg-slate-800 text-slate-400 uppercase">Port ${engine.port}</span>
                                <span class="font-bold ${statusClass}">${statusText}</span>
                            </div>
                            <h3 class="text-xl font-bold mb-1">${engine.name}</h3>
                            <p class="text-xs text-slate-400 mb-4">${engine.quality}</p>
                            
                            <div class="text-[10px] font-mono text-slate-500 bg-black/30 p-2 rounded">
                                ${isOnline ? JSON.stringify(engine.details) : 'Server tidak merespon / belum dijalankan'}
                            </div>
                        </div>
                    `;

                    diagnostics.innerHTML += `
                        <p class="${statusClass}">
                            [${new_timestamp()}] Engine ${engine.name} di Port ${engine.port} -> ${statusText}
                        </p>
                    `;
                }

                diagnostics.innerHTML += `<p class="text-green-400 mt-2">✓ Selesai. Seluruh backend telah diperiksa.</p>`;
            } catch (error) {
                diagnostics.innerHTML = `<p class="text-red-500 font-bold">Error: Gagal terhubung ke API Laravel. Harap pastikan 'php artisan serve' sudah jalan.</p>`;
            }
        }

        function new_timestamp() {
            const now = new Date();
            return now.getHours().toString().padStart(2, '0') + ':' +
                now.getMinutes().toString().padStart(2, '0') + ':' +
                now.getSeconds().toString().padStart(2, '0');
        }

        // Auto refresh on load
        window.onload = refreshStatus;
    </script>
</body>

</html>