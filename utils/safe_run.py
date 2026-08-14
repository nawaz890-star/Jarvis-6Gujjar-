"""
Safe subprocess execution helpers.

Provide a controlled wrapper around subprocess.run to avoid shell injection and to
centralize timeout/error handling.
"""
from __future__ import annotations

import subprocess
import shlex
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


def safe_execute_command(cmd: List[str], timeout: int = 30) -> Tuple[int, str, str]:
    """Execute a command safely without shell. cmd should be a list of arguments.

    Returns tuple: (returncode, stdout, stderr)
    """
    if not isinstance(cmd, list) or not cmd:
        raise ValueError("cmd must be a non-empty list of arguments")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=False)
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as e:
        logger.exception("Command timeout: %s", e)
        raise
    except Exception as e:
        logger.exception("Command execution failed: %s", e)
        raise