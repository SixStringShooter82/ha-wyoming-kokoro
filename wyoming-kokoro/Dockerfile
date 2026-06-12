FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    espeak-ng git curl gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    kokoro-onnx wyoming soundfile numpy scipy

RUN sed -i 's/np\.load(voices_path)/np.load(voices_path, allow_pickle=True)/g' \
    /usr/local/lib/python3.11/site-packages/kokoro_onnx/__init__.py

COPY server.py /app/server.py
COPY entrypoint.py /app/entrypoint.py

WORKDIR /data
CMD ["python3", "/app/entrypoint.py"]
