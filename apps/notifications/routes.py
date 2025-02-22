# -*- encoding: utf-8 -*-
"""
Rotas para o sistema de notificações
"""

import json
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from flask_login import login_required, current_user
from apps import db
from apps.notifications.models import Notification, NotificationPreference, PushSubscription
from apps.notifications.service import NotificationService

# Criação do blueprint
blueprint = Blueprint(
    'notifications_blueprint',
    __name__,
    url_prefix='/notifications',
    template_folder='templates',
    static_folder='static'
)

# Instância do serviço de notificações
notification_service = None

@blueprint.before_app_first_request
def initialize_service():
    global notification_service
    notification_service = NotificationService(current_app)

# Rotas para o centro de notificações
@blueprint.route('/', methods=['GET'])
@login_required
def notification_center():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    notifications = notification_service.get_user_notifications(
        user_id=current_user.id,
        limit=per_page,
        offset=offset
    )
    
    unread_count = Notification.query.filter_by(
        user_id=current_user.id, 
        read_at=None
    ).count()
    
    return render_template(
        'notifications/index.html',
        segment='notifications',
        notifications=notifications,
        unread_count=unread_count,
        page=page
    )

@blueprint.route('/unread', methods=['GET'])
@login_required
def unread_notifications():
    notifications = notification_service.get_user_notifications(
        user_id=current_user.id,
        unread_only=True,
        limit=10
    )
    
    unread_count = len(notifications)
    
    return render_template(
        'notifications/unread.html',
        segment='notifications',
        notifications=notifications,
        unread_count=unread_count
    )

@blueprint.route('/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_read(notification_id):
    success = notification_service.mark_notification_read(
        notification_id=notification_id,
        user_id=current_user.id
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': success})
    
    return redirect(url_for('notifications_blueprint.notification_center'))

@blueprint.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    count = notification_service.mark_all_read(user_id=current_user.id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'count': count})
    
    return redirect(url_for('notifications_blueprint.notification_center'))

# Rotas para gerenciamento de preferências
@blueprint.route('/preferences', methods=['GET'])
@login_required
def preferences():
    # Obtém as categorias de notificação disponíveis
    notification_types = [
        {'id': 'contract', 'name': 'Contratos', 'description': 'Notificações sobre vencimento e renovação de contratos'},
        {'id': 'document', 'name': 'Documentos', 'description': 'Alertas sobre vencimento de documentos como AVCB, alvarás, etc.'},
        {'id': 'maintenance', 'name': 'Manutenção', 'description': 'Alertas sobre manutenções preventivas e corretivas'},
        {'id': 'financial', 'name': 'Financeiro', 'description': 'Alertas sobre pagamentos, despesas e receitas'},
        {'id': 'property', 'name': 'Imóveis', 'description': 'Notificações sobre status dos imóveis'},
    ]
    
    # Obtém as preferências do usuário para cada categoria
    user_preferences = {}
    for notif_type in notification_types:
        pref = NotificationPreference.query.filter_by(
            user_id=current_user.id,
            notif_type=notif_type['id']
        ).first()
        
        if not pref:
            pref = NotificationPreference(
                user_id=current_user.id,
                notif_type=notif_type['id'],
                push_enabled=True,
                in_app_enabled=True,
                email_enabled=True
            )
            db.session.add(pref)
            db.session.commit()
        
        user_preferences[notif_type['id']] = pref
    
    return render_template(
        'notifications/preferences.html',
        segment='notifications_preferences',
        notification_types=notification_types,
        preferences=user_preferences
    )

@blueprint.route('/preferences/update', methods=['POST'])
@login_required
def update_preferences():
    data = request.form
    notif_type = data.get('notif_type')
    
    if not notif_type:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'Tipo de notificação não especificado'})
        return redirect(url_for('notifications_blueprint.preferences'))
    
    # Atualiza as preferências
    pref = notification_service.update_user_preferences(
        user_id=current_user.id,
        notif_type=notif_type,
        push_enabled='push_enabled' in data,
        in_app_enabled='in_app_enabled' in data,
        email_enabled='email_enabled' in data,
        threshold_days=data.get('threshold_days', type=int)
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    
    return redirect(url_for('notifications_blueprint.preferences'))

# Rotas para gerenciamento de inscrições push
@blueprint.route('/push/public-key', methods=['GET'])
@login_required
def get_push_public_key():
    return jsonify({'publicKey': current_app.config.get('VAPID_PUBLIC_KEY', '')})

@blueprint.route('/push/register', methods=['POST'])
@login_required
def register_push():
    data = request.json
    
    if not data or 'subscription' not in data:
        return jsonify({'success': False, 'error': 'Dados de inscrição ausentes'}), 400
    
    user_agent = request.headers.get('User-Agent')
    
    try:
        subscription = notification_service.register_push_subscription(
            user_id=current_user.id,
            subscription_data=data['subscription'],
            user_agent=user_agent
        )
        
        return jsonify({'success': True, 'id': subscription.id})
    except Exception as e:
        current_app.logger.error(f"Erro ao registrar inscrição push: {str(e)}")
        return jsonify({'success': False, 'error': 'Erro ao registrar inscrição'}), 500

@blueprint.route('/push/unregister', methods=['POST'])
@login_required
def unregister_push():
    data = request.json
    
    if not data or 'endpoint' not in data:
        return jsonify({'success': False, 'error': 'Endpoint ausente'}), 400
    
    subscription = PushSubscription.query.filter_by(
        user_id=current_user.id,
        endpoint=data['endpoint']
    ).first()
    
    if subscription:
        db.session.delete(subscription)
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Inscrição não encontrada'}), 404

# API para obter contagem de notificações não lidas
@blueprint.route('/api/unread-count', methods=['GET'])
@login_required
def api_unread_count():
    count = Notification.query.filter_by(
        user_id=current_user.id, 
        read_at=None
    ).count()
    
    return jsonify({'count': count})

# Endpoint temporário para criar notificações de teste
@blueprint.route('/test-notification', methods=['GET'])
@login_required
def test_notification():
    notification_service.create_notification(
        user_id=current_user.id,
        title="Notificação de Teste",
        message="Esta é uma notificação de teste prioridade alta.",
        notif_type="property",
        priority="urgent"
    )
    return redirect(url_for('notifications_blueprint.notification_center'))

@blueprint.route('/api/unread', methods=['GET'])
@login_required
def api_unread():
    notifications = notification_service.get_user_notifications(
        user_id=current_user.id,
        unread_only=True,
        limit=5
    )
    
    # Converter para formato JSON
    notifications_list = []
    for notif in notifications:
        notifications_list.append({
            'id': notif.id,
            'title': notif.title,
            'message': notif.message,
            'created_at': notif.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
            'notif_type': notif.notif_type,
            'link': notif.link
        })
    
    return jsonify({'notifications': notifications_list})