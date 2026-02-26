import boto3
import os
from dotenv import load_dotenv

load_dotenv()

class S3Manager:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=os.getenv('AWS_ENDPOINT'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION', 'auto')
        )
        self.bucket = os.getenv('AWS_BUCKET')

    def download_dataset(self, bucket, remote_path, local_path):
        """Download file audio tunggal dari S3/R2"""
        print(f"📥 Downloading dataset from {remote_path} to {local_path}...")
        bucket_name = bucket if bucket else self.bucket
        
        # Pastikan directory tujuan ada
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        try:
            self.s3.download_file(bucket_name, remote_path, local_path)
            print("✅ Download selesai.")
            return True
        except Exception as e:
            print(f"❌ Error downloading file: {str(e)}")
            return False

    def download_folder(self, remote_path, local_path):
        """Download folder dataset dari S3 ke worker Runpod (untuk banyak file)"""
        print(f"📥 Downloading folder from {remote_path}...")
        os.makedirs(local_path, exist_ok=True)
        
        paginator = self.s3.get_paginator('list_objects_v2')
        for result in paginator.paginate(Bucket=self.bucket, Prefix=remote_path):
            if 'Contents' in result:
                for obj in result['Contents']:
                    key = obj['Key']
                    if not key.endswith('/'):
                        filename = os.path.basename(key)
                        self.s3.download_file(self.bucket, key, os.path.join(local_path, filename))

    def upload_model(self, local_path, bucket, remote_path):
        """Upload hasil training (.pth, config.json atau folder) ke Cloud"""
        bucket_name = bucket if bucket else self.bucket
        
        if os.path.isfile(local_path):
            print(f"📤 Uploading file {local_path} to {remote_path}...")
            self.s3.upload_file(local_path, bucket_name, remote_path)
        else:
            print(f"📤 Uploading folder {local_path} to {remote_path}...")
            for root, dirs, files in os.walk(local_path):
                for file in files:
                    if file.endswith(('.pth', '.json', '.txt', '.csv')):
                        local_file = os.path.join(root, file)
                        # Hitung relative path untuk remote
                        rel_path = os.path.relpath(local_file, local_path)
                        remote_file = os.path.join(remote_path, rel_path)
                        self.s3.upload_file(local_file, bucket_name, remote_file)
        print("✅ Upload selesai.")
