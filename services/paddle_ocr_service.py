# paddle_ocr_service.py
from paddleocr import PaddleOCR
import cv2
import numpy as np

# Inicializo OCR për gjuhët latine (përfshin shqip)
ocr = PaddleOCR(use_angle_cls=True, lang='latin', show_log=False)

def paddle_ocr_image(image_path):
    """
    Kthen tekstin e nxjerrë nga imazhi përmes PaddleOCR
    """
    img = cv2.imread(image_path)
    if img is None:
        return ""

    result = ocr.ocr(img, cls=True)
    text = " ".join([line[1][0] for line in result[0]])
    return text.strip()