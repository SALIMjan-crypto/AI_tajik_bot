"""
VOICE LAYER — ElevenLabs speech-to-text and text-to-speech.

CTO note: These are the integration points that turn the text prototype into a
real voice agent. They are written and ready, but calling them requires a valid
ELEVENLABS_API_KEY and network access. In the pipeline:

    caller audio  --> transcribe() --> text
    agent text    --> synthesize() --> audio to caller

Tajik reality check (from our research):
  - STT (Scribe) supports Tajik at "Good" accuracy. Test on real phone audio
    with financial vocabulary before trusting it.
  - TTS Tajik voice quality is unconfirmed at native level. If it's weak,
    use a custom/cloned voice or run the pilot in Russian (ACTIVE_LANGUAGE="ru").
"""

import requests
from config.settings import ELEVENLABS_API_KEY, ACTIVE_LANGUAGE

# Map our language codes to ElevenLabs language codes.
_LANG_MAP = {"en": "eng", "ru": "rus", "tg": "tgk"}

# Choose a voice_id per language. Replace with real voice IDs from your
# ElevenLabs account (a cloned Tajik voice would go here for "tg").
_VOICE_IDS = {
    "en": "REPLACE_WITH_ENGLISH_VOICE_ID",
    "ru": "REPLACE_WITH_RUSSIAN_VOICE_ID",
    "tg": "REPLACE_WITH_TAJIK_OR_CLONED_VOICE_ID",
}


def transcribe(audio_bytes: bytes) -> str:
    """
    Speech-to-text via ElevenLabs Scribe.
    audio_bytes: raw audio from the telephony layer (e.g. WAV/OPUS).
    Returns the transcribed text.
    """
    resp = requests.post(
        "https://api.elevenlabs.io/v1/speech-to-text",
        headers={"xi-api-key": ELEVENLABS_API_KEY},
        files={"file": ("audio.wav", audio_bytes, "audio/wav")},
        data={"model_id": "scribe_v1", "language_code": _LANG_MAP[ACTIVE_LANGUAGE]},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("text", "")


def synthesize(text: str) -> bytes:
    """
    Text-to-speech via ElevenLabs.
    Returns audio bytes to stream back to the caller.
    """
    voice_id = _VOICE_IDS[ACTIVE_LANGUAGE]
    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.content
