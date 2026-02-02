import os
import uuid
import re
from werkzeug.utils import secure_filename
from PIL import Image  # Shtuar për get_image_dimensions

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'tiff', 'bmp'}

def allowed_file(filename):
    """Kontrollon nëse ekstenzioni i file-it është i lejuar"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, upload_folder='uploads'):
    """
    Ruaj një file të ngarkuar dhe kthe path-in e tij
    
    Args:
        file: File object nga request.files
        upload_folder: Folderi ku do ruhet file (default: 'uploads')
    
    Returns:
        str: Path i plotë i file-it të ruajtur, ose None nëse dështon
    """
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    # Krijo folderin uploads nëse nuk ekziston
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Krijo emër unik për file (për të evituar përplasjet)
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    filepath = os.path.join(upload_folder, unique_filename)
    
    # Ruaj file
    file.save(filepath)
    return filepath

def generate_unique_id():
    """Gjeneron një ID unik"""
    return str(uuid.uuid4())

def format_datetime(dt):
    """Formaton datën për shfaqje"""
    if dt:
        return dt.strftime('%d/%m/%Y %H:%M')
    return ''

def clean_text(text):
    """
    Pastron tekstin nga karaktere të panevojshme dhe whitespace.
    
    Args:
        text (str): Teksti për të pastruar
        
    Returns:
        str: Teksti i pastruar
    """
    if not text:
        return ""
    
    # Heq whitespace të tepërt
    text = re.sub(r'\s+', ' ', text)
    
    # Heq newline të tepërt
    text = text.replace('\n\n\n', '\n\n').strip()
    
    # Heq karaktere të kontrollit (jo-printable)
    text = ''.join(char for char in text if char.isprintable() or char in '\n\r\t')
    
    return text

def get_image_dimensions(image_path):
    """
    Kthen dimensionet e një image (width, height).
    
    Args:
        image_path (str): Path i file-it të imazhit
        
    Returns:
        tuple: (width, height) ose (None, None) nëse dështon
    """
    try:
        with Image.open(image_path) as img:
            return img.size  # Kthen (width, height)
    except Exception as e:
        print(f"Error reading image dimensions: {e}")
        return (None, None)