FROM ghcr.io/home-assistant/amd64-base-python:3.12

RUN apt-get update && apt-get install -y \
    espeak-ng \
    git \
    wget \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
    kokoro-onnx \
    wyoming \
    soundfile \
    numpy \
    scipy

COPY server.py /app/server.py
COPY run.sh /run.sh
RUN chmod +x /run.sh

WORKDIR /data
CMD ["/run.sh"]
