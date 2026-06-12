#!/usr/bin/env python3
"""
Entrypoint - downloads models and starts Wyoming server
Replaces run.sh to avoid CRLF issues
"""
import os
import sys
import subprocess

MODEL_DIR = "/data/kokoro-models"
os.makedirs(MODEL_DIR, exist_ok=True)

ONNX_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

def download(url, path):
    print(f"Downloading {os.path.basename(path)}...")
    subprocess.run(["curl", "-L", "-o", path, url], check=True)

if not os.path.exists(f"{MODEL_DIR}/kokoro-v1.0.onnx"):
    download(ONNX_URL, f"{MODEL_DIR}/kokoro-v1.0.onnx")

voices_path = f"{MODEL_DIR}/voices-v1.0.bin"
if not os.path.exists(voices_path) or os.path.getsize(voices_path) < 1000:
    download(VOICES_URL, voices_path)

print("Models ready. Starting Wyoming Kokoro TTS v2.1...")
os.execv(sys.executable, [
    sys.executable, "/app/server.py",
    "--uri", "tcp://0.0.0.0:10200",
    "--config", "/data/options.json",
    "--model-dir", MODEL_DIR
])
