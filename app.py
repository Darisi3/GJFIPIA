# app.py
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config
import os

# Extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5500", "http://127.0.0.1:5500"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Database
    db.init_app(app)
    migrate.init_app(app, db)

    # Upload folder
    if not os.path.exists(config.UPLOAD_FOLDER):
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

    # Blueprints
    from routes.auth import auth_bp
    from routes.images import images_bp
    from routes.ocr import ocr_bp
    from routes.search import search_bp
    from routes.download import download_bp
    from routes.health_check import health_bp  # NEW

    app.register_blueprint(auth_bp, url_prefix=config.API_PREFIX)
    app.register_blueprint(images_bp, url_prefix=config.API_PREFIX)
    app.register_blueprint(ocr_bp, url_prefix=config.API_PREFIX)
    app.register_blueprint(search_bp, url_prefix=config.API_PREFIX)
    app.register_blueprint(download_bp, url_prefix=config.API_PREFIX)
    app.register_blueprint(health_bp)  # NEW – pa prefix, /health

    # Serve static frontend files
    @app.route('/')
    def home():
        return send_from_directory('static', 'index.html')

    @app.route('/about')
    def about():
        return send_from_directory('static', 'about.html')

    @app.route('/login')
    def login():
        return send_from_directory('static', 'login.html')

    @app.route('/register')
    def register():
        return send_from_directory('static', 'register.html')

    # Serve CSS/JS/images
    @app.route('/<path:filename>')
    def static_files(filename):
        return send_from_directory('static', filename)

    # Serve cache screenshots
    @app.route('/static/uploads/cache/<path:filename>')
    def cache_files(filename):
        return send_from_directory(os.path.join(config.UPLOAD_FOLDER, 'cache'), filename)

    # Fallback health (legacy – mbajet për backward compatibility)
    @app.route('/api/health')
    def legacy_health():
        return jsonify({'status': 'healthy', 'database': 'connected'})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)