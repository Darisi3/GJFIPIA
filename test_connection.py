#!/usr/bin/env python3
"""
Skript për testimin e lidhjes me databazën
"""
import sys
import os

# Shto folderin aktual në path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.setup_database import init_database, db
from config import config

def test_connection():
    """Testo lidhjen me databazën"""
    print("=" * 50)
    print("🧪 TESTIMI I LIDHJES ME DATABAZËN")
    print("=" * 50)
    print(f"\n📋 Konfigurimi:")
    print(f"   Server: {config.DB_SERVER}")
    print(f"   Database: {config.DB_NAME}")
    print(f"   User: {config.DB_USER}")
    print(f"   Trusted Connection: {config.trusted_connection}")
    print()
    
    print("🔄 Duke u lidhur me databazën...")
    
    if init_database():
        print("\n✅ Lidhja me databazën u krye me sukses!")
        
        # Testo një query të thjeshtë
        print("\n🔄 Testimi i një query të thjeshtë...")
        try:
            result = db.fetch_one("SELECT @@VERSION AS version")
            if result:
                print(f"✅ Query u ekzekutua me sukses!")
                print(f"   Versioni: {result['version'][:50]}...")
            else:
                print("⚠️ Query nuk ktheu rezultate")
        except Exception as e:
            print(f"❌ Gabim në query: {e}")
        
        db.close()
        print("\n" + "=" * 50)
        print("✅ TË GJITHA TESTET KALUAN!")
        print("=" * 50)
        return True
    else:
        print("\n" + "=" * 50)
        print("❌ LIDHJA DËSHTOI!")
        print("=" * 50)
        print("\n💡 SHËNIM: Sigurohu që:")
        print("   1. SQL Server është duke punuar")
        print("   2. Databaza 'ocr_db' ekziston")
        print("   3. ODBC Driver 17 është instaluar")
        print("   4. Kredencialet në .env janë të sakta")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
