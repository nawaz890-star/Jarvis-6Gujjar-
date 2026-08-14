"""
Wake-word detection using VOSK grammar-based keyword spotting.

This is a lightweight, offline-capable approach: we instantiate a KaldiRecognizer
with a constrained grammar/keyword list to detect the wake word. It's not as
sophisticated as dedicated wake-word engines (Mycroft Precise or Porcupine),
but it's compact and uses the same VOSK model.
"""
import logging
import json

logger = logging.getLogger(__name__)

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except Exception as e:
    Model = None
    KaldiRecognizer = None
    VOSK_AVAILABLE = False
    logger.debug("VOSK not available for wake-word: %s", e)


class WakeWordDetector:
    def __init__(self, model_path: str, wake_word: str = "jarvis", sample_rate: int = 16000):
        if not VOSK_AVAILABLE:
            raise RuntimeError("vosk package not installed")
        self.model = Model(model_path)
        # Use a simple JSON grammar that looks for the wake word
        grammar = f'["{wake_word}"]'
        self.rec = KaldiRecognizer(self.model, sample_rate, grammar)
        self.wake_word = wake_word.lower()

    def is_wake_word(self, pcm_block: bytes) -> bool:
        """Process a chunk of PCM16 audio bytes. Return True if wake word detected."""
        if self.rec.AcceptWaveform(pcm_block):
            try:
                out = json.loads(self.rec.Result())
                text = out.get('text', '').lower()
                return self.wake_word in text
            except Exception as e:
                logger.debug("Wake recognizer result parse error: %s", e)
        else:
            # partial results ignored
            pass
        return False
