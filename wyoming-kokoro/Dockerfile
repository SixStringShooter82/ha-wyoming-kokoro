ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    espeak-ng \
    git \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    wget

# Install Python dependencies
RUN pip3 install --no-cache-dir --break-system-packages \
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

# Copy server
COPY server.py /app/server.py
COPY run.sh /run.sh
RUN chmod +x /run.sh

WORKDIR /kokoro
CMD ["/run.sh"]
