"""
Camera manager using OpenCV for capturing frames and saving images.

This module provides a CameraManager class that can enumerate cameras, start
and stop a preview loop (calling a user-supplied callback with frames), and
capture a still image. It is designed to be robust when OpenCV is missing:
all methods will raise informative RuntimeError if cv2 is not available.
"""
import threading
import time
import logging
from typing import Callable, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except Exception as e:
    cv2 = None
    np = None
    CV2_AVAILABLE = False
    logger.debug("OpenCV not available: %s", e)


class CameraManager:
    def __init__(self):
        if not CV2_AVAILABLE:
            raise RuntimeError("OpenCV (cv2) is not installed")
        self._cap = None
        self._thread = None
        self._running = threading.Event()
        self._lock = threading.Lock()
        self._latest_frame = None

    @staticmethod
    def list_cameras(max_devices: int = 5):
        if not CV2_AVAILABLE:
            return []
        devices = []
        for idx in range(max_devices):
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if not cap or not cap.isOpened():
                try:
                    cap.release()
                except Exception:
                    pass
                continue
            ret, frame = cap.read()
            if ret:
                devices.append(idx)
            try:
                cap.release()
            except Exception:
                pass
        return devices

    def start_preview(self, camera_index: int = 0, frame_callback: Optional[Callable] = None, width: int = 640, height: int = 480, fps: int = 15):
        if not CV2_AVAILABLE:
            raise RuntimeError("OpenCV (cv2) is not installed")
        if self._running.is_set():
            raise RuntimeError("Preview already running")
        self._cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not self._cap or not self._cap.isOpened():
            raise RuntimeError(f"Could not open camera {camera_index}")
        # Try to set resolution
        try:
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        except Exception:
            pass
        self._running.set()

        def _loop():
            logger.info("Camera preview loop started")
            while self._running.is_set():
                ret, frame = self._cap.read()
                if not ret:
                    time.sleep(0.01)
                    continue
                with self._lock:
                    self._latest_frame = frame
                if frame_callback:
                    try:
                        frame_callback(frame)
                    except Exception:
                        logger.exception("frame_callback raised an exception")
                # throttle
                time.sleep(1.0 / max(1, fps))
            try:
                self._cap.release()
            except Exception:
                pass
            logger.info("Camera preview loop stopped")

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop_preview(self):
        if not CV2_AVAILABLE:
            return
        self._running.clear()
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None
        if self._cap:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None

    def capture_image(self, path: Optional[Path] = None):
        """Capture the latest frame and save to path if provided. Returns a numpy array of the image."""
        if not CV2_AVAILABLE:
            raise RuntimeError("OpenCV (cv2) is not installed")
        with self._lock:
            frame = None if self._latest_frame is None else self._latest_frame.copy()
        if frame is None:
            # try a direct read
            if not self._cap:
                raise RuntimeError("Camera is not running and no frame available")
            ret, frame = self._cap.read()
            if not ret:
                raise RuntimeError("Failed to capture image from camera")
        if path:
            try:
                cv2.imwrite(str(path), frame)
            except Exception as e:
                logger.exception("Failed to write image: %s", e)
                raise
        return frame
