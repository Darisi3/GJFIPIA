# health_check.py
from flask import Blueprint, jsonify
from config import config
import os
import subprocess
import pyodbc

health_bp = Blueprint('health', __name__)

def _check_db():
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 13 for SQL Server}};"
            f"SERVER={config.DB_SERVER};"
            f"DATABASE={config.DB_NAME};"
            f"UID={config.DB_USER};"
            f"PWD={config.DB_PASSWORD};"
            "Trusted_Connection=no;",
            timeout=3
        )
        conn.close()
        return True
    except:  # noqa
        return False

def _check_tesseract():
    return os.path.isfile(config.TESSERACT_PATH)

def _check_playwright():
    try:
        subprocess.run(['playwright', '--version'], check=True, capture_output=True)
        return True
    except:  # noqa
        return False

import shutil

def _check_disk():
    """
    Kthen True nëse ka të paktën 500 MB hapësirë të lirë.
    Funksionon në Windows dhe Linux.
    """
    total, used, free = shutil.disk_usage(config.UPLOAD_FOLDER)
    free_gb = free / (1024**3)
    return free_gb > 0.5

@health_bp.route('/health', methods=['GET'])
def health():
    checks = {
        'database': _check_db(),
        'tesseract': _check_tesseract(),
        'playwright': _check_playwright(),
        'disk_space': _check_disk()
    }
    status = all(checks.values())
    code = 200 if status else 503
    return jsonify(status=status, checks=checks), code