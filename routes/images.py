from flask import Blueprint, request, jsonify, send_file
from models.image import Image
from models.ocr_result import OCRResult
from app import db
from utils.helpers import save_uploaded_file
import os
from config import config

images_bp = Blueprint('images', __name__)

@images_bp.route('/upload', methods=['POST'])
def upload_image():
    """Upload image file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    file_info = save_uploaded_file(file)
    if not file_info:
        return jsonify({'error': 'File type not allowed'}), 400
    
    filename, filepath = file_info
    
    # Create image record
    image = Image(
        user_id=request.form.get('user_id', 1),
        file_name=filename,
        file_path=filepath,
        file_type=filename.split('.')[-1],
        file_size=os.path.getsize(filepath)
    )
    
    db.session.add(image)
    db.session.commit()
    
    return jsonify({
        'message': 'Image uploaded successfully',
        'image': image.to_dict(),
        'url': f"/static/uploads/{filename}"
    }), 201

@images_bp.route('/list', methods=['GET'])
def list_images():
    """List all images for user"""
    user_id = request.args.get('user_id', 1)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    images = Image.query.filter_by(
        user_id=user_id, 
        is_deleted=False
    ).order_by(Image.uploaded_at.desc()).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'images': [img.to_dict() for img in images.items],
        'total': images.total,
        'pages': images.pages,
        'current_page': page
    }), 200

@images_bp.route('/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """Delete image (soft delete)"""
    image = Image.query.get_or_404(image_id)
    image.is_deleted = True
    db.session.commit()
    
    return jsonify({'message': 'Image deleted successfully'}), 200