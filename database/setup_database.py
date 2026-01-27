import pyodbc
import sys
import os

# Shto folderin prind në path për të importuar config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from datetime import datetime
import logging

# Konfiguro logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Klasa për menaxhimin e lidhjeve me databazën"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Krijon lidhjen me databazën"""
        try:
            # Krijoni stringun e lidhjes bazuar në konfigurim
            if config.trusted_connection:
                connection_string = (
                    f"DRIVER={{ODBC Driver 13 for SQL Server}};"
                    f"SERVER={config.DB_SERVER};"
                    f"DATABASE={config.DB_NAME};"
                    f"Trusted_Connection=yes;"
                )
            else:
                connection_string = (
                    f"DRIVER={{ODBC Driver 13 for SQL Server}};"
                    f"SERVER={config.DB_SERVER};"
                    f"DATABASE={config.DB_NAME};"
                    f"UID={config.DB_USER};"
                    f"PWD={config.DB_PASSWORD};"
                )
            
            logger.info(f"Duke u lidhur me {config.DB_SERVER}/{config.DB_NAME}...")
            
            self.connection = pyodbc.connect(connection_string)
            self.cursor = self.connection.cursor()
            
            # Test lidhjen
            self.cursor.execute("SELECT @@VERSION")
            version = self.cursor.fetchone()[0]
            
            logger.info(f"✅ U lidh me sukses me SQL Server")
            logger.info(f"Version: {version[:50]}...")
            
            return True
            
        except pyodbc.Error as e:
            logger.error(f"❌ Gabim në lidhjen me databazën: {e}")
            
            # Sugjerime për zgjidhjen e problemit
            print("\n🔧 PROBLEM NË LIDHJE ME DATABAZËN")
            print("=" * 40)
            print(f"Server: {config.DB_SERVER}")
            print(f"Database: {config.DB_NAME}")
            print(f"Windows Auth: {config.trusted_connection}")
            
            if not config.trusted_connection:
                print(f"User: {config.DB_USER}")
            
            print("\n🔧 KONTROLLONI KËTO:")
            print("1. SQL Server është duke u ekzekutuar")
            print("2. Emri i serverit është i saktë")
            print("3. Databaza 'ocr_db' ekziston")
            print("4. ODBC Driver 13 për SQL Server është instaluar")
            print("5. TCP/IP është aktivizuar në SQL Server Configuration Manager")
            print("6. Kredencialet janë të sakta")
            
            return False
    
    def execute_query(self, query, params=None, fetch=False):
        """Ekzekuton query në databazë"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if fetch:
                # Merr rezultatet si lista dictionaries
                columns = [column[0] for column in self.cursor.description]
                results = []
                for row in self.cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
            else:
                self.connection.commit()
                return self.cursor.rowcount
                
        except pyodbc.Error as e:
            logger.error(f"Gabim në ekzekutimin e query: {e}")
            self.connection.rollback()
            return None
    
    def fetch_one(self, query, params=None):
        """Merr një rresht të vetëm"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            row = self.cursor.fetchone()
            if row:
                columns = [column[0] for column in self.cursor.description]
                return dict(zip(columns, row))
            return None
        except pyodbc.Error as e:
            logger.error(f"Gabim në fetch_one: {e}")
            return None
    
    def close(self):
        """Mbyll lidhjen me databazën"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Lidhja me databazën u mbyll")

# Krijoni instancë globale për lidhje
db = DatabaseConnection()

def init_database():
    """Inicializon lidhjen me databazën"""
    return db.connect()

# Funksione helper për operacione të shpeshta
def get_user_by_email(email):
    """Merr përdoruesin me email"""
    return db.fetch_one("SELECT * FROM users WHERE email = ? AND is_deleted = 0", (email,))

def get_user_by_username(username):
    """Merr përdoruesin me username"""
    return db.fetch_one("SELECT * FROM users WHERE username = ? AND is_deleted = 0", (username,))

def create_user(username, email, password_hash, role_id=3):
    """Krijon përdorues të ri"""
    query = """
        INSERT INTO users (username, email, password, role_id, created_at)
        VALUES (?, ?, ?, ?, GETDATE())
    """
    return db.execute_query(query, (username, email, password_hash, role_id))

def save_ocr_result(image_id, extracted_text, confidence_score, language='sqi'):
    """Ruaj rezultatin OCR në databazë"""
    query = """
        INSERT INTO ocr_results (image_id, extracted_text, confidence_score, language, created_at)
        VALUES (?, ?, ?, ?, GETDATE())
    """
    return db.execute_query(query, (image_id, extracted_text, confidence_score, language))

def get_recent_ocr_results(limit=10):
    """Merr rezultatet e fundit OCR"""
    query = """
        SELECT TOP (?) 
            ocr.id, ocr.extracted_text, ocr.confidence_score, ocr.created_at,
            img.file_name, img.file_path,
            u.username
        FROM ocr_results ocr
        JOIN images img ON ocr.image_id = img.id
        JOIN users u ON img.user_id = u.id
        WHERE ocr.is_deleted = 0
        ORDER BY ocr.created_at DESC
    """
    return db.execute_query(query, (limit,), fetch=True)

def create_audit_log(user_id, action_type, description):
    """Krijon log auditimi"""
    query = """
        INSERT INTO audit_logs (user_id, action_type, description, created_at)
        VALUES (?, ?, ?, GETDATE())
    """
    return db.execute_query(query, (user_id, action_type, description))

if __name__ == "__main__":
    # Testo lidhjen kur ekzekutohet direkt
    print("🔄 Testimi i lidhjes me databazën...")
    if init_database():
        print("✅ Lidhja me databazën funksionon!")
        db.close()
    else:
        print("❌ Lidhja dështoi!")
        sys.exit(1)