import logging

logger = logging.getLogger(__name__)

class OllamaProvider:
    """Stub for Ollama local provider.

    Implement this if you choose to run Ollama locally. It's intentionally a
    lightweight stub so the codebase runs without Ollama installed.
    """
    def __init__(self):
        logger.info("OllamaProvider stub initialized. Install and implement if needed.")

    def send_message(self, messages, timeout=30):
        # A simple local echo for now
        last = messages[-1]['text'] if messages else ''
        return f"(local-ollama-stub) I heard: {last[:200]}"