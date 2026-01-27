import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # SQLite Database (file-based)
    DB_PATH = os.getenv('DB_PATH', 'app.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # PaddleOCR Settings
    ENABLE_PADDLE_OCR = True
    PADDLE_OCR_LANG = os.getenv('PADDLE_OCR_LANG', 'en')  # ose 'sq' për shqip (nëse ke modelin)
    
    # Model Cache - Rëndësishëm: Modelet e PaddleOCR janë 100MB+, ruaji në disk të përhershëm
    PADDLE_MODEL_DIR = os.getenv('PADDLE_MODEL_DIR', '/mnt/data/.paddleocr')
    
    # Tesseract (fallback)
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract')
    
    # Uploads
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/mnt/data/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    API_PREFIX = '/api/v1'

config = Config()