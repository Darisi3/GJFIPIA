from flask import Blueprint, request, jsonify, current_app
from models.image import Image
from models.ocr_result import OCRResult
from app import db
from services.ocr_service import OCRService
from services.image_processor import ImageProcessor
from utils.helpers import save_uploaded_file, get_image_dimensions
import datetime
import os

ocr_bp = Blueprint('ocr', __name__)

@ocr_bp.route('/process', methods=['POST'])
def process_ocr():
    """Process OCR from uploaded image or URL"""
    try:
        data = request.form
        
        # Check if URL provided
        if 'url' in data and data['url']:
            url = data['url']
            language = data.get('language', 'sqi')
            
            # Process from URL
            result = OCRService.process_from_url(url, language)
            
            if not result['success']:
                return jsonify({'error': result['error']}), 400
            
            # Save to database
            image = Image(
                user_id=data.get('user_id', 1),
                source_url=url,
                file_name=url.split('/')[-1],
                file_path=url,
                file_type='url',
                uploaded_at=datetime.datetime.utcnow()
            )
            db.session.add(image)
            db.session.commit()
            
            ocr_result = OCRResult(
                image_id=image.id,
                extracted_text=result['text'],
                confidence_score=result['confidence'],
                language=language
            )
            db.session.add(ocr_result)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'image_id': image.id,
                'ocr_id': ocr_result.id,
                'extracted_text': result['text'],
                'confidence': result['confidence'],
                'word_count': result.get('word_count', 0),
                'language': language
            }), 200
        
        # Check if file uploaded
        elif 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Save file
            file_info = save_uploaded_file(file)
            if not file_info:
                return jsonify({'error': 'Invalid file type'}), 400
            
            filename, filepath = file_info
            
            # Get image dimensions
            width, height = get_image_dimensions(filepath)
            
            # Save image record
            image = Image(
                user_id=data.get('user_id', 1),
                file_name=filename,
                file_path=filepath,
                file_type=filename.split('.')[-1],
                file_size=os.path.getsize(filepath),
                resolution_width=width,
                resolution_height=height
            )
            db.session.add(image)
            db.session.commit()
            
            # Process OCR
            language = data.get('language', 'sqi')
            result = OCRService.perform_ocr(filepath, language)
            
            if not result['success']:
                return jsonify({'error': result['error']}), 400
            
            # Save OCR result
            ocr_result = OCRResult(
                image_id=image.id,
                extracted_text=result['text'],
                confidence_score=result['confidence'],
                language=language
            )
            db.session.add(ocr_result)
            
            # Update image processed timestamp
            image.processed_at = datetime.datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'image_id': image.id,
                'ocr_id': ocr_result.id,
                'extracted_text': result['text'],
                'confidence': result['confidence'],
                'word_count': result.get('word_count', 0),
                'language': language,
                'image_url': f"/static/uploads/{filename}"
            }), 200
        
        else:
            return jsonify({'error': 'No file or URL provided'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ocr_bp.route('/generate-news', methods=['POST'])
def generate_news():
    """Generate newspaper-style image from text"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        # Generate image
        text_data = {
            'title': data.get('title', 'Nga Gazeta Generator'),
            'content': data['text'],
            'date': data.get('date', datetime.datetime.now().strftime('%d %B %Y'))
        }
        
        filename = ImageProcessor.generate_news_image(text_data)
        
        if not filename:
            return jsonify({'error': 'Failed to generate image'}), 500
        
        return jsonify({
            'success': True,
            'image_url': f"/static/uploads/{filename}",
            'download_url': f"/api/v1/download/{filename}"
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ocr_bp.route('/results/<int:image_id>', methods=['GET'])
def get_ocr_result(image_id):
    """Get OCR result by image ID"""
    try:
        ocr_result = OCRResult.query.filter_by(image_id=image_id).first()
        
        if not ocr_result:
            return jsonify({'error': 'OCR result not found'}), 404
        
        return jsonify({
            'success': True,
            'result': ocr_result.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500