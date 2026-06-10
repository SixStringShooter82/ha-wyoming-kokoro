ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    espeak-ng \
    git \
    wget \
    curl \
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
