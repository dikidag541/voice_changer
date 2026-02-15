import os
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from redis import Redis
from rq import Queue
from rq.job import Job

app = Flask(__name__)
CORS(app)

# Redis Connection
redis_conn = Redis()
voice_queue = Queue('voice_jobs', connection=redis_conn)

# Configuration
backend_dir = os.path.dirname(os.path.abspath(__file__))
temp_folder = os.path.join(backend_dir, "temp_audio")
generated_folder = os.path.join(backend_dir, "generated_audio")

os.makedirs(temp_folder, exist_ok=True)
os.makedirs(generated_folder, exist_ok=True)

@app.route('/generate', methods=['POST'])
def generate_voice():
    """
    Endpoint to receive voice generation request.
    Laravel will send: audio (file), text (form)
    """
    if 'audio' not in request.files or 'text' not in request.form:
        return jsonify({"error": "Missing audio or text"}), 400
    
    audio_file = request.files['audio']
    text = request.form['text']
    model_type = request.form.get('model_type', 'fine-tuned') # Default to premium
    job_id = str(uuid.uuid4())
    
    # Save reference audio temporarily
    ref_path = os.path.join(temp_folder, f"ref_{job_id}.wav")
    audio_file.save(ref_path)
    
    # Enqueue the job to Redis using string reference to avoid loading model in API
    job = voice_queue.enqueue(
        'voice_worker.process_voice_job', 
        args=(text, ref_path, job_id, model_type),
        job_id=job_id,
        result_ttl=3600 # Keep result for 1 hour
    )
    
    return jsonify({
        "status": "queued",
        "job_id": job_id,
        "message": "Voice generation job added to queue"
    }), 202

@app.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """
    Check the status of a specific job
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        if job.is_queued:
            return jsonify({"status": "queued", "job_id": job_id}), 200
        elif job.is_started:
            return jsonify({"status": "processing", "job_id": job_id}), 200
        elif job.is_finished:
            return jsonify({
                "status": "completed", 
                "job_id": job_id, 
                "download_url": f"/download/{job_id}"
            }), 200
        elif job.is_failed:
            return jsonify({"status": "failed", "error": str(job.exc_info)}), 500
            
    except Exception as e:
        return jsonify({"error": "Job not found"}), 404

@app.route('/download/<job_id>', methods=['GET'])
def download_audio(job_id):
    """
    Download the generated audio file
    """
    out_path = os.path.join(generated_folder, f"voice_{job_id}.wav")
    if os.path.exists(out_path):
        return send_file(out_path, mimetype='audio/wav')
    else:
        return jsonify({"error": "File not found"}), 404

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "mode": "queue_system_active"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
