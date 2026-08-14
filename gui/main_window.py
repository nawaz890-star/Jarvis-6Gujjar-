"""
PySide6 main window for the JARVIS assistant. This module provides a
lightweight, responsive UI that connects to the UIController (which is
framework-agnostic).

The GUI is deliberately minimal in Phase 7: it provides a chat area, a
microphone button placeholder, status indicators, and a settings button.
Heavy visuals and animations are kept optional to maintain low memory
usage on 8GB systems.

Note: PySide6 must be installed to run this UI. The rest of the project
can be used without the GUI.
"""
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QTextEdit, QLabel, QListWidget, QListWidgetItem, QSplitter,
        QComboBox, QMessageBox
    )
    from PySide6.QtCore import Qt, Slot
except Exception as e:
    raise RuntimeError("PySide6 is required to run the GUI: %s" % e)

from gui.controllers.ui_controller import UIController
from core.chat import ChatManager
from core.app import CoreApp

class MainWindow(QMainWindow):
    def __init__(self, controller: UIController):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('JARVIS — Phase 7 GUI')
        self.setMinimumSize(800, 600)
        self._build_ui()
        # register callbacks
        self.controller.on_message(self._on_message)
        self.controller.on_status(self._on_status)

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        # Top status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel('Status: Idle')
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        self.settings_btn = QPushButton('Settings')
        self.settings_btn.clicked.connect(self._open_settings)
        status_layout.addWidget(self.settings_btn)
        layout.addLayout(status_layout)

        # Main splitter: chat view and right panel
        splitter = QSplitter(Qt.Horizontal)

        # Chat area (left)
        chat_widget = QWidget()
        chat_layout = QVBoxLayout()
        self.chat_list = QListWidget()
        self.chat_list.setAlternatingRowColors(True)
        chat_layout.addWidget(self.chat_list)

        input_layout = QHBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setFixedHeight(60)
        input_layout.addWidget(self.input_text)
        self.send_btn = QPushButton('Send')
        self.send_btn.clicked.connect(self._on_send)
        input_layout.addWidget(self.send_btn)
        chat_layout.addLayout(input_layout)

        chat_widget.setLayout(chat_layout)
        splitter.addWidget(chat_widget)

        # Right panel: voice controls / quick actions
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        self.mic_btn = QPushButton('🎤')
        self.mic_btn.setToolTip('Toggle microphone / push-to-talk (placeholder)')
        right_layout.addWidget(self.mic_btn)
        right_layout.addWidget(QLabel('Quick actions:'))
        self.open_browser_btn = QPushButton('Open Browser')
        self.open_browser_btn.clicked.connect(self._open_browser)
        right_layout.addWidget(self.open_browser_btn)
        right_layout.addStretch()
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        splitter.setSizes([600, 200])
        layout.addWidget(splitter)

        central.setLayout(layout)
        self.setCentralWidget(central)

    @Slot()
    def _on_send(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            return
        self.input_text.clear()
        # send via controller (background)
        self.controller.send_user_message(text)

    def _on_message(self, payload):
        # payload: {role, text}
        role = payload.get('role', 'user')
        text = payload.get('text', '')
        item = QListWidgetItem(f"{role.title()}: {text}")
        self.chat_list.addItem(item)
        # autoscroll
        self.chat_list.scrollToBottom()

    def _on_status(self, text: str):
        self.status_label.setText(f"Status: {text}")

    def _open_settings(self):
        QMessageBox.information(self, 'Settings', 'Settings dialog not implemented yet.')

    def _open_browser(self):
        import webbrowser
        webbrowser.open('https://www.google.com')


def run_gui():
    app = QApplication(sys.argv)
    # wire controller to real ChatManager and CoreApp
    core = CoreApp()
    core.start()
    chat_manager = ChatManager()
    controller = UIController(chat_manager=chat_manager)
    win = MainWindow(controller)
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    run_gui()
