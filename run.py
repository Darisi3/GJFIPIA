import os
from app import create_app, db
from flask_migrate import upgrade

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    # Në prod: app.run hiqet, përdoret gunicorn
    app.run(host='0.0.0.0', port=port)