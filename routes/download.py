from flask import Blueprint, send_file, jsonify
import os
from config import config

download_bp = Blueprint('download', __name__)

@download_bp.route('/image/<filename>')
def download_image(filename):
    """Download image file"""
    filepath = os.path.join(config.UPLOAD_FOLDER, filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filepath, as_attachment=True)

@download_bp.route('/ocr-text/<int:ocr_id>')
def download_ocr_text(ocr_id):
    """Download OCR text as TXT file"""
    from models.ocr_result import OCRResult
    
    ocr_result = OCRResult.query.get_or_404(ocr_id)
    
    # Create temporary text file
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(ocr_result.extracted_text)
    temp_file.close()
    
    return send_file(
        temp_file.name,
        as_attachment=True,
        download_name=f'ocr_result_{ocr_id}.txt'
    )