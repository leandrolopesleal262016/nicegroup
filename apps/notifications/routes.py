# -*- encoding: utf-8 -*-
# apps/notifications/routes.py
from sqlalchemy import case
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from flask_login import login_required, current_user
from apps import db
from apps.notifications.models import Notification, NotificationPreference, PushSubscription
from apps.services.notification_service import NotificationService
from datetime import datetime

# Criação do blueprint
blueprint = Blueprint(
    'notifications_blueprint',
    __name__,
    url_prefix='/notifications'
)

# Instância do serviço de notificações
notification_service = None

@blueprint.before_app_first_request
def initialize_service():
    global notification_service
    notification_service = NotificationService(current_app)

# ... resto do código ...

# Rotas para o centro de notificações
@blueprint.route('/', methods=['GET'])
@login_required
def notification_center():
    # Buscar todas as notificações
    notifications = Notification.query.filter_by(user_id=current_user.id).all()
    
    # Agrupar notificações por prioridade
    grouped_notifications = {
        'urgent': [],
        'high': [],
        'medium': [],
        'low': []
    }
    
    for notif in notifications:
        if notif.priority in grouped_notifications:
            grouped_notifications[notif.priority].append(notif)
    
    return render_template(
        'notification/index.html',
        segment='notifications',
        grouped_notifications=grouped_notifications
    )


@blueprint.route('/unread', methods=['GET'])
@login_required
def unread_notifications():
    # Buscar notificações não lidas e agrupar por prioridade
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        read_at=None
    ).order_by(
        case(
            {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1, 'normal': 0},
            value=Notification.priority
        ).desc(),
        Notification.created_at.desc()
    ).all()
    
    # Agrupar notificações por prioridade
    grouped_notifications = {
        'urgent': [],
        'high': [],
        'medium': [],
        'low': []
    }
    
    for notif in notifications:
        if notif.priority in grouped_notifications:
            grouped_notifications[notif.priority].append(notif)
    
    unread_count = len(notifications)
    
    return render_template(
        'notification/unread.html',
        segment='notifications',
        grouped_notifications=grouped_notifications,
        unread_count=unread_count
    )

@blueprint.route('/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_read(notification_id):
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first()
    
    if notification:
        notification.read_at = datetime.now()
        db.session.commit()
        success = True
    else:
        success = False
    
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

# Importe o novo modelo
from apps.notifications.models import Notification, NotificationPreference, PushSubscription, NotificationResolution

# Adicione este novo endpoint
@blueprint.route('/resolve/<int:notification_id>', methods=['POST'])
@login_required
def resolve_notification(notification_id):
    """
    Endpoint para marcar uma notificação como resolvida
    """
    data = request.get_json() or {}
    resolution_description = data.get('resolution_description', '')
    
    # Buscar a notificação
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first()
    
    if not notification:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'Notificação não encontrada'}), 404
        return redirect(url_for('notifications_blueprint.notification_center'))
    
    # Verificar se já existe uma resolução
    existing_resolution = NotificationResolution.query.filter_by(
        notification_id=notification_id
    ).first()
    
    if existing_resolution:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'Notificação já resolvida'}), 400
        return redirect(url_for('notifications_blueprint.notification_center'))
    
    # Criar a resolução
    resolution = NotificationResolution(
        notification_id=notification_id,
        user_id=current_user.id,
        resolution_description=resolution_description,
        resolved_at=datetime.now()
    )
    
    # Também marcar como lida, se ainda não estiver
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now()
    
    db.session.add(resolution)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'resolution': {
                'id': resolution.id,
                'notification_id': resolution.notification_id,
                'resolved_by': current_user.username,
                'description': resolution.resolution_description,
                'resolved_at': resolution.resolved_at.strftime('%Y-%m-%dT%H:%M:%S')
            }
        })
    
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
        'notification/preferences.html',
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

# API endpoints
@blueprint.route('/api/unread-count', methods=['GET'])
@login_required
def api_unread_count():
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id, 
        read_at=None
    ).all()
    
    count = len(unread_notifications)
    highest_priority = 'normal'
    
    # Determina a prioridade mais alta entre as notificações não lidas
    priority_order = {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1, 'normal': 0}
    
    if unread_notifications:
        highest_priority = max(
            unread_notifications,
            key=lambda x: priority_order.get(x.priority, 0)
        ).priority
    
    return jsonify({
        'count': count,
        'highest_priority': highest_priority
    })

@blueprint.route('/api/unread', methods=['GET'])
@login_required
def api_unread():
    try:
        notifications = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).order_by(
            case({
                'urgent': 4,
                'high': 3,
                'medium': 2,
                'low': 1
            }, value=Notification.priority),
            Notification.created_at.desc()
        ).limit(5).all()

        notifications_list = []
        for notif in notifications:
            notifications_list.append({
                'id': notif.id,
                'title': notif.title,
                'message': notif.message,
                'created_at': notif.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
                'priority': notif.priority,
                'category': notif.category
            })

        return jsonify({'notifications': notifications_list})
    except Exception as e:
        print(f"Erro ao buscar notificações: {e}")  # Debug
        return jsonify({'error': str(e)}), 500

# Endpoint de teste
@blueprint.route('/test-notification', methods=['GET'])
@login_required
def test_notification():
    priorities = ['urgent', 'high', 'medium', 'low']
    messages = {
        'urgent': 'Esta é uma notificação de teste URGENTE.',
        'high': 'Esta é uma notificação de teste de ALTA prioridade.',
        'medium': 'Esta é uma notificação de teste de MÉDIA prioridade.',
        'low': 'Esta é uma notificação de teste de BAIXA prioridade.'
    }
    
    for priority in priorities:
        notification_service.create_notification(
            user_id=current_user.id,
            title=f"Notificação de Teste ({priority.upper()})",
            message=messages[priority],
            notif_type="property",
            priority=priority
        )
    
    return redirect(url_for('notifications_blueprint.notification_center'))