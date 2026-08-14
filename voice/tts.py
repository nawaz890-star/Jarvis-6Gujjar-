"""
TTS implementation preferring Edge TTS (edge-tts package) with a fallback to
Windows SAPI via pywin32.

Note: edge-tts is async and uses Microsoft Edge's online synthesis. It offers
high-quality voices but requires internet. The fallback (SAPI) uses built-in
Windows voices and works offline.

We intentionally avoid pyttsx3 as requested.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try Edge TTS
try:
    import asyncio
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except Exception as e:
    edge_tts = None
    EDGE_TTS_AVAILABLE = False
    logger.debug("edge-tts not available: %s", e)

# Fallback: Windows SAPI via pywin32
try:
    import win32com.client
    SAPI_AVAILABLE = True
except Exception as e:
    win32com = None
    SAPI_AVAILABLE = False
    logger.debug("pywin32 SAPI not available: %s", e)


class EdgeTTS:
    def __init__(self, voice: str = "en-US-JennyNeural"):
        if not EDGE_TTS_AVAILABLE:
            raise RuntimeError("edge-tts is not installed")
        self.voice = voice

    async def _speak_async(self, text: str):
        communicate = edge_tts.Communicate(text, self.voice)
        # stream to stdout in memory and discard; for GUI we would stream to a player
        await communicate.save("_tmp_edge_tts_audio.mp3")
        # Play the MP3 using the default player (synchronous, simple fallback)
        import subprocess
        subprocess.run(["powershell", "-c", "Start-Process -FilePath _tmp_edge_tts_audio.mp3 -WindowStyle Hidden"], check=False)

    def speak(self, text: str):
        try:
            asyncio.run(self._speak_async(text))
        except Exception as e:
            logger.exception("EdgeTTS playback failed: %s", e)
            raise


class SapiTTS:
    def __init__(self):
        if not SAPI_AVAILABLE:
            raise RuntimeError("pywin32 is not installed")
        self.sapi = win32com.client.Dispatch("SAPI.SpVoice")

    def speak(self, text: str):
        try:
            self.sapi.Speak(text)
        except Exception as e:
            logger.exception("SAPI speak failed: %s", e)
            raise