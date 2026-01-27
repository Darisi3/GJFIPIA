import os
import logging
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

class PaddleOCRService:
    def __init__(self):
        self.ocr = None
        self.model_dir = os.getenv('PADDLE_MODEL_DIR', '/mnt/data/.paddleocr')
        
    def get_ocr(self):
        """Lazy loading - inicializo vetëm kur të nevojitet"""
        if self.ocr is None:
            try:
                from paddleocr import PaddleOCR
                
                # Krijo direktorinë për modele nëse nuk ekziston
                os.makedirs(self.model_dir, exist_ok=True)
                
                logger.info("Initializing PaddleOCR (first time may take 1-2 minutes)...")
                
                self.ocr = PaddleOCR(
                    use_angle_cls=True,
                    lang='en',  # Ndrysho në 'sq' nëse ke model shqip
                    show_log=False,
                    use_gpu=False,  # CPU only në Render
                    det_model_dir=os.path.join(self.model_dir, 'det'),
                    rec_model_dir=os.path.join(self.model_dir, 'rec'),
                    cls_model_dir=os.path.join(self.model_dir, 'cls')
                )
                logger.info("PaddleOCR initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize PaddleOCR: {e}")
                raise
        return self.ocr
    
    def extract_text(self, image_path):
        """Extract text from image"""
        try:
            ocr = self.get_ocr()
            result = ocr.ocr(image_path, cls=True)
            
            # Parse results
            texts = []
            if result and result[0]:
                for line in result[0]:
                    if line:
                        text = line[1][0]  # Text content
                        confidence = line[1][1]  # Confidence score
                        texts.append({
                            'text': text,
                            'confidence': float(confidence),
                            'box': line[0]
                        })
            
            return {
                'success': True,
                'text': '\n'.join([t['text'] for t in texts]),
                'blocks': texts
            }
        except Exception as e:
            logger.error(f"OCR Error: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': ''
            }

# Singleton instance
paddle_service = PaddleOCRService()