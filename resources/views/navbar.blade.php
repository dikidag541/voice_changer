<nav class="fixed top-0 left-0 w-full z-50 transition-all duration-300 px-6 py-4" id="mainNav">
    <div class="max-w-6xl mx-auto flex justify-between items-center glass rounded-2xl px-6 py-3 border border-white/5">
        <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center font-bold text-white">V</div>
            <span class="text-xl font-bold tracking-tight text-white">Voice<span class="text-indigo-400">Cloner</span></span>
        </div>

        <div class="hidden md:flex items-center gap-8">
            <a href="/" class="text-sm font-medium {{ Request::is('/') ? 'text-white' : 'text-gray-400' }} hover:text-indigo-400 transition-colors">Home</a>
            <a href="/debug" class="text-sm font-medium {{ Request::is('debug') ? 'text-white' : 'text-gray-400' }} hover:text-indigo-400 transition-colors">Backend Debugger</a>
            <a href="/terms" class="text-sm font-medium {{ Request::is('terms') ? 'text-white' : 'text-gray-400' }} hover:text-indigo-400 transition-colors">Terms</a>
        </div>

        <div>
            <a href="https://github.com/pandustrr/voice-changer" target="_blank" class="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-sm font-medium text-white border border-white/10 transition-all">
                GitHub
            </a>
        </div>
    </div>
</nav>

<style>
    .glass {
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>