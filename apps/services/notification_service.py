# apps/services/notification_service.py
from apps import db
from apps.models.notification import Notification, NotificationPriority
from datetime import datetime, timedelta

class NotificationService:
    @staticmethod
    def create_notification(user_id, title, message, priority=NotificationPriority.MEDIUM, 
                           category=None, related_entity_type=None, related_entity_id=None):
        """
        Cria uma nova notificação
        """
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            priority=priority,
            category=category,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id
        )
        
        db.session.add(notification)
        db.session.commit()
        return notification
    
    @staticmethod
    def get_notifications_by_priority(user_id, priority=None, limit=50):
        """
        Retorna as notificações de um usuário filtradas por prioridade
        """
        query = Notification.query.filter_by(user_id=user_id)
        
        if priority:
            query = query.filter_by(priority=priority)
            
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def determine_priority_for_contract_expiration(days_remaining):
        """
        Determina a prioridade com base no tempo restante para expiração de contratos
        """
        if days_remaining <= 15:
            return NotificationPriority.URGENT
        elif days_remaining <= 30:
            return NotificationPriority.HIGH
        elif days_remaining <= 60:
            return NotificationPriority.MEDIUM
        else:
            return NotificationPriority.LOW
    
    @staticmethod
    def determine_priority_for_document_expiration(days_remaining, document_type):
        """
        Determina a prioridade com base no tempo restante para expiração de documentos
        """
        if document_type in ['AVCB', 'CLB', 'Alvará']:
            # Documentos críticos têm maior prioridade
            if days_remaining <= 15:
                return NotificationPriority.URGENT
            elif days_remaining <= 30:
                return NotificationPriority.HIGH
            else:
                return NotificationPriority.MEDIUM
        else:
            # Documentos regulares
            if days_remaining <= 7:
                return NotificationPriority.HIGH
            elif days_remaining <= 15:
                return NotificationPriority.MEDIUM
            else:
                return NotificationPriority.LOW