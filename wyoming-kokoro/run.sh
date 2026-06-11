#!/bin/bash

MODEL_DIR="/data/kokoro-models"
mkdir -p "${MODEL_DIR}"

if [ ! -f "${MODEL_DIR}/kokoro-v1.0.onnx" ]; then
    echo "Downloading Kokoro model (one time only)..."
    curl -L -o "${MODEL_DIR}/kokoro-v1.0.onnx" \
        "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
fi

if [ ! -f "${MODEL_DIR}/voices.bin" ] || [ $(wc -c < "${MODEL_DIR}/voices.bin") -lt 1000 ]; then
    echo "Downloading voices file (one time only)..."
    curl -L -o "${MODEL_DIR}/voices.bin" \
        "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices.bin"
fi

echo "Model ready. Starting Wyoming Kokoro TTS v2.0..."

exec python3 /app/server.py \
    --uri tcp://0.0.0.0:10200 \
    --config /data/options.json \
    --model-dir "${MODEL_DIR}"
