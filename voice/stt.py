"""
STT adapters. Primary: VOSK (offline). Fallback: SpeechRecognition (online Google STT)

Notes on dependencies and Windows installation:
- VOSK provides offline speech recognition and is the preferred choice for privacy
  and reliability. It requires a downloaded model (see README) which can be large.
- If VOSK wheels are not available for Python 3.12 on your platform, SpeechRecognition
  + PyAudio can be used as a fallback but requires internet for Google's recognizer
  and PyAudio may require additional system installation.
"""
import logging
import json
from typing import Optional

logger = logging.getLogger(__name__)

# Attempt to import VOSK
try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except Exception as e:
    Model = None
    KaldiRecognizer = None
    VOSK_AVAILABLE = False
    logger.debug("VOSK not available: %s", e)

# Fallback: SpeechRecognition (uses Google Web Speech API)
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except Exception as e:
    sr = None
    SR_AVAILABLE = False
    logger.debug("SpeechRecognition not available: %s", e)


class VoskSTT:
    def __init__(self, model_path: str, sample_rate: int = 16000):
        if not VOSK_AVAILABLE:
            raise RuntimeError("vosk package not installed")
        self.model = Model(model_path)
        self.sample_rate = sample_rate
        # A recognizer may be created per stream

    def recognize_buffer(self, data: bytes) -> str:
        """Recognize raw PCM16 audio buffer (mono) and return text."""
        rec = KaldiRecognizer(self.model, self.sample_rate)
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            return res.get('text', '')
        else:
            # Try to return partial result (may be empty)
            try:
                res = json.loads(rec.FinalResult())
                return res.get('text', '')
            except Exception:
                return ""


class SpeechRecognitionSTT:
    def __init__(self):
        if not SR_AVAILABLE:
            raise RuntimeError("speech_recognition package not installed")
        self.rec = sr.Recognizer()

    def recognize_from_microphone(self, timeout: float = 5.0, phrase_time_limit: float = 10.0) -> str:
        with sr.Microphone() as source:
            self.rec.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.rec.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            try:
                text = self.rec.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return ""
            except sr.RequestError as e:
                logger.error("SpeechRecognition request error: %s", e)
                return ""