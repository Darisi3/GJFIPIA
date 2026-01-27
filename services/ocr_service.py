# ocr_service.py - VERSION I KORRIGJUAR
import cv2
import os
import numpy as np
from config import config
from utils.helpers import clean_text

# shmang timeout-in e modelit
os.environ['DISABLE_MODEL_SOURCE_CHECK'] = 'True'
os.environ['OMP_NUM_THREADS'] = '1'  # Ndrysho nga '4' në '1' për të shmangur warning

# ------------------------------------------------------------------
# 1.  PADDLEOCR – drop-in replacement për Tesseract
# ------------------------------------------------------------------
try:
    from paddleocr import PaddleOCR
    print("[OCR] Duke inicializuar PaddleOCR...")
    
    # Inicializo dy instance për gjuhë të ndryshme
    _paddle_eng = PaddleOCR(
        use_angle_cls=True,
        lang='en',
        use_gpu=False,  # Përdor CPU nëse GPU nuk është i disponueshëm
        show_log=False,
        det_db_thresh=0.3,  # Threshold më i ulët për detektim
        det_db_box_thresh=0.3,
        det_db_unclip_ratio=1.5,
        max_text_length=100  # Rrit gjatësinë maksimale të tekstit
    )
    
    _paddle_sqi = PaddleOCR(
        use_angle_cls=True,
        lang='en',  # Përdor anglisht për shqip (nuk ka model shqip)
        use_gpu=False,
        show_log=False,
        det_db_thresh=0.3,
        det_db_box_thresh=0.3,
        det_db_unclip_ratio=1.5,
        max_text_length=100
    )
    
    PADDLE_AVAILABLE = True
    print("[OCR] PaddleOCR u inicializua me sukses!")
except Exception as e:
    print(f"[OCR] PaddleOCR nuk u ngarkua: {e}  – do përdorim Tesseract fallback")
    PADDLE_AVAILABLE = False
    try:
        import pytesseract
        from PIL import Image as PILImage
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
    except Exception as tess_e:
        print(f"[OCR] As Tesseract nuk u ngarkua: {tess_e}")


