import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def init_database():
    """Initialize database with PostgreSQL"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Verify connection
        try:
            result = db.session.execute(text('SELECT version()'))
            version = result.scalar()
            print(f"✅ Database connected: {version}")
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
        
        print("✅ Tables created successfully!")
        return True

if __name__ == '__main__':
    init_database()