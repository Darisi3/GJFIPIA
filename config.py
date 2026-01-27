import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database - PostgreSQL për Render (nuk mund të përdorësh SQL Server local)
    # Render jep DATABASE_URL automatikisht kur krijon PostgreSQL
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Nëse nuk ka DATABASE_URL, përdor parametrat individuale
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'ocr_db')
    
    # SQLAlchemy URI
    if DATABASE_URL:
        # Render e jep këtë si: postgres://user:pass@host/db (duhet converitu në postgresql://)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql://')
    else:
        # Local development
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_pre_ping': True  # Kontrollon lidhjen përpara përdorimit
    }
    
    # Tesseract - Path në Linux (Render/Alpine/Debian)
    # Në Render duhet të instalosh tesseract në build command
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract')
    
    # Uploads - Në Render duhet të përdorësh persistent disk ose S3
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    API_PREFIX = '/api/v1'
    
    # PaddleOCR - Lazy loading sepse është i rëndë
    ENABLE_PADDLE_OCR = os.getenv('ENABLE_PADDLE_OCR', 'False').lower() == 'true'
    
    # Cache
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300

config = Config()