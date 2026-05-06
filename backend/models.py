from database import db
from datetime import datetime

class Gift(db.Model):
    __tablename__ = 'gifts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    recipient = db.Column(db.String(50))
    price = db.Column(db.Float, default=0)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    