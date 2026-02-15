<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('voice_generations', function (Blueprint $view) {
            $view->id();
            $view->foreignId('user_id')->nullable()->constrained()->onDelete('cascade');
            $view->text('input_text');
            $view->string('reference_audio_path');
            $view->string('result_audio_path')->nullable();
            $view->string('status')->default('pending'); // pending, processing, completed, failed
            $view->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('voice_generations');
    }
};
