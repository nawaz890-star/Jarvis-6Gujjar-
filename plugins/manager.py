"""
Plugin manager: discovers plugins by reading a plugins directory where each plugin
has a manifest JSON file (plugin.json) describing metadata and an entrypoint script.

Plugins are executed in a separate process for isolation. The manager does not
execute arbitrary code in-process.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import sys
from plugins.base import PluginManifest
from plugins.runner import run_plugin_process

logger = logging.getLogger(__name__)

class PluginManager:
    def __init__(self, plugins_dir: Optional[Path] = None):
        if plugins_dir is None:
            self.plugins_dir = Path('plugins')
        else:
            self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, Dict[str, Any]] = {}
        self._load_plugins()

    def _load_plugins(self):
        self.plugins.clear()
        if not self.plugins_dir.exists():
            logger.debug('Plugins directory does not exist: %s', self.plugins_dir)
            return
        for d in self.plugins_dir.iterdir():
            if d.is_dir():
                manifest_path = d / 'plugin.json'
                if manifest_path.exists():
                    try:
                        manifest = PluginManifest.load(manifest_path)
                        self.plugins[manifest.id] = {
                            'manifest': manifest,
                            'path': d,
                            'enabled': True
                        }
                    except Exception:
                        logger.exception('Failed to load plugin manifest: %s', manifest_path)

    def list_plugins(self) -> List[Dict[str, Any]]:
        return [
            {
                'id': pid,
                'name': info['manifest'].name,
                'version': info['manifest'].version,
                'enabled': info['enabled'],
                'description': info['manifest'].description,
                'permissions': info['manifest'].permissions
            }
            for pid, info in self.plugins.items()
        ]

    def enable_plugin(self, plugin_id: str):
        if plugin_id in self.plugins:
            self.plugins[plugin_id]['enabled'] = True

    def disable_plugin(self, plugin_id: str):
        if plugin_id in self.plugins:
            self.plugins[plugin_id]['enabled'] = False

    def run_plugin(self, plugin_id: str, input_payload: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
        if plugin_id not in self.plugins:
            raise ValueError('Unknown plugin id')
        info = self.plugins[plugin_id]
        if not info.get('enabled'):
            raise RuntimeError('Plugin disabled')
        manifest: PluginManifest = info['manifest']
        entry = info['path'] / manifest.entrypoint
        if not entry.exists():
            raise FileNotFoundError(f'Entrypoint not found: {entry}')
        # Run the plugin in a separate process
        result = run_plugin_process(entry, input_payload, timeout=timeout)
        return result
