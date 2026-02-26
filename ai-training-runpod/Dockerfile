# Gunakan image CUDA untuk RTX 4090
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Setup environment
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/workspace/ai-training-worker

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    ffmpeg \
    libsndfile1 \
    git \
    git-lfs \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Setup workdir
WORKDIR /workspace/ai-training-worker

# Install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Copy source code
COPY . .

# Expose FastAPI port
EXPOSE 8001

# Jalankan server (uvicorn untuk production)
CMD ["python3", "-m", "uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8001"]
