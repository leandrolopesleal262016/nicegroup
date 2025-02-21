# -*- encoding: utf-8 -*-
"""
Sistema de notificações - Modelos de dados
"""

from datetime import datetime
from apps import db
from flask_login import UserMixin
from apps.authentication.models import Users

class Notification(db.Model):
    """
    Modelo para armazenar notificações individuais
    """
    __tablename__ = 'Notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(100), nullable=True)
    link = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    notif_type = db.Column(db.String(50), nullable=False)  # 'contract', 'maintenance', 'document', etc.
    source_id = db.Column(db.Integer, nullable=True)  # ID do recurso relacionado (imóvel, contrato, etc.)
    source_type = db.Column(db.String(50), nullable=True)  # Tipo de recurso ('property', 'contract', etc.)
    priority = db.Column(db.String(20), default='normal')  # 'high', 'normal', 'low'
    
    # Relacionamentos
    user = db.relationship('Users', backref='notifications')
    
    @property
    def is_read(self):
        return self.read_at is not None
    
    def mark_as_read(self):
        self.read_at = datetime.utcnow()
        db.session.commit()
        
    def __repr__(self):
        return f"<Notification {self.id}: {self.title}>"


class NotificationPreference(db.Model):
    """
    Modelo para armazenar preferências de notificação do usuário
    """
    __tablename__ = 'NotificationPreferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    notif_type = db.Column(db.String(50), nullable=False)  # 'contract', 'maintenance', 'document', etc.
    
    # Canais de entrega
    push_enabled = db.Column(db.Boolean, default=True)
    in_app_enabled = db.Column(db.Boolean, default=True)
    email_enabled = db.Column(db.Boolean, default=True)
    
    # Limiares específicos (por exemplo, quantos dias antes de um evento)
    threshold_days = db.Column(db.Integer, nullable=True)
    
    # Relacionamentos
    user = db.relationship('Users', backref='notification_preferences')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'notif_type', name='uq_user_notif_type'),
    )
    
    def __repr__(self):
        return f"<NotificationPreference {self.user_id}: {self.notif_type}>"


class PushSubscription(db.Model):
    """
    Modelo para armazenar inscrições de notificações push (endpoints dos navegadores)
    """
    __tablename__ = 'PushSubscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    endpoint = db.Column(db.String(500), nullable=False)
    p256dh = db.Column(db.String(255), nullable=False)
    auth = db.Column(db.String(255), nullable=False)
    user_agent = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    user = db.relationship('Users', backref='push_subscriptions')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'endpoint', name='uq_user_endpoint'),
    )
    
    def __repr__(self):
        return f"<PushSubscription {self.id}: {self.user_id}>"