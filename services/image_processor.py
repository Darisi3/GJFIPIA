from PIL import Image as PILImage, ImageDraw, ImageFont
import cv2
import numpy as np
import os
from config import config

class ImageProcessor:
    @staticmethod
    def generate_news_image(text_data, template_type='default'):
        """
        Generate newspaper-style image with extracted text
        Args:
            text_data: dict with title, content, date, etc.
            template_type: template style
        Returns:
            path to generated image
        """
        try:
            # Create blank image
            width, height = 1200, 800
            image = PILImage.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)
            
            # Load font (use default or custom)
            try:
                title_font = ImageFont.truetype("arial.ttf", 48)
                content_font = ImageFont.truetype("arial.ttf", 24)
                date_font = ImageFont.truetype("arial.ttf", 18)
            except:
                title_font = ImageFont.load_default()
                content_font = ImageFont.load_default()
                date_font = ImageFont.load_default()
            
            # Draw newspaper elements
            # Header
            draw.rectangle([(0, 0), (width, 100)], fill='#0A2540')
            draw.text((50, 30), "GAZETA GENERATOR", fill='white', font=title_font)
            
            # Title
            title = text_data.get('title', 'LAJM I RËNDËSISHËM')
            draw.text((50, 120), title, fill='black', font=title_font)
            
            # Date
            date = text_data.get('date', '15 Dhjetor 2025')
            draw.text((50, 180), date, fill='gray', font=date_font)
            
            # Content
            content = text_data.get('content', '')
            # Split content into lines
            lines = []
            current_line = ""
            words = content.split()
            
            for word in words:
                test_line = f"{current_line} {word}".strip()
                bbox = draw.textbbox((0, 0), test_line, font=content_font)
                text_width = bbox[2] - bbox[0]
                
                if text_width < width - 100:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            # Draw lines
            y_position = 220
            for line in lines[:15]:  # Limit to 15 lines
                draw.text((50, y_position), line, fill='black', font=content_font)
                y_position += 35
            
            # Footer
            draw.rectangle([(0, height-50), (width, height)], fill='#0A2540')
            draw.text((50, height-35), "www.gazetagenerator.ks", fill='white', font=date_font)
            
            # Save image
            filename = f"generated_{os.urandom(4).hex()}.png"
            filepath = os.path.join(config.UPLOAD_FOLDER, filename)
            image.save(filepath)
            
            return filename
            
        except Exception as e:
            print(f"Image generation error: {e}")
            return None
    
    @staticmethod
    def extract_keyword_highlights(image_path, keyword):
        """
        Highlight keyword occurrences in image
        """
        # This would require more advanced image processing
        # For now, return modified image path
        return image_path