#!/usr/bin/with-contenv bashio

bashio::log.info "Starting Wyoming Kokoro TTS v2.0..."
bashio::log.info "Multi-character emotional TTS engine"

exec python3 /app/server.py \
    --uri tcp://0.0.0.0:10200 \
    --config /data/options.json
