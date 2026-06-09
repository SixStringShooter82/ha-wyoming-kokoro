#!/usr/bin/with-contenv bashio

VOICE=$(bashio::config 'voice')
SPEED=$(bashio::config 'speed')

bashio::log.info "Starting Wyoming Kokoro TTS..."
bashio::log.info "Voice: ${VOICE}"
bashio::log.info "Speed: ${SPEED}"

exec python3 -m wyoming_kokoro \
    --voice "${VOICE}" \
    --speed "${SPEED}" \
    --uri tcp://0.0.0.0:10200
