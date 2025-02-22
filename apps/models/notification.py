# apps/models/notification.py
from apps import db
from datetime import datetime

class NotificationPriority:
    LOW = 'baixa'
    MEDIUM = 'média'
    HIGH = 'alta'
    URGENT = 'urgente'

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default=NotificationPriority.MEDIUM)
    category = db.Column(db.String(50))
    related_entity_type = db.Column(db.String(50))  # 'imovel', 'contrato', 'documento', etc
    related_entity_id = db.Column(db.Integer)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Modificando o backref para evitar conflitos
    user = db.relationship('Users', backref=db.backref('user_notifications', lazy=True))