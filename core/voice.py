"""
VOICE LAYER — open-source speech-to-text and text-to-speech.

CTO note: These are the integration points that turn the text prototype into a
real voice agent, using a fully self-hosted, open-source stack instead of a
paid third-party API — no client audio leaves the bank's own infrastructure.

    caller audio  --> transcribe() --> text     (faster-whisper, MIT-derived)
    agent text    --> synthesize() --> audio    (Piper TTS, MIT)

Setup:
  pip install faster-whisper piper-tts
  Download a Piper voice (.onnx + .onnx.json) per language you plan to use
  from https://huggingface.co/rhasspy/piper-voices and point
  PIPER_VOICE_PATHS at the .onnx files in config/settings.py.
  faster-whisper downloads its model automatically on first use (cached
  locally after that — still no data sent to a third party at inference time).

Tajik reality check (same as before): Piper does not currently ship a native
Tajik voice. If a suitable one isn't available, pilot in Russian
(ACTIVE_LANGUAGE="ru") while sourcing/fine-tuning a Tajik voice, exactly as
planned for the ElevenLabs-based version of this layer.
"""

import io
import tempfile
import wave

from config.settings import ACTIVE_LANGUAGE, WHISPER_MODEL_SIZE, PIPER_VOICE_PATHS

# Map our language codes to faster-whisper/Whisper language codes.
_WHISPER_LANG_MAP = {"en": "en", "ru": "ru", "tg": "tg"}

_whisper_model = None
_piper_voices = {}


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        # CPU + int8 by default so this runs without a GPU; switch device="cuda"
        # if the bank's server has one, for lower latency.
        _whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
    return _whisper_model


def _get_piper_voice():
    if ACTIVE_LANGUAGE in _piper_voices:
        return _piper_voices[ACTIVE_LANGUAGE]

    model_path = PIPER_VOICE_PATHS.get(ACTIVE_LANGUAGE)
    if not model_path:
        raise ValueError(
            f"No Piper voice configured for language='{ACTIVE_LANGUAGE}'. "
            f"Download a voice from https://huggingface.co/rhasspy/piper-voices "
            f"and set PIPER_VOICE_PATHS['{ACTIVE_LANGUAGE}'] in config/settings.py."
        )

    from piper import PiperVoice
    voice = PiperVoice.load(model_path)
    _piper_voices[ACTIVE_LANGUAGE] = voice
    return voice


def transcribe(audio_bytes: bytes) -> str:
    """
    Speech-to-text via faster-whisper, running locally.
    audio_bytes: raw audio from the telephony layer (e.g. WAV/OPUS).
    Returns the transcribed text.
    """
    model = _get_whisper_model()
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        segments, _info = model.transcribe(
            tmp.name, language=_WHISPER_LANG_MAP.get(ACTIVE_LANGUAGE)
        )
        return " ".join(seg.text.strip() for seg in segments).strip()


def synthesize(text: str) -> bytes:
    """
    Text-to-speech via Piper, running locally.
    Returns WAV audio bytes to stream back to the caller.
    """
    voice = _get_piper_voice()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_file:
        voice.synthesize(text, wav_file)
    return buf.getvalue()
