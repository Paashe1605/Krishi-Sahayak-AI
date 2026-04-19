from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """Simple user model."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Diagnosis(db.Model):
    """Stores the history of crop checks."""
    __tablename__ = 'diagnoses'
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(255), nullable=False)
    user_query = db.Column(db.Text, nullable=True) # Text from voice or typing
    ai_diagnosis = db.Column(db.Text)
    audio_path = db.Column(db.String(255)) # Path to the generated MP3
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # © 2026 Paaras Shemrudkar & Prachi Sharma (Owners of KisanMitra AI). All rights reserved.