"""
OCR utilities using pytesseract and Pillow. Requires the Tesseract-OCR
executable to be installed on the system. This module attempts to auto-detect
common Windows installation paths and sets pytesseract.pytesseract.tesseract_cmd
if found.

Functions accept either a filesystem path, a PIL Image, or a numpy array as input.
"""
import logging
from typing import Union, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import pytesseract
    from PIL import Image, ImageOps, ImageFilter
    TESS_AVAILABLE = True
except Exception as e:
    pytesseract = None
    Image = None
    ImageOps = None
    ImageFilter = None
    TESS_AVAILABLE = False
    logger.debug("pytesseract/Pillow not available: %s", e)

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except Exception:
    cv2 = None
    np = None
    CV2_AVAILABLE = False


def detect_tesseract_cmd() -> Optional[str]:
    if not TESS_AVAILABLE:
        return None
    # If pytesseract already has cmd set, return it
    try:
        cmd = getattr(pytesseract.pytesseract, 'tesseract_cmd', None)
        if cmd:
            return cmd
    except Exception:
        pass

    # Common Windows install locations
    candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for c in candidates:
        p = Path(c)
        if p.exists():
            try:
                pytesseract.pytesseract.tesseract_cmd = str(p)
                return str(p)
            except Exception:
                pass
    return None


def _to_pil_image(source: Union[str, Path, 'numpy.ndarray', Image.Image]):
    if isinstance(source, (str, Path)):
        return Image.open(str(source))
    if TESS_AVAILABLE and isinstance(source, Image.Image):
        return source
    if CV2_AVAILABLE and np is not None and isinstance(source, np.ndarray):
        # Convert BGR (OpenCV) to RGB
        img = cv2.cvtColor(source, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img)
    raise ValueError("Unsupported image type or missing dependencies")


def preprocess_for_ocr(pil_img: 'Image.Image'):
    # Convert to grayscale, increase contrast, optional denoising
    img = pil_img.convert('L')
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.MedianFilter(size=3))
    return img


def ocr_from_image(source: Union[str, Path, 'numpy.ndarray', Image.Image], lang: str = 'eng') -> str:
    if not TESS_AVAILABLE:
        raise RuntimeError('pytesseract or Pillow is not installed')
    try:
        pil = _to_pil_image(source)
        pre = preprocess_for_ocr(pil)
        text = pytesseract.image_to_string(pre, lang=lang)
        return text.strip()
    except Exception as e:
        logger.exception('OCR failed: %s', e)
        raise