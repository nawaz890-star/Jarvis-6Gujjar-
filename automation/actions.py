"""
Automation actions for Windows: safe wrappers to open apps, URLs, folders, search files,
get system info, volume (optional), lock, shutdown/restart with confirmation.

Dependencies:
- psutil (optional but recommended for system info)
- pycaw/comtypes (optional for volume control)

All destructive actions (shutdown/restart) require explicit confirmation argument.
"""
from __future__ import annotations

import os
import sys
import subprocess
import webbrowser
import platform
import shutil
import logging
from pathlib import Path
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

# Optional dependency: psutil
try:
    import psutil
    PSUTIL_AVAILABLE = True
except Exception as e:
    psutil = None
    PSUTIL_AVAILABLE = False
    logger.debug("psutil not available: %s", e)

# Optional dependency: pycaw for volume control
try:
    from ctypes import POINTER, cast
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCaw_AVAILABLE = True
except Exception as e:
    PYCaw_AVAILABLE = False
    logger.debug("pycaw not available: %s", e)

from utils.safe_run import safe_execute_command


def open_url(url: str) -> Tuple[bool, str]:
    if not url or not isinstance(url, str):
        return False, "Invalid URL"
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "http://" + url
    try:
        webbrowser.open(url)
        return True, f"Opened URL: {url}"
    except Exception as e:
        logger.exception("Failed to open URL: %s", e)
        return False, str(e)


def open_path(path: str) -> Tuple[bool, str]:
    try:
        if not path:
            return False, "No path provided"
        p = Path(path)
        if p.exists():
            os.startfile(str(p))
            return True, f"Opened {path}"
        else:
            return False, f"Path does not exist: {path}"
    except Exception as e:
        logger.exception("Failed to open path: %s", e)
        return False, str(e)


def open_application(name_or_path: str) -> Tuple[bool, str]:
    try:
        if not name_or_path:
            return False, "No application specified"
        # If path provided and exists
        p = Path(name_or_path)
        if p.exists():
            try:
                os.startfile(str(p))
                return True, f"Launched {name_or_path}"
            except Exception:
                # fallback to subprocess
                subprocess.Popen([str(p)])
                return True, f"Launched {name_or_path}"
        # Try to resolve via PATH
        exe = shutil.which(name_or_path)
        if exe:
            subprocess.Popen([exe])
            return True, f"Launched {exe}"
        # Try common Windows program names
        common_paths = [
            r"C:\Program Files\%s" % name_or_path,
            r"C:\Program Files (x86)\%s" % name_or_path,
        ]
        for cp in common_paths:
            if Path(cp).exists():
                os.startfile(cp)
                return True, f"Launched {cp}"
        return False, f"Application not found: {name_or_path}"
    except Exception as e:
        logger.exception("Failed to open application: %s", e)
        return False, str(e)


def search_files(root: str, pattern: str, max_results: int = 50) -> List[str]:
    results: List[str] = []
    try:
        r = Path(root)
        if not r.exists():
            return []
        # simple substring match in filename
        for dirpath, dirnames, filenames in os.walk(r):
            for fn in filenames:
                if pattern.lower() in fn.lower():
                    results.append(str(Path(dirpath) / fn))
                    if len(results) >= max_results:
                        return results
        return results
    except Exception as e:
        logger.exception("search_files error: %s", e)
        return []


def get_system_info() -> dict:
    info = {
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'python_version': platform.python_version(),
    }
    try:
        if PSUTIL_AVAILABLE:
            vm = psutil.virtual_memory()
            info.update({
                'cpu_count': psutil.cpu_count(logical=True),
                'memory_total': vm.total,
                'memory_available': vm.available,
                'boot_time': psutil.boot_time(),
            })
        else:
            info['cpu_count'] = os.cpu_count()
    except Exception as e:
        logger.debug("get_system_info psutil error: %s", e)
    return info


def get_volume() -> Optional[int]:
    if not PYCaw_AVAILABLE:
        raise NotImplementedError("Volume control requires pycaw/comtypes to be installed")
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    # GetMasterVolumeLevelScalar returns 0.0 - 1.0
    level = volume.GetMasterVolumeLevelScalar()
    return int(level * 100)


def set_volume(percent: int) -> None:
    if not PYCaw_AVAILABLE:
        raise NotImplementedError("Volume control requires pycaw/comtypes to be installed")
    if percent < 0 or percent > 100:
        raise ValueError("percent must be between 0 and 100")
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(percent / 100.0, None)


def lock_computer() -> Tuple[bool, str]:
    if platform.system().lower() != 'windows':
        return False, 'Lock not supported on this OS'
    try:
        import ctypes
        ctypes.windll.user32.LockWorkStation()
        return True, 'Locked workstation'
    except Exception as e:
        logger.exception("Failed to lock workstation: %s", e)
        return False, str(e)


def shutdown(confirm: bool = False, delay: int = 0) -> Tuple[bool, str]:
    if not confirm:
        return False, 'Confirmation required to shutdown.'
    try:
        cmd = ['shutdown', '/s', '/t', str(int(delay))]
        safe_execute_command(cmd, timeout=60)
        return True, 'Shutdown initiated'
    except Exception as e:
        logger.exception("Shutdown failed: %s", e)
        return False, str(e)


def restart(confirm: bool = False, delay: int = 0) -> Tuple[bool, str]:
    if not confirm:
        return False, 'Confirmation required to restart.'
    try:
        cmd = ['shutdown', '/r', '/t', str(int(delay))]
        safe_execute_command(cmd, timeout=60)
        return True, 'Restart initiated'
    except Exception as e:
        logger.exception("Restart failed: %s", e)
        return False, str(e)