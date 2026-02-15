import requests
import time

API_URL = "http://localhost:5002"
REFERENCE_WAV = "/Users/dikiferdianto/Voice-Changer/voice-changer/python_backend/finetune/datasets/indonesian_voice/wavs/chunk_0006.wav"

def test_pipeline():
    print("📤 Sending job to Queue API...")
    with open(REFERENCE_WAV, 'rb') as f:
        files = {'audio': f}
        data = {'text': 'Ini adalah uji coba sistem antrean produksi. Harap bersabar, suara sedang diproses di latar belakang.'}
        response = requests.post(f"{API_URL}/generate", files=files, data=data)
    
    if response.status_code != 202:
        print(f"❌ Failed to enqueue: {response.text}")
        return
    
    job_id = response.json()['job_id']
    print(f"✅ Job Enqueued! Job ID: {job_id}")
    
    # Poll for status
    while True:
        status_resp = requests.get(f"{API_URL}/status/{job_id}")
        status = status_resp.json().get('status')
        print(f"🔄 Current Status: {status}")
        
        if status == 'completed':
            print("🎉 Job Completed!")
            print(f"🔗 Download URL: {API_URL}{status_resp.json()['download_url']}")
            break
        elif status == 'failed':
            print(f"❌ Job Failed: {status_resp.json().get('error')}")
            break
        
        time.sleep(5)

if __name__ == "__main__":
    test_pipeline()
