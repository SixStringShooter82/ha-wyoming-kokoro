ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.12-alpine3.21
FROM ${BUILD_FROM}

RUN apk add --no-cache \
    espeak-ng \
    git \
    wget \
    curl \
    gcc \
    musl-dev \
    python3-dev

RUN pip3 install --no-cache-dir --break-system-packages \
    kokoro-onnx \
    wyoming \
    soundfile \
    numpy \
    scipy

RUN sed -i 's/np\.load(voices_path)/np.load(voices_path, allow_pickle=True)/g' \
    /usr/local/lib/python3.12/site-packages/kokoro_onnx/__init__.py

COPY server.py /app/server.py
COPY run.sh /run.sh
RUN chmod +x /run.sh

WORKDIR /data
CMD ["/run.sh"]
