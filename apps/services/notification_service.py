# apps/services/notification_service.py
from sqlalchemy import case
from apps import db
from apps.notifications.models import Notification, NotificationPreference, PushSubscription

class NotificationService:
    """
    Serviço para envio e gerenciamento de notificações
    """
    
    def __init__(self, app=None):
        """
        Inicializa o serviço de notificações
        """
        self.app = app
    
    @staticmethod
    def get_notifications_by_priority(user_id):
        notifications = {
            'urgent': Notification.query.filter_by(user_id=user_id, priority='urgent').order_by(Notification.created_at.desc()).all(),
            'high': Notification.query.filter_by(user_id=user_id, priority='high').order_by(Notification.created_at.desc()).all(),
            'medium': Notification.query.filter_by(user_id=user_id, priority='medium').order_by(Notification.created_at.desc()).all(),
            'low': Notification.query.filter_by(user_id=user_id, priority='low').order_by(Notification.created_at.desc()).all()
        }
        return notifications

    
    def create_notification(self, user_id, title, message, priority='normal',
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
        
        # Verificar preferências do usuário e enviar por canais habilitados
        preferences = NotificationPreference.query.filter_by(
            user_id=user_id,
            notif_type=category if category else 'general'
        ).first()
        
        return notification

    def get_user_notifications(self, user_id, limit=None, offset=0, unread_only=False):
        """
        Obtém notificações de um usuário
        """
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        query = query.order_by(
            case({
                'urgent': 4,
                'high': 3,
                'medium': 2,
                'low': 1
            }, value=Notification.priority),
            Notification.created_at.desc()
        )
        
        if limit:
            query = query.offset(offset).limit(limit)
            
        return query.all()

    def mark_notification_read(self, notification_id, user_id):
        """
        Marca uma notificação como lida
        """
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False

    def mark_all_read(self, user_id):
        """
        Marca todas as notificações de um usuário como lidas
        """
        notifications = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).all()
        
        for notification in notifications:
            notification.is_read = True
        
        db.session.commit()
        return len(notifications)