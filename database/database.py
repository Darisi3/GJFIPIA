import pyodbc
from config import config

def get_db_connection():
    """Create database connection using pyodbc"""
    connection_string = (
        f'DRIVER={{ODBC Driver 13 for SQL Server}};'
        f'SERVER={config.DB_SERVER};'
        f'DATABASE={config.DB_NAME};'
        f'UID={config.DB_USER};'
        f'PWD={config.DB_PASSWORD};'
        'Trusted_Connection=no;'
    )
    
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    """Execute SQL query"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
        else:
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        print(f"Query execution error: {e}")
        return None
    finally:
        conn.close()