class OCRService:
    # ---------- preprocessing ----------
    @staticmethod
    def _preprocess_image(image, target_height=2000):
        """
        Përpunon imazhin për OCR me cilësi më të lartë
        """
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Ruaj dimensionet origjinale
            original_height, original_width = gray.shape[:2]
            
            # Rritja e rezolucionit vetëm nëse imazhi është shumë i vogël
            if original_height < 500:
                # Rrit rezolucionin për imazhe të vogla
                scale = 3
                gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            elif original_height < 1000:
                # Rrit pak për imazhe të mesme
                scale = 2
                gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            else:
                # Për imazhe të mëdha, mbaje madhësinë aktuale
                scale = 1
            
            # Rregullo kontrastin me CLAHE
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
            
            # Heq zhurmat
            gray = cv2.medianBlur(gray, 3)
            gray = cv2.bilateralFilter(gray, d=5, sigmaColor=50, sigmaSpace=50)
            
            # Përdor threshold adaptiv për tekst të qartë
            gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
            
            # E bën tekstin më të trashë për detektim më të mirë
            kernel = np.ones((2, 2), np.uint8)
            gray = cv2.dilate(gray, kernel, iterations=1)
            
            return gray, scale
            
        except Exception as e:
            print(f"[OCR] Gabim në preprocessing: {e}")
            return gray, 1

    @staticmethod
    def _text_similarity(text1, text2):
        """
        Llogarit ngjashmërinë midis dy teksteve (0-1)
        """
        try:
            # Heq hapësirat dhe bëj lowercase
            t1 = text1.replace(" ", "").lower()
            t2 = text2.replace(" ", "").lower()
            
            if not t1 or not t2:
                return 0
            
            # Nëse njëri tekst është në tjetrin
            if t1 in t2 or t2 in t1:
                return 0.8
            
            # Përputhje karakteresh
            common_chars = set(t1) & set(t2)
            total_chars = len(set(t1)) + len(set(t2))
            
            if total_chars > 0:
                similarity = (2 * len(common_chars)) / total_chars
                return similarity
            
            return 0
        except Exception as e:
            print(f"[OCR] Gabim në text_similarity: {e}")
            return 0

    # ---------- perform_ocr ----------
    @staticmethod
    def perform_ocr(image_path, language='eng'):
        try:
            if not os.path.exists(image_path):
                return {'success': False, 'error': 'Image path does not exist'}
            
            img = cv2.imread(image_path)
            if img is None:
                return {'success': False, 'error': f'Nuk mund të lexohet imazhi: {image_path}'}
            
            gray, scale = OCRService._preprocess_image(img)
            
            if PADDLE_AVAILABLE:
                # Zgjidh modelin e duhur për gjuhën
                ocr_instance = _paddle_eng if language == 'eng' else _paddle_sqi
                
                # Kryej OCR
                result = ocr_instance.ocr(gray, cls=True, det=True, rec=True)
                
                if not result or not result[0]:
                    return {'success': True, 'text': '', 'confidence': 0, 'language': language}
                
                # Mbledh të gjitha tekstet e njohura
                texts = []
                confidences = []
                
                for line in result[0]:
                    if line and len(line) >= 2:
                        text, conf = line[1]
                        if text and text.strip():
                            texts.append(text.strip())
                            confidences.append(conf)
                
                full_text = " ".join(texts)
                
                # Print për debug (vetëm 100 karaktere të para)
                if full_text:
                    print(f"[OCR] Teksti i lexuar ({len(full_text)} karaktere): {full_text[:100]}...")
                
                avg_conf = sum(confidences) / len(confidences) if confidences else 0
                
                return {
                    'success': True,
                    'text': full_text,
                    'confidence': round(avg_conf * 100, 2),
                    'language': language,
                    'word_count': len(full_text.split())
                }

            # Fallback Tesseract nëse PaddleOCR nuk është i disponueshëm
            if not PADDLE_AVAILABLE:
                try:
                    import pytesseract
                    from PIL import Image as PILImage
                    
                    # Konverto në PIL Image
                    pil_img = PILImage.fromarray(gray)
                    
                    # Konfigurim i përmirësuar për Tesseract
                    custom_config = f'--oem 3 --psm 6 -l {language}'
                    
                    # Lexo tekstin
                    text = pytesseract.image_to_string(pil_img, config=custom_config)
                    text = clean_text(text)
                    
                    # Lexo të dhënat për besueshmëri
                    data = pytesseract.image_to_data(pil_img, config=custom_config, output_type=pytesseract.Output.DICT)
                    confidences = [int(c) for c in data['conf'] if int(c) > 0]
                    avg_conf = sum(confidences) / len(confidences) if confidences else 0
                    
                    return {
                        'success': True,
                        'text': text,
                        'confidence': round(avg_conf, 2),
                        'language': language,
                        'word_count': len(text.split())
                    }
                except Exception as tess_e:
                    return {'success': False, 'error': f'Tesseract error: {tess_e}'}

        except Exception as e:
            print(f"[OCR] perform_ocr error: {e}")
            return {'success': False, 'error': str(e)}

    # ---------- search_text_in_image ----------
    @staticmethod
    def search_text_in_image(image_path, search_text, language='eng'):
        """
        Kërkon për një tekst specifik në imazh dhe kthen bbox
        """
        try:
            if not os.path.exists(image_path):
                return {'success': False, 'error': 'Image path does not exist', 'matches': []}
            
            img = cv2.imread(image_path)
            if img is None:
                return {'success': False, 'error': f'Cannot read image: {image_path}', 'matches': []}
            
            # Përpunimi i imazhit
            gray, scale = OCRService._preprocess_image(img)
            
            matches = []
            
            if PADDLE_AVAILABLE:
                # Zgjidh modelin e duhur
                ocr_instance = _paddle_eng if language == 'eng' else _paddle_sqi
                
                # Kryej OCR me detaje të bbox
                result = ocr_instance.ocr(gray, cls=True, det=True, rec=True)
                
                if not result or not result[0]:
                    print(f"[OCR] Nuk u gjet asnjë tekst në {image_path}")
                    return {'success': True, 'matches': []}
                
                print(f"[OCR] Gjetur {len(result[0])} bbox-e në imazh")
                
                # Përgatit tekstin e kërkuar për krahasim
                search_lower = search_text.lower().strip()
                
                # Kërko për përputhje
                for line in result[0]:
                    if not line or len(line) < 2:
                        continue
                    
                    bbox_coords, (text, confidence) = line
                    
                    if not text or not bbox_coords:
                        continue
                    
                    text_lower = text.lower().strip()
                    
                    # Kontrollo për përputhje të saktë ose të pjesshme
                    if (search_lower in text_lower or 
                        text_lower in search_lower or
                        OCRService._text_similarity(search_lower, text_lower) > 0.6):
                        
                        # Konverto bbox në format të thjeshtë
                        points = np.array(bbox_coords, dtype=np.float32)
                        left = int(points[:, 0].min() / scale)
                        top = int(points[:, 1].min() / scale)
                        right = int(points[:, 0].max() / scale)
                        bottom = int(points[:, 1].max() / scale)
                        
                        # Krijoni bbox të thjeshtë
                        bbox = {
                            'left': left,
                            'top': top,
                            'width': right - left,
                            'height': bottom - top
                        }
                        
                        matches.append({
                            'text': text,
                            'bbox': bbox,
                            'confidence': round(confidence * 100, 2)
                        })
                        
                        print(f"[OCR] Gjetur përputhje: '{text}' me besueshmëri {confidence:.2f}")
                
                print(f"[OCR] Total përputhje për '{search_text}': {len(matches)}")
                return {'success': True, 'matches': matches}
            
            # Fallback për Tesseract
            if not PADDLE_AVAILABLE:
                try:
                    import pytesseract
                    from PIL import Image as PILImage
                    from pytesseract import Output
                    
                    pil_img = PILImage.fromarray(gray)
                    custom_config = f'--oem 3 --psm 6 -l {language}'
                    
                    # Merr të dhëna të detajuara nga Tesseract
                    data = pytesseract.image_to_data(pil_img, config=custom_config, output_type=Output.DICT)
                    
                    search_lower = search_text.lower()
                    
                    # Kërko për fjalët e kërkuara
                    for i in range(len(data['text'])):
                        text = data['text'][i].strip()
                        if not text:
                            continue
                        
                        text_lower = text.lower()
                        
                        if search_lower in text_lower or text_lower in search_lower:
                            # Krijoni bbox
                            bbox = {
                                'left': int(data['left'][i] / scale),
                                'top': int(data['top'][i] / scale),
                                'width': int(data['width'][i] / scale),
                                'height': int(data['height'][i] / scale)
                            }
                            
                            matches.append({
                                'text': text,
                                'bbox': bbox,
                                'confidence': float(data['conf'][i])
                            })
                    
                    return {'success': True, 'matches': matches}
                    
                except Exception as tess_e:
                    return {'success': False, 'error': f'Tesseract error: {tess_e}', 'matches': []}
            
            return {'success': True, 'matches': []}
            
        except Exception as e:
            print(f"[OCR] search_text_in_image error: {e}")
            return {'success': False, 'error': str(e), 'matches': []}

    # ---------- extract_text_with_bbox ----------
    @staticmethod
    def extract_text_with_bbox(image_path, language='eng'):
        """
        Nxjerr të gjithë tekstin me bbox nga imazhi
        """
        try:
            if not os.path.exists(image_path):
                return {'success': False, 'error': 'Image path does not exist'}
            
            img = cv2.imread(image_path)
            if img is None:
                return {'success': False, 'error': 'Cannot read image'}
            
            gray, scale = OCRService._preprocess_image(img)
            
            if PADDLE_AVAILABLE:
                ocr_instance = _paddle_eng if language == 'eng' else _paddle_sqi
                result = ocr_instance.ocr(gray, cls=True, det=True, rec=True)
                
                if not result or not result[0]:
                    return {'success': True, 'text_blocks': []}
                
                text_blocks = []
                for line in result[0]:
                    if not line or len(line) < 2:
                        continue
                    
                    bbox_coords, (text, confidence) = line
                    
                    points = np.array(bbox_coords, dtype=np.float32)
                    left = int(points[:, 0].min() / scale)
                    top = int(points[:, 1].min() / scale)
                    right = int(points[:, 0].max() / scale)
                    bottom = int(points[:, 1].max() / scale)
                    
                    text_blocks.append({
                        'text': text,
                        'bbox': {
                            'left': left,
                            'top': top,
                            'width': right - left,
                            'height': bottom - top
                        },
                        'confidence': round(confidence * 100, 2)
                    })
                
                return {'success': True, 'text_blocks': text_blocks}
            
            return {'success': True, 'text_blocks': []}
            
        except Exception as e:
            print(f"[OCR] extract_text_with_bbox error: {e}")
            return {'success': False, 'error': str(e)}