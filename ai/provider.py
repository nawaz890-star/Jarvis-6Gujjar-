from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging
from core.config import Config

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    @abstractmethod
    def send_message(self, messages: List[Dict[str, str]]) -> str:
        """Send a list of messages (each a dict with 'role' and 'text') and return assistant reply."""
        raise NotImplementedError

class ProviderManager:
    """Selects and delegates to the configured AI provider. Falls back to local fallback on errors."""
    def __init__(self):
        self.provider = None
        provider_name = getattr(Config, 'AI_PROVIDER', 'local')
        provider_name = provider_name.lower() if isinstance(provider_name, str) else 'local'
        logger.info("Configured AI provider: %s", provider_name)
        if provider_name == 'gemini':
            try:
                from ai.gemini import GeminiProvider
                self.provider = GeminiProvider()
            except Exception as e:
                logger.exception("Failed to initialize Gemini provider: %s", e)
                self.provider = None
        elif provider_name == 'ollama':
            try:
                from ai.ollama import OllamaProvider
                self.provider = OllamaProvider()
            except Exception as e:
                logger.exception("Failed to initialize Ollama provider: %s", e)
                self.provider = None
        else:
            logger.info("No cloud AI provider configured; using local fallback.")
            self.provider = None

    def send(self, messages: List[Dict[str, str]]) -> str:
        if self.provider:
            try:
                return self.provider.send_message(messages)
            except Exception:
                logger.exception("AI provider error; falling back to local response.")
                from ai.fallback import fallback_response
                return fallback_response(messages[-1]['text'] if messages else '')
        else:
            from ai.fallback import fallback_response
            return fallback_response(messages[-1]['text'] if messages else '')
