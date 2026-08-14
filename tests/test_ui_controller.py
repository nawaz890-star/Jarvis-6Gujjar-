"""
Basic test for UIController. Uses a fake ChatManager to simulate replies and
ensures that message and status listeners are invoked correctly.
"""
from gui.controllers.ui_controller import UIController

class FakeChatManager:
    def user_message(self, text):
        return f"echo: {text}"


def test_ui_controller_message_flow():
    cm = FakeChatManager()
    controller = UIController(chat_manager=cm)
    messages = []
    statuses = []
    controller.on_message(lambda p: messages.append(p))
    controller.on_status(lambda s: statuses.append(s))

    controller.send_user_message('hello')
    # allow background task to run
    import time
    time.sleep(0.2)
    # There should be at least two messages: user and assistant
    assert len(messages) >= 2
    assert messages[0]['role'] == 'user'
    assert messages[-1]['role'] == 'assistant'
    assert 'echo: hello' in messages[-1]['text']
    assert 'Thinking' in statuses[0] or 'Idle' in statuses[-1]
