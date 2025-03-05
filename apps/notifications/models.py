# -*- encoding: utf-8 -*-
"""
Sistema de notificações - Modelos de dados
"""

from datetime import datetime
from apps import db
from flask_login import UserMixin
from apps.authentication.models import Users

class NotificationPriority:
    URGENT = 'urgent'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'

class NotificationResolution(db.Model):
    """
    Modelo para armazenar informações sobre resoluções de notificações
    """
    __tablename__ = 'notification_resolutions'
    
    id = db.Column(db.Integer, primary_key=True)
    notification_id = db.Column(db.Integer, db.ForeignKey('notifications.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)  # Quem resolveu
    resolution_description = db.Column(db.Text, nullable=True)
    resolved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    notification = db.relationship('Notification', backref=db.backref('resolution', uselist=False, lazy=True))
    resolver = db.relationship('Users', backref=db.backref('resolved_notifications', lazy=True))
    
    def __repr__(self):
        return f"<NotificationResolution {self.id} for notification {self.notification_id}>"


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))  # Changed to match the actual table name
    title = db.Column(db.String(255))
    message = db.Column(db.Text)
    priority = db.Column(db.String(50))
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    
    user = db.relationship('Users', backref=db.backref('user_notifications', lazy=True))
    
    @property
    def formatted_created_at(self):
        """Retorna a data formatada para exibição"""
        return self.created_at.strftime('%d/%m/%Y %H:%M')
    
    def mark_as_read(self):
        """Marca a notificação como lida"""
        self.is_read = True
        db.session.commit()
    
    @staticmethod
    def get_unread_count(user_id):
        """Retorna o número de notificações não lidas para um usuário"""
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()
    
    @staticmethod
    def get_highest_priority(user_id):
        """Retorna a prioridade mais alta entre as notificações não lidas"""
        priorities = {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1, 'normal': 0}
        notifications = Notification.query.filter_by(user_id=user_id, is_read=False).all()
        if not notifications:
            return 'normal'
        return max(notifications, key=lambda x: priorities.get(x.priority, 0)).priority
    
    @property
    def is_resolved(self):
        """Verifica se a notificação foi resolvida"""
        return hasattr(self, 'resolution') and self.resolution is not None
    
    @property
    def resolution_text(self):
        """Retorna a descrição da resolução, se houver"""
        if self.is_resolved:
            return self.resolution.resolution_description
        return None
    
    @property
    def resolved_at_date(self):
        """Retorna a data de resolução, se houver"""
        if self.is_resolved:
            return self.resolution.resolved_at
        return None
        
    def __repr__(self):
        return f"<Notification {self.id}: {self.title}>"

class NotificationPreference(db.Model):
    """
    Modelo para armazenar preferências de notificação do usuário
    """
    __tablename__ = 'notification_preferences'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'notif_type', name='uq_user_notif_type'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    notif_type = db.Column(db.String(50), nullable=False)
    
    # Canais de entrega
    push_enabled = db.Column(db.Boolean, default=True)
    in_app_enabled = db.Column(db.Boolean, default=True)
    email_enabled = db.Column(db.Boolean, default=True)
    
    # Limiares específicos
    threshold_days = db.Column(db.Integer, nullable=True)
    
    # Relacionamentos
    user = db.relationship('Users', backref=db.backref('user_notification_preferences', lazy=True))
    
    def __repr__(self):
        return f"<NotificationPreference {self.user_id}: {self.notif_type}>"

class PushSubscription(db.Model):
    """
    Modelo para armazenar inscrições de notificações push
    """
    __tablename__ = 'push_subscriptions'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'endpoint', name='uq_user_endpoint'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    endpoint = db.Column(db.String(500), nullable=False)
    p256dh = db.Column(db.String(255), nullable=False)
    auth = db.Column(db.String(255), nullable=False)
    user_agent = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    user = db.relationship('Users', backref=db.backref('user_push_subscriptions', lazy=True))
    
    def update_last_used(self):
        """Atualiza a data do último uso"""
        self.last_used = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f"<PushSubscription {self.id}: {self.user_id}>"
