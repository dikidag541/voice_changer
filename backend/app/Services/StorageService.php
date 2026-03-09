<?php

namespace App\Services;

use Illuminate\Support\Facades\Storage;

class StorageService
{
    /**
     * Handle S3 / Cloud Storage logic
     */
    public function uploadToCloud($localPath, $cloudPath)
    {
        if (!is_file($localPath)) {
            \Illuminate\Support\Facades\Log::error("❌ Upload Error: $localPath is not a valid file.");
            return false;
        }

        $disk = config('filesystems.disks.s3.key') ? 's3' : 'public';
        
        // Pisahkan directory dan filename
        $dir = dirname($cloudPath);
        $filename = basename($cloudPath);

        // putFileAs mendukung streaming (tidak makan RAM meski file 1.42GB)
        return Storage::disk($disk)->putFileAs($dir, new \Illuminate\Http\File($localPath), $filename);
    }

    public function getPresignedUrl($path)
    {
        $disk = config('filesystems.disks.s3.key') ? 's3' : 'public';

        /** @var \Illuminate\Filesystem\FilesystemAdapter $diskObj */
        $diskObj = Storage::disk($disk);

        return $diskObj->url($path);
    }
}
