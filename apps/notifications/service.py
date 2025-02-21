# -*- encoding: utf-8 -*-
"""
Serviço para gerenciamento de notificações
"""

import json
import requests
from datetime import datetime
from pywebpush import webpush, WebPushException
from apps import db
from apps.notifications.models import Notification, PushSubscription, NotificationPreference

class NotificationService:
    """
    Serviço para envio e gerenciamento de notificações
    """
    
    def __init__(self, app=None):
        self.app = app
        # Chaves VAPID para notificações push
        self.vapid_private_key = app.config.get('VAPID_PRIVATE_KEY', '')
        self.vapid_public_key = app.config.get('VAPID_PUBLIC_KEY', '')
        self.vapid_claims = {
            "sub": f"mailto:{app.config.get('VAPID_CONTACT_EMAIL', 'admin@example.com')}"
        }
    
    def create_notification(self, user_id, title, message, notif_type, 
                           source_id=None, source_type=None, icon=None, 
                           link=None, priority='normal'):
        """
        Cria uma nova notificação
        """
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notif_type=notif_type,
            source_id=source_id,
            source_type=source_type,
            icon=icon,
            link=link,
            priority=priority
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # Verificar preferências do usuário e enviar por canais habilitados
        self._process_notification_delivery(notification)
        
        return notification
    
    def _process_notification_delivery(self, notification):
        """
        Processa a entrega da notificação com base nas preferências do usuário
        """
        preferences = NotificationPreference.query.filter_by(
            user_id=notification.user_id,
            notif_type=notification.notif_type
        ).first()
        
        # Se não houver preferências específicas, usar valores padrão
        if not preferences:
            preferences = NotificationPreference(
                user_id=notification.user_id,
                notif_type=notification.notif_type,
                push_enabled=True,
                in_app_enabled=True,
                email_enabled=True
            )
            db.session.add(preferences)
            db.session.commit()
        
        # Enviar notificação push se habilitado
        if preferences.push_enabled:
            self._send_push_notification(notification)
        
        # Envio por email será implementado posteriormente
    
    def _send_push_notification(self, notification):
        """
        Envia uma notificação push para todos os dispositivos do usuário
        """
        subscriptions = PushSubscription.query.filter_by(user_id=notification.user_id).all()
        
        if not subscriptions:
            return  # Usuário não tem inscrições push
        
        payload = json.dumps({
            "title": notification.title,
            "body": notification.message,
            "icon": notification.icon,
            "url": notification.link,
            "notificationId": notification.id,
            "priority": notification.priority
        })
        
        for subscription in subscriptions:
            subscription_info = {
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth": subscription.auth
                }
            }
            
            try:
                webpush(
                    subscription_info=subscription_info,
                    data=payload,
                    vapid_private_key=self.vapid_private_key,
                    vapid_claims=self.vapid_claims
                )
                
                # Atualizar última utilização
                subscription.last_used = datetime.utcnow()
                db.session.commit()
                
            except WebPushException as ex:
                # Se a inscrição expirou ou é inválida, remover
                if ex.response and ex.response.status_code in [404, 410]:
                    db.session.delete(subscription)
                    db.session.commit()
                else:
                    # Logar o erro
                    if self.app:
                        self.app.logger.error(f"Push Error: {ex}")
    
    def register_push_subscription(self, user_id, subscription_data, user_agent=None):
        """
        Registra uma nova inscrição push para o usuário
        """
        subscription = PushSubscription(
            user_id=user_id,
            endpoint=subscription_data['endpoint'],
            p256dh=subscription_data['keys']['p256dh'],
            auth=subscription_data['keys']['auth'],
            user_agent=user_agent
        )
        
        try:
            db.session.add(subscription)
            db.session.commit()
            return subscription
        except Exception as e:
            db.session.rollback()
            # Caso já exista, atualizar
            existing = PushSubscription.query.filter_by(
                user_id=user_id,
                endpoint=subscription_data['endpoint']
            ).first()
            
            if existing:
                existing.p256dh = subscription_data['keys']['p256dh']
                existing.auth = subscription_data['keys']['auth']
                existing.user_agent = user_agent
                existing.last_used = datetime.utcnow()
                db.session.commit()
                return existing
            raise e
    
    def get_user_notifications(self, user_id, unread_only=False, limit=20, offset=0):
        """
        Obtém notificações de um usuário
        """
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter(Notification.read_at == None)
        
        query = query.order_by(Notification.created_at.desc())
        
        return query.limit(limit).offset(offset).all()
    
    def mark_notification_read(self, notification_id, user_id):
        """
        Marca uma notificação como lida
        """
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()
        
        if notification:
            notification.read_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def mark_all_read(self, user_id):
        """
        Marca todas as notificações de um usuário como lidas
        """
        unread = Notification.query.filter_by(
            user_id=user_id, 
            read_at=None
        ).all()
        
        now = datetime.utcnow()
        for notification in unread:
            notification.read_at = now
        
        db.session.commit()
        return len(unread)
    
    def update_user_preferences(self, user_id, notif_type, push_enabled=None, 
                               in_app_enabled=None, email_enabled=None, threshold_days=None):
        """
        Atualiza as preferências de notificação de um usuário
        """
        pref = NotificationPreference.query.filter_by(
            user_id=user_id,
            notif_type=notif_type
        ).first()
        
        if not pref:
            pref = NotificationPreference(
                user_id=user_id,
                notif_type=notif_type
            )
            db.session.add(pref)
        
        if push_enabled is not None:
            pref.push_enabled = push_enabled
        
        if in_app_enabled is not None:
            pref.in_app_enabled = in_app_enabled
            
        if email_enabled is not None:
            pref.email_enabled = email_enabled
            
        if threshold_days is not None:
            pref.threshold_days = threshold_days
        
        db.session.commit()
        return pref