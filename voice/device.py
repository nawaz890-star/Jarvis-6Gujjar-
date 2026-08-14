"""
Microphone and audio device management using sounddevice.

This module provides a simple MicrophoneManager for listing devices, selecting
default input/output, and testing the microphone by recording a short sample.

Dependencies:
- sounddevice (required for audio I/O)
- numpy (used by sounddevice)

If sounddevice is not available, the module will raise informative errors when
used. The GUI or CLI should catch these and present helpful instructions.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

try:
    import sounddevice as sd
    import numpy as np
except Exception as e:
    sd = None
    np = None
    logger.debug("sounddevice or numpy not available: %s", e)


class MicrophoneManager:
    def __init__(self):
        if sd is None:
            logger.warning("sounddevice not installed. Microphone functionality disabled.")

    def list_devices(self) -> List[Dict[str, Any]]:
        """Return a list of available audio devices (may be empty or raise if sd missing)."""
        if sd is None:
            return []
        devs = sd.query_devices()
        devices = []
        for i, d in enumerate(devs):
            devices.append({
                "index": i,
                "name": d.get('name'),
                "max_input_channels": d.get('max_input_channels'),
                "max_output_channels": d.get('max_output_channels')
            })
        return devices

    def default_input(self):
        if sd is None:
            return None
        try:
            idx = sd.default.device[0]
            return idx
        except Exception:
            return None

    def test_microphone(self, device: int | None = None, duration: float = 2.0, samplerate: int = 16000):
        """Record a short sample from the microphone and return basic stats.

        Returns dict with keys: success(bool), duration(float), rms(float) or error(str).
        """
        if sd is None or np is None:
            return {"success": False, "error": "sounddevice or numpy not installed"}
        try:
            channels = 1
            if device is not None:
                sd.default.device = device
            recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='int16')
            sd.wait()
            arr = np.array(recording, dtype=np.int16)
            # compute RMS
            rms = float(np.sqrt((arr.astype('float32') ** 2).mean()))
            return {"success": True, "duration": duration, "rms": rms}
        except Exception as e:
            return {"success": False, "error": str(e)}