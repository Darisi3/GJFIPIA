import os
from dotenv import load_dotenv

# Load environment variables from .env file (nëse ekziston)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Application Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'gazeta-generator-secret-key-2025')
    
    # Database Configuration - RREGULLIME KRYESORE
    # VENDOS KËTU TË DHËNAT E SAKTA:
    DB_SERVER = os.getenv('DB_SERVER', 'DESKTOP-GU4CRQ7')  # \\ eshte backslash i dyfishte per SQL
    DB_NAME = os.getenv('DB_NAME', 'ocr_db')
    DB_USER = os.getenv('DB_USER', 'sa')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Admin123!')  # Ndrysho me password-in tënd të vërtetë!
    DB_DRIVER = os.getenv('DB_DRIVER', 'ODBC Driver 13 for SQL Server')  # Ose: ODBC Driver 17 for SQL Server
    
    # Trusted Connection (True = Windows Auth, False = SQL Auth me user/pass)
    trusted_connection = True
    
    # Tesseract Configuration
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # API Configuration
    API_PREFIX = '/api/v1'
    
    # SQLAlchemy Configuration (nëse e përdor SQLAlchemy)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        """
        Connection string për SQLAlchemy ORM.
        Shembull: mssql+pyodbc://user:pass@SERVER\INSTANCE/db?driver=...
        """
        driver_encoded = self.DB_DRIVER.replace(' ', '+')
        
        if self.trusted_connection:
            # Windows Authentication
            return (f"mssql+pyodbc://{self.DB_SERVER}/{self.DB_NAME}"
                   f"?driver={driver_encoded}"
                   f"&Trusted_Connection=yes")
        else:
            # SQL Server Authentication (me user/pass)
            return (f"mssql+pyodbc://{self.DB_USER}:{self.DB_PASSWORD}"
                   f"@{self.DB_SERVER}/{self.DB_NAME}"
                   f"?driver={driver_encoded}")

    @property
    def PYODBC_CONNECTION_STRING(self):
        """
        Connection string për pyodbc direkt (përdoret në database/setup_database.py).
        Kthen stringun e gatshëm për pyodbc.connect().
        """
        if self.trusted_connection:
            return (f"DRIVER={{{self.DB_DRIVER}}};"
                   f"SERVER={self.DB_SERVER};"
                   f"DATABASE={self.DB_NAME};"
                   f"Trusted_Connection=yes;")
        else:
            return (f"DRIVER={{{self.DB_DRIVER}}};"
                   f"SERVER={self.DB_SERVER};"
                   f"DATABASE={self.DB_NAME};"
                   f"UID={self.DB_USER};"
                   f"PWD={self.DB_PASSWORD};")

# Create config instance
config = Config()