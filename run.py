from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

import logging, os
log_path = os.path.join(os.path.dirname(__file__), 'flask_debug.log')
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)
from paddleocr import PaddleOCR
PaddleOCR(use_angle_cls=True, lang='latin', show_log=True)