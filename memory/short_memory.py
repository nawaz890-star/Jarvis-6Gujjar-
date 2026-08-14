from collections import deque

class ShortMemory:
    def __init__(self, capacity=20):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)

    def push(self, role, text):
        self.buffer.append({"role": role, "text": text})

    def get_context(self):
        return list(self.buffer)

    def clear(self):
        self.buffer.clear()
