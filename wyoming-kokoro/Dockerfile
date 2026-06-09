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
    python3-dev

# Install Python dependencies
RUN pip3 install --no-cache-dir --break-system-packages \
    kokoro-onnx \
    wyoming \
    soundfile

# Install wyoming-kokoro from GitHub
RUN pip3 install --no-cache-dir --break-system-packages \
    git+https://github.com/dstrout/wyoming-kokoro.git

COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
