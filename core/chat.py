from memory.short_memory import ShortMemory
from ai.provider import ProviderManager
import logging

logger = logging.getLogger(__name__)

class ChatManager:
    """Manages short-term conversation context and delegates to AI provider."""
    def __init__(self, memory_capacity: int = 20):
        self.memory = ShortMemory(capacity=memory_capacity)
        self.provider = ProviderManager()

    def user_message(self, text: str) -> str:
        # Push the user message to short-term memory
        self.memory.push('user', text)
        context = self.memory.get_context()
        # Send to provider
        reply = self.provider.send(context)
        # Save assistant reply
        self.memory.push('assistant', reply)
        logger.debug("User: %s", text)
        logger.debug("Assistant: %s", reply)
        return reply

    def get_context(self):
        return self.memory.get_context()

    def clear_context(self):
        self.memory.clear()