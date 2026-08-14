"""
Run a plugin script in a separate process and communicate via JSON on stdin/stdout.

The plugin entrypoint should accept a `--run` flag and read a JSON object from stdin
and write a JSON object to stdout. This keeps the protocol simple and language-agnostic.
"""
from __future__ import annotations

import subprocess
import json
import sys
from pathlib import Path
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def run_plugin_process(entrypoint: Path, input_payload: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
    """Run the plugin and return parsed JSON output. Raises on errors or invalid JSON."""
    python = sys.executable
    cmd = [python, str(entrypoint), '--run']
    try:
        proc = subprocess.run(cmd, input=json.dumps(input_payload).encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        if proc.returncode != 0:
            logger.error('Plugin process failed: %s', proc.stderr.decode('utf-8', errors='replace'))
            raise RuntimeError(f'Plugin exited with code {proc.returncode}: {proc.stderr.decode("utf-8", errors="replace")}')
        out = proc.stdout.decode('utf-8')
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            logger.error('Plugin returned non-JSON output: %s', out[:1000])
            raise
    except subprocess.TimeoutExpired as e:
        logger.exception('Plugin timed out: %s', e)
        raise
