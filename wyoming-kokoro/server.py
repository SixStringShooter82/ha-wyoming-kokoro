"""
Wyoming Kokoro TTS Server
Multi-character emotional TTS with voice blending, pitch control, and audio effects
"""

import argparse
import asyncio
import logging
import json
import re
import numpy as np
from typing import Optional

from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.server import AsyncEventHandler, AsyncServer
from wyoming.tts import Synthesize

from kokoro_onnx import Kokoro

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

EMOTION_PRESETS = {
    "neutral":  (1.0,  0,  "none"),
    "calm":     (0.85, -1, "none"),
    "excited":  (1.2,  2,  "none"),
    "urgent":   (1.3,  1,  "radio"),
    "serious":  (0.9,  -2, "none"),
    "whisper":  (0.7,  -1, "whisper"),
    "alert":    (1.15, 3,  "radio"),
    "sad":      (0.8,  -2, "none"),
    "friendly": (1.05, 1,  "none"),
}


def apply_pitch_shift(audio: np.ndarray, sample_rate: int, semitones: float) -> np.ndarray:
    if semitones == 0:
        return audio
    try:
        import scipy.signal
        factor = 2 ** (semitones / 12.0)
        new_length = int(len(audio) / factor)
        shifted = scipy.signal.resample(audio, new_length)
        return scipy.signal.resample(shifted, len(audio)).astype(np.float32)
    except Exception as e:
        _LOGGER.warning(f"Pitch shift failed: {e}")
        return audio


def apply_effect(audio: np.ndarray, sample_rate: int, effect: str) -> np.ndarray:
    if not effect or effect == "none":
        return audio
    try:
        import scipy.signal
        if effect == "reverb":
            decay = np.exp(-np.arange(int(sample_rate * 0.3)) / (sample_rate * 0.05))
            decay = decay / decay.sum()
            wet = np.convolve(audio, decay, mode='full')[:len(audio)]
            return (audio * 0.7 + wet * 0.3).astype(np.float32)
        elif effect == "telephone":
            nyq = sample_rate / 2
            b, a = scipy.signal.butter(4, [300/nyq, 3400/nyq], btype='band')
            filtered = scipy.signal.filtfilt(b, a, audio)
            return (np.tanh(filtered * 2) * 0.5).astype(np.float32)
        elif effect == "radio":
            nyq = sample_rate / 2
            b, a = scipy.signal.butter(3, [500/nyq, 3000/nyq], btype='band')
            filtered = scipy.signal.filtfilt(b, a, audio)
            noise = np.random.normal(0, 0.003, len(filtered))
            return (np.tanh((filtered + noise) * 3) * 0.4).astype(np.float32)
        elif effect == "whisper":
            nyq = sample_rate / 2
            b, a = scipy.signal.butter(2, 200/nyq, btype='high')
            filtered = scipy.signal.filtfilt(b, a, audio)
            noise = np.random.normal(0, 0.01, len(filtered))
            return (filtered * 0.7 + noise * 0.3).astype(np.float32)
        elif effect == "hall":
            decay = np.exp(-np.arange(int(sample_rate * 0.8)) / (sample_rate * 0.15))
            decay = decay / decay.sum()
            wet = np.convolve(audio, decay, mode='full')[:len(audio)]
            return (audio * 0.5 + wet * 0.5).astype(np.float32)
    except Exception as e:
        _LOGGER.warning(f"Effect '{effect}' failed: {e}")
    return audio


def process_text(text: str):
    overrides = {}
    emotion_match = re.search(r'\[emotion:(\w+)\]', text)
    if emotion_match:
        overrides['emotion'] = emotion_match.group(1)
        text = re.sub(r'\[emotion:\w+\]', '', text)
    text = re.sub(r'\[pause:\d+\]', ',', text)
    text = re.sub(r'\[/?emphasis\]', '', text)
    return text.strip(), overrides


class KokoroEventHandler(AsyncEventHandler):
    def __init__(self, kokoro: Kokoro, characters: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kokoro = kokoro
        self.characters = {c['name']: c for c in characters}

    async def handle_event(self, event: Event) -> bool:
        if not Synthesize.is_type(event.type):
            return True

        synthesize = Synthesize.from_event(event)
        text = synthesize.text
        voice_name = synthesize.voice.name if synthesize.voice else None

        character = None
        if voice_name and voice_name in self.characters:
            character = self.characters[voice_name]
        elif self.characters:
            character = next(iter(self.characters.values()))

        if not character:
            _LOGGER.error("No character configured")
            return False

        text, tag_overrides = process_text(text)
        emotion_name = tag_overrides.get('emotion', character.get('default_emotion', 'neutral'))
        emotion = EMOTION_PRESETS.get(emotion_name, EMOTION_PRESETS['neutral'])
        emotion_speed, emotion_pitch, emotion_effect = emotion

        speed = character.get('speed', 1.0) * emotion_speed
        pitch = character.get('pitch', 0) + emotion_pitch
        effect = character.get('effect', 'none') if emotion_effect == 'none' else emotion_effect

        voice1 = character['voice']
        voice2 = character.get('blend_voice', '')
        ratio = float(character.get('blend_ratio', 0.0))

        v1 = self.kokoro.get_voice(voice1)
        if voice2 and ratio > 0:
            v2 = self.kokoro.get_voice(voice2)
            voice_tensor = v1 * (1.0 - ratio) + v2 * ratio
        else:
            voice_tensor = v1

        lang = 'en-gb' if voice1.startswith('b') else 'en-us'

        _LOGGER.info(f"Synthesizing: char={character['name']} emotion={emotion_name} speed={speed:.2f} pitch={pitch} effect={effect}")

        samples, sample_rate = self.kokoro.create(
            text,
            voice=voice_tensor,
            speed=speed,
            lang=lang
        )

        if pitch != 0:
            samples = apply_pitch_shift(samples, sample_rate, pitch)

        if effect and effect != 'none':
            samples = apply_effect(samples, sample_rate, effect)

        max_val = np.max(np.abs(samples))
        if max_val > 0:
            samples = samples / max_val * 0.95

        audio_int16 = (samples * 32767).astype(np.int16)
        audio_bytes = audio_int16.tobytes()

        await self.write_event(AudioStart(rate=sample_rate, width=2, channels=1).event())
        chunk_size = 1024
        for i in range(0, len(audio_bytes), chunk_size):
            chunk = audio_bytes[i:i + chunk_size]
            await self.write_event(AudioChunk(audio=chunk, rate=sample_rate, width=2, channels=1).event())
        await self.write_event(AudioStop().event())
        return True


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", default="tcp://0.0.0.0:10200")
    parser.add_argument("--config", default="/data/options.json")
    parser.add_argument("--model-dir", default="/data/kokoro-models")
    args = parser.parse_args()

    with open(args.config) as f:
        options = json.load(f)

    characters = options.get('characters', [])
    model_dir = args.model_dir

    _LOGGER.info("Loading Kokoro model...")
    kokoro = Kokoro(
    f"{model_dir}/kokoro-v1.0.onnx",
    f"{model_dir}/voices-v1.0.bin"
)
    _LOGGER.info(f"Kokoro loaded with {len(characters)} character(s)")

    server = AsyncServer.from_uri(args.uri)
    _LOGGER.info(f"Wyoming server starting on {args.uri}")
    await server.run(lambda *a, **kw: KokoroEventHandler(kokoro, characters, *a, **kw))


if __name__ == "__main__":
    asyncio.run(main())
