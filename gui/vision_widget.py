"""
PySide6 vision widget: camera preview, capture, and OCR actions. The widget is
lightweight and relies on vision.camera.CameraManager and vision.ocr functions.

The widget must be created from the main GUI thread and will use signals to
receive frames. If OpenCV or pytesseract are missing, the widget will display
an informative message and disable functionality.
"""
import logging

logger = logging.getLogger(__name__)

try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QMessageBox, QHBoxLayout
    from PySide6.QtGui import QPixmap, QImage
    from PySide6.QtCore import Qt, Slot
except Exception as e:
    raise RuntimeError('PySide6 is required for vision widget: %s' % e)

try:
    from vision.camera import CameraManager, CV2_AVAILABLE
    from vision.ocr import ocr_from_image, detect_tesseract_cmd, TESS_AVAILABLE
    import numpy as np
except Exception:
    CameraManager = None
    CV2_AVAILABLE = False
    ocr_from_image = None
    detect_tesseract_cmd = None
    TESS_AVAILABLE = False
    np = None


class VisionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.camera = None
        self.cam_mgr = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.status = QLabel('Vision: disabled')
        layout.addWidget(self.status)

        self.preview_label = QLabel('Camera preview not started')
        self.preview_label.setFixedSize(320, 240)
        self.preview_label.setStyleSheet('background-color: #111; color: #ddd;')
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label)

        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton('Start Camera')
        self.start_btn.clicked.connect(self.start_camera)
        btn_layout.addWidget(self.start_btn)

        self.capture_btn = QPushButton('Capture')
        self.capture_btn.clicked.connect(self.capture_image)
        self.capture_btn.setEnabled(False)
        btn_layout.addWidget(self.capture_btn)

        self.ocr_btn = QPushButton('OCR')
        self.ocr_btn.clicked.connect(self.perform_ocr)
        self.ocr_btn.setEnabled(False)
        btn_layout.addWidget(self.ocr_btn)

        layout.addLayout(btn_layout)

        self.ocr_text = QTextEdit()
        self.ocr_text.setReadOnly(True)
        layout.addWidget(self.ocr_text)

        self.setLayout(layout)

    @Slot()
    def start_camera(self):
        if not CV2_AVAILABLE:
            QMessageBox.warning(self, 'Missing Dependency', 'OpenCV (cv2) is not installed. Camera disabled.')
            return
        try:
            self.cam_mgr = CameraManager()
            available = CameraManager.list_cameras(max_devices=5)
            if not available:
                QMessageBox.warning(self, 'No Camera', 'No camera devices detected.')
                return
            cam_idx = available[0]
            self.cam_mgr.start_preview(camera_index=cam_idx, frame_callback=self._on_frame)
            self.status.setText(f'Camera started (index {cam_idx})')
            self.capture_btn.setEnabled(True)
            self.ocr_btn.setEnabled(True if TESS_AVAILABLE else False)
        except Exception as e:
            QMessageBox.critical(self, 'Camera Error', str(e))

    def _on_frame(self, frame: 'numpy.ndarray'):
        # called from camera thread; convert to QImage via QPixmap
        try:
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            # convert BGR->RGB
            import cv2
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pix = QPixmap.fromImage(qimg).scaled(self.preview_label.width(), self.preview_label.height(), Qt.KeepAspectRatio)
            # update UI on main thread
            def _upd():
                self.preview_label.setPixmap(pix)
            try:
                self.preview_label.window().windowHandle()  # ensure mainloop exists
            except Exception:
                pass
            self.preview_label.setPixmap(pix)
        except Exception:
            logger.exception('Failed to update preview frame')

    @Slot()
    def capture_image(self):
        if not self.cam_mgr:
            return
        try:
            from pathlib import Path
            out = Path('data') / 'captures'
            out.mkdir(parents=True, exist_ok=True)
            dest = out / f'capture_{int(time.time())}.png'
            frame = self.cam_mgr.capture_image(path=dest)
            self.preview_label.setText(f'Captured to {dest.name}')
            QMessageBox.information(self, 'Captured', f'Image saved to {dest}')
        except Exception as e:
            QMessageBox.critical(self, 'Capture Error', str(e))

    @Slot()
    def perform_ocr(self):
        if not TESS_AVAILABLE:
            QMessageBox.warning(self, 'Missing Dependency', 'pytesseract/Pillow not installed; OCR unavailable.')
            return
        try:
            # Attempt to use latest capture if exists
            import glob
            from pathlib import Path
            captures = list(Path('data') . glob('captures/capture_*.png'))
            if not captures:
                QMessageBox.information(self, 'No Capture', 'No captured image found. Please capture first.')
                return
            latest = max(captures, key=lambda p: p.stat().st_mtime)
            text = ocr_from_image(str(latest))
            self.ocr_text.setPlainText(text)
        except Exception as e:
            QMessageBox.critical(self, 'OCR Error', str(e))
