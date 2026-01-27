from app import db
from datetime import datetime

class OCRResult(db.Model):
    __tablename__ = 'ocr_results'
    
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    confidence_score = db.Column(db.Float)
    language = db.Column(db.String(10), default='sqi')  # sqi for Albanian
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'image_id': self.image_id,
            'extracted_text': self.extracted_text[:500] + '...' if len(self.extracted_text) > 500 else self.extracted_text,
            'full_text': self.extracted_text,
            'confidence_score': self.confidence_score,
            'language': self.language,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }