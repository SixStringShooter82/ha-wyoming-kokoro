FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    espeak-ng \
    git \
    gcc \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    kokoro-onnx \
    wyoming \
    soundfile \
    numpy \
    scipy

# Download Kokoro model files
RUN mkdir -p /kokoro && \
    wget -q -O /kokoro/kokoro-v1.0.onnx \
    https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v1.0.onnx && \
    wget -q -O /kokoro/voices.bin \
    https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.bin

COPY server.py /app/server.py
COPY run.sh /run.sh
RUN chmod +x /run.sh

WORKDIR /kokoro
CMD ["/run.sh"]
