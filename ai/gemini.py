import logging
import requests
from core.config import Config

logger = logging.getLogger(__name__)

class GeminiProvider:
    """Simple Gemini HTTP provider implementation.

    This implementation is intentionally generic — adapt payload/response parsing
    to your specific Gemini/Vertex AI endpoint schema.
    """
    def __init__(self):
        self.url = getattr(Config, 'GEMINI_API_URL', '')
        self.key = getattr(Config, 'GEMINI_API_KEY', '')
        if not self.url or not self.key:
            logger.warning("GeminiProvider created but URL/key not configured.")
        self.headers = {
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json'
        } if self.key else {}

    def send_message(self, messages, timeout=30):
        if not self.url or not self.key:
            raise RuntimeError("Gemini API not configured")

        # Build a plain text input from the message history. Providers usually
        # accept structured chat messages; adapt as needed.
        composed = []
        for m in messages[-20:]:
            role = m.get('role', 'user')
            text = m.get('text', '')
            composed.append(f"{role}: {text}")
        input_text = "\n".join(composed)

        payload = {
            'model': 'gpt-like-model',
            'input': input_text
        }

        resp = requests.post(self.url, headers=self.headers, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()

        # Generic parsing heuristics (adapt to your provider's response schema)
        if isinstance(data, dict):
            if 'output' in data and isinstance(data['output'], str):
                return data['output']
            if 'choices' in data:
                try:
                    return data['choices'][0]['message']['content']
                except Exception:
                    pass
            if 'responses' in data and isinstance(data['responses'], list):
                first = data['responses'][0]
                if isinstance(first, dict) and 'text' in first:
                    return first['text']
        # Fall back to stringified JSON for debugging
        return str(data)