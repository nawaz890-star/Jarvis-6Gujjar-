"""
UI controller that mediates between the core services (ChatManager, CoreApp)
and the GUI layer. It is intentionally GUI-framework-agnostic: it exposes
callback registration methods so the GUI can subscribe to events without
requiring PySide6 in tests or non-GUI environments.
"""
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class UIController:
    def __init__(self, chat_manager=None, max_workers: int = 2):
        # chat_manager expected to implement user_message(text) -> reply
        self.chat_manager = chat_manager
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._on_message_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self._on_status_listeners: List[Callable[[str], None]] = []

    # Listener registration
    def on_message(self, callback: Callable[[Dict[str, Any]], None]):
        self._on_message_listeners.append(callback)

    def on_status(self, callback: Callable[[str], None]):
        self._on_status_listeners.append(callback)

    def _emit_message(self, payload: Dict[str, Any]):
        for cb in list(self._on_message_listeners):
            try:
                cb(payload)
            except Exception:
                logger.exception("Message listener failed")

    def _emit_status(self, text: str):
        for cb in list(self._on_status_listeners):
            try:
                cb(text)
            except Exception:
                logger.exception("Status listener failed")

    def send_user_message(self, text: str):
        """Called by the UI when the user submits a message. This will emit
        an immediate local message event (user bubble), then run the chat
        manager in a background thread and emit the assistant reply when
        available.
        """
        if not text:
            return
        # emit immediate user message
        self._emit_message({"role": "user", "text": text})
        self._emit_status("Thinking...")

        def _work(user_text: str):
            try:
                if self.chat_manager is None:
                    # no AI configured; respond with placeholder
                    reply = "[No chat manager configured]"
                else:
                    reply = self.chat_manager.user_message(user_text)
                # emit assistant message
                self._emit_message({"role": "assistant", "text": reply})
            except Exception as e:
                logger.exception("ChatManager failed: %s", e)
                self._emit_message({"role": "assistant", "text": "[Error: failed to get response]"})
            finally:
                self._emit_status("Idle")

        self.executor.submit(_work, text)

    def shutdown(self):
        self.executor.shutdown(wait=False)
