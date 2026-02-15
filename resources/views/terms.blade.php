<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terms of Service | VoiceCloner AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Outfit', sans-serif;
            background-color: #030712;
            color: #f3f4f6;
            background-image:
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.1) 0, transparent 50%),
                radial-gradient(at 100% 0%, rgba(168, 85, 247, 0.1) 0, transparent 50%);
        }

        .glass {
            background: rgba(17, 24, 39, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
</head>

<body class="min-h-screen pt-32 pb-20 px-6">
    @include('navbar')

    <div class="max-w-4xl mx-auto">
        <header class="text-center mb-16">
            <h1 class="text-5xl font-extrabold mb-6 tracking-tight">Terms of <span class="text-indigo-400 italic">Service</span></h1>
            <p class="text-gray-400 text-lg">Kebijakan penggunaan teknologi Voice Cloning AI</p>
        </header>

        <div class="glass rounded-[32px] p-10 space-y-12 leading-relaxed">
            <section>
                <h2 class="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                    <span class="text-indigo-500">01.</span> Penggunaan Etis
                </h2>
                <p class="text-gray-400">
                    Sistem ini dibuat untuk tujuan kreatif dan produktivitas. Pengguna dilarang keras menggunakan teknologi Voice Cloning ini untuk meniru identitas orang lain tanpa izin, menyebarkan berita bohong (hoax), atau melakukan tindakan penipuan suara (vishing).
                </p>
            </section>

            <section>
                <h2 class="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                    <span class="text-indigo-500">02.</span> Hak Kekayaan Intelektual
                </h2>
                <p class="text-gray-400">
                    Program ini mengintegrasikan teknologi open-source (XTTS v2 / Coqui TTS) di bawah lisensi Mozilla Public License 2.0. Pengembang memberikan hak penggunaan kepada klien, namun membebaskan diri dari tanggung jawab hukum jika klien menyalahgunakan output suara yang dihasilkan oleh sistem.
                </p>
            </section>

            <section>
                <h2 class="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                    <span class="text-indigo-500">03.</span> Tanggung Jawab Konten
                </h2>
                <p class="text-gray-400">
                    Segala bentuk kerugian yang muncul akibat penyebaran audio yang dihasilkan oleh AI ini sepenuhnya menjadi tanggung jawab Pengguna/Klien. Kami menyarankan untuk selalu memberikan tanda (label) bahwa konten tersebut adalah **"AI Generated Content"** untuk menjaga transparansi publik.
                </p>
            </section>

            <section>
                <h2 class="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                    <span class="text-indigo-500">04.</span> Batasan Garansi
                </h2>
                <p class="text-gray-400">
                    Teknologi AI ini bergantung pada server lokal dan model pre-trained. Kualitas suara bisa bervariasi tergantung pada kualitas audio referensi yang diunggah. Kami tidak menjamin kemiripan 100% pada setiap jenis karakter suara.
                </p>
            </section>

            <div class="pt-10 border-t border-white/5 text-center">
                <p class="text-gray-500 text-sm italic">
                    Dengan menggunakan aplikasi ini, Anda secara otomatis menyetujui seluruh kebijakan di atas sesuai hukum yang berlaku di Indonesia (UU ITE).
                </p>
            </div>
        </div>
    </div>
</body>

</html>