from vision.ocr import detect_tesseract_cmd


def test_detect_tesseract_cmd():
    # This test simply runs detection; it may return None on CI but must not raise
    _ = detect_tesseract_cmd()
    assert True
