from dataclasses import dataclass
from typing import List, Dict, Any
import json
from pathlib import Path

@dataclass
class PluginManifest:
    id: str
    name: str
    version: str
    entrypoint: str
    permissions: List[str]
    description: str = ""

    @staticmethod
    def load(path: Path) -> 'PluginManifest':
        with open(path, 'r', encoding='utf-8') as f:
            obj = json.load(f)
        return PluginManifest(
            id=obj['id'],
            name=obj.get('name', obj['id']),
            version=obj.get('version', '0.0.1'),
            entrypoint=obj['entrypoint'],
            permissions=obj.get('permissions', []),
            description=obj.get('description', '')
        )