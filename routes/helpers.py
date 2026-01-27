import os
import uuid
from PIL import Image as PILImage
from datetime import datetime
from config import config

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    """Generate unique filename to avoid collisions"""
    ext = filename.rsplit('.', 1)[1].lower()
    unique_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{timestamp}_{unique_id}.{ext}"

def save_uploaded_file(file):
    """Save uploaded file to server"""
    if not file or not allowed_file(file.filename):
        return None
    
    filename = generate_unique_filename(file.filename)
    file_path = os.path.join(config.UPLOAD_FOLDER, filename)
    
    try:
        file.save(file_path)
        return filename, file_path
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

def get_image_dimensions(file_path):
    """Get image dimensions"""
    try:
        with PILImage.open(file_path) as img:
            return img.size  # (width, height)
    except Exception as e:
        print(f"Error getting image dimensions: {e}")
        return (0, 0)

def clean_text(text):
    """Clean OCR extracted text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove non-printable characters but keep Albanian characters
    import string
    printable = set(string.printable + 'çëëËÇ')
    text = ''.join(filter(lambda x: x in printable, text))
    
    return text.strip()