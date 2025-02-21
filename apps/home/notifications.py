from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from apps import db
from apps.home.models import Alert, Document, Property
from datetime import datetime, timedelta
import json
import os
from pywebpush import webpush, WebPushException

notifications_blueprint = Blueprint(
    'notifications_blueprint',
    __name__,
    url_prefix='/api/notifications'
)

# Endpoint para registrar uma nova inscrição de notificação push
@notifications_blueprint.route('/subscribe', methods=['POST'])
@login_required
def subscribe():
    subscription_info = request.json.get('subscription_info')
    
    if not subscription_info:
        return jsonify({'error': 'Informações de inscrição não fornecidas'}), 400
    
    # Salvar informações de inscrição no banco de dados
    # (Você precisará criar um modelo para armazenar essas informações)
    
    return jsonify({'success': True}), 201

# Função para verificar documentos a expirar
def check_expiring_documents():
    # Documentos que expiram em 30 dias
    thirty_days_ahead = datetime.now().date() + timedelta(days=30)
    expiring_docs = Document.query.filter(Document.expiry_date <= thirty_days_ahead).all()
    
    for doc in expiring_docs:
        # Verificar se já existe um alerta para este documento
        existing_alert = Alert.query.filter_by(
            document_id=doc.id, 
            alert_type='vencimento',
            status='não lido'
        ).first()
        
        if not existing_alert:
            # Criar novo alerta
            property_owner = doc.property.owner
            
            alert = Alert(
                title=f"Documento expirando: {doc.title}",
                message=f"O documento {doc.title} do imóvel {doc.property.address} expira em {(doc.expiry_date - datetime.now().date()).days} dias.",
                alert_type='vencimento',
                due_date=doc.expiry_date,
                property_id=doc.property_id,
                document_id=doc.id,
                user_id=property_owner.id
            )
            
            db.session.add(alert)
            db.session.commit()
            
            # Enviar notificação push para o usuário

# Função para enviar notificação push
def send_push_notification(subscription_info, title, body, url):
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps({
                'title': title,
                'body': body,
                'url': url
            }),
            vapid_private_key=current_app.config.get('VAPID_PRIVATE_KEY'),
            vapid_claims={
                'sub': 'mailto:info@nicegroup.com.br'
            }
        )
        return True
    except WebPushException as e:
        print(f"Erro ao enviar notificação push: {e}")
        return False

# Registrar o blueprint
def init_app(app):
    app.register_blueprint(notifications_blueprint)