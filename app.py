import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize extensions outside
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()

def create_app(config_class=None):
    """Application Factory"""
    app = Flask(__name__, static_folder='static', static_url_path='')
    
    # Load config
    if config_class is None:
        from config import Config
        config_class = Config
    app.config.from_object(config_class)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Register blueprints
    register_blueprints(app)
    
    # Create tables if they don't exist (only in dev, prod use migrations)
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables checked/created")
        except Exception as e:
            app.logger.error(f"Database initialization error: {e}")
    
    # Health check route
    @app.route('/health')
    def health_check():
        try:
            db.session.execute('SELECT 1')
            return {'status': 'healthy', 'database': 'connected'}, 200
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}, 500
    
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    return app

def register_blueprints(app):
    """Register all blueprints"""
    try:
        from routes.auth import auth_bp
        from routes.images import images_bp
        from.routes.ocr import ocr_bp
        from routes.search import search_bp
        from routes.download import download_bp
        from routes.health_check import health_bp
        
        app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
        app.register_blueprint(images_bp, url_prefix='/api/v1/images')
        app.register_blueprint(ocr_bp, url_prefix='/api/v1/ocr')
        app.register_blueprint(search_bp, url_prefix='/api/v1/search')
        app.register_blueprint(download_bp, url_prefix='/api/v1/download')
        app.register_blueprint(health_bp, url_prefix='/api/v1/health')
        
    except ImportError as e:
        app.logger.warning(f"Some blueprints not loaded: {e}")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)