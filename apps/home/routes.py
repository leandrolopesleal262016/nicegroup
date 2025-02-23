from apps.home import blueprint
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from apps import db
from apps.home.models import Property, PropertyImage, Document, Transaction, Alert
from apps.home.forms import PropertyForm, DocumentForm, PropertyImageForm, TransactionForm
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
from flask import render_template, request, jsonify
from apps.notifications.models import Notification, NotificationPriority
from apps.services.notification_service import NotificationService

# Adicione estas rotas ao arquivo
@blueprint.route('/notificacoes')
@login_required
def notification_center():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    # Agrupar notificações por prioridade para a visualização
    grouped_notifications = {
        'urgent': [],
        'high': [],
        'medium': [],
        'low': []
    }
    
    # Distribuir as notificações nos grupos corretos
    for notification in notifications:
        grouped_notifications[notification.priority].append(notification)
    
    return render_template(
        'home/notifications.html',
        segment='notifications',
        grouped_notifications=grouped_notifications,
        priorities=NotificationPriority
    )

@blueprint.route('/api/notificacoes', methods=['GET'])
@login_required
def get_notifications_api():
    priority = request.args.get('priority')
    limit = request.args.get('limit', 10, type=int)
    
    notifications = NotificationService.get_notifications_by_priority(
        current_user.id, priority, limit
    )
    
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'priority': n.priority,
        'category': n.category,
        'created_at': n.created_at.isoformat(),
        'is_read': n.is_read
    } for n in notifications])

@blueprint.route('/api/notificacoes/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_as_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    # Verificar se a notificação pertence ao usuário atual
    if notification.user_id != current_user.id:
        return jsonify({"error": "Não autorizado"}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({"success": True})

@blueprint.route('/index')
@login_required
def index():
    # Obter estatísticas básicas para o dashboard
    properties_count = Property.query.count()
    rented_count = Property.query.filter_by(status='alugado').count()
    vacant_count = Property.query.filter_by(status='desocupado').count()
    renovation_count = Property.query.filter_by(status='em reforma').count()
    
    # Calcular receitas e despesas totais
    income = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='receita').scalar() or 0
    expenses = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='despesa').scalar() or 0
    balance = income - expenses
    
    # Obter alertas recentes
    recent_alerts = Alert.query.filter_by(user_id=current_user.id, status='não lido').order_by(Alert.created_at.desc()).limit(5).all()
    
    # Obter imóveis recentes
    recent_properties = Property.query.order_by(Property.created_at.desc()).limit(5).all()
    
    return render_template('home/index.html', 
                           segment='index',
                           properties_count=properties_count,
                           rented_count=rented_count,
                           vacant_count=vacant_count,
                           renovation_count=renovation_count,
                           income=income,
                           expenses=expenses,
                           balance=balance,
                           recent_alerts=recent_alerts,
                           properties=recent_properties)

@blueprint.route('/properties')
@login_required
def properties():
    properties = Property.query.filter_by(parent_property_id=None).order_by(Property.created_at.desc()).all()
    return render_template('home/properties.html', 
                           segment='properties',
                           properties=properties)

@blueprint.route('/property/add', methods=['GET', 'POST'])
@login_required
def add_property():
    form = PropertyForm()
    if form.validate_on_submit():
        property = Property(
            address=form.address.data,
            size=form.size.data,
            property_type=form.property_type.data,
            status=form.status.data,
            rent_value=form.rent_value.data,
            iptu=form.iptu.data,
            condominium_fee=form.condominium_fee.data,
            description=form.description.data,
            is_condominium=form.is_condominium.data,
            adjustment_index=form.adjustment_index.data,
            owner_id=current_user.id
        )
        db.session.add(property)
        db.session.commit()
        flash('Imóvel adicionado com sucesso!', 'success')
        return redirect(url_for('home_blueprint.properties'))
    
    return render_template('home/property_form.html',
                           segment='properties',
                           form=form,
                           title='Adicionar Imóvel')

@blueprint.route('/property/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(id):
    property = Property.query.get_or_404(id)
    form = PropertyForm(obj=property)
    
    if form.validate_on_submit():
        form.populate_obj(property)
        db.session.commit()
        flash('Imóvel atualizado com sucesso!', 'success')
        return redirect(url_for('home_blueprint.property_detail', id=property.id))
    
    return render_template('home/property_form.html',
                           segment='properties',
                           form=form,
                           property=property,
                           title='Editar Imóvel')

@blueprint.route('/property/<int:id>')
@login_required
def property_detail(id):
    property = Property.query.get_or_404(id)
    documents = Document.query.filter_by(property_id=property.id).order_by(Document.uploaded_at.desc()).all()
    transactions = Transaction.query.filter_by(property_id=property.id).order_by(Transaction.date.desc()).all()
    alerts = Alert.query.filter_by(property_id=property.id).order_by(Alert.created_at.desc()).all()
    
    # Calcular totais financeiros para o imóvel específico
    total_income = db.session.query(db.func.sum(Transaction.amount)).filter_by(property_id=property.id, type='receita').scalar() or 0
    total_expenses = db.session.query(db.func.sum(Transaction.amount)).filter_by(property_id=property.id, type='despesa').scalar() or 0
    
    # Inicializar formulários para modais
    document_form = DocumentForm()
    transaction_form = TransactionForm()
    
    return render_template('home/property_detail.html',
                           segment='properties',
                           property=property,
                           documents=documents,
                           transactions=transactions,
                           alerts=alerts,
                           total_income=total_income,
                           total_expenses=total_expenses,
                           document_form=document_form,
                           transaction_form=transaction_form)

@blueprint.route('/property/<int:id>/delete', methods=['POST'])
@login_required
def delete_property(id):
    property = Property.query.get_or_404(id)
    
    # Deletar imagens associadas
    for image in property.images:
        try:
            if os.path.exists(os.path.join(current_app.static_folder, image.path)):
                os.remove(os.path.join(current_app.static_folder, image.path))
        except Exception as e:
            current_app.logger.error(f"Erro ao deletar imagem: {str(e)}")
    
    # Deletar documentos associados
    for document in property.documents:
        try:
            if os.path.exists(os.path.join(current_app.static_folder, document.path)):
                os.remove(os.path.join(current_app.static_folder, document.path))
        except Exception as e:
            current_app.logger.error(f"Erro ao deletar documento: {str(e)}")
    
    db.session.delete(property)
    db.session.commit()
    
    flash('Imóvel excluído com sucesso!', 'success')
    return redirect(url_for('home_blueprint.properties'))

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_file(file, folder):
    filename = secure_filename(file.filename)
    # Gerar nome único para evitar conflitos
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(folder, unique_filename)
    
    # Garantir que o diretório exista
    os.makedirs(os.path.join(current_app.static_folder, folder), exist_ok=True)
    
    # Salvar arquivo
    file.save(os.path.join(current_app.static_folder, file_path))
    return file_path

@blueprint.route('/property/<int:property_id>/add-document', methods=['POST'])
@login_required
def add_document(property_id):
    property = Property.query.get_or_404(property_id)
    form = DocumentForm()
    
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename, {'pdf', 'jpg', 'jpeg', 'png'}):
            file_path = save_file(file, 'uploads/documents')
            
            document = Document(
                title=form.title.data,
                filename=file.filename,
                path=file_path,
                document_type=form.document_type.data,
                issue_date=form.issue_date.data,
                expiry_date=form.expiry_date.data,
                description=form.description.data,
                property_id=property.id
            )
            
            db.session.add(document)
            db.session.commit()
            
            flash('Documento adicionado com sucesso!', 'success')
        else:
            flash('Tipo de arquivo não permitido.', 'error')
    
    return redirect(url_for('home_blueprint.property_detail', id=property.id))

@blueprint.route('/property/<int:property_id>/add-image', methods=['POST'])
@login_required
def add_property_image(property_id):
    property = Property.query.get_or_404(property_id)
    form = PropertyImageForm()
    
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename, {'jpg', 'jpeg', 'png'}):
            file_path = save_file(file, 'uploads/properties')
            
            image = PropertyImage(
                filename=file.filename,
                path=file_path,
                description=form.description.data,
                has_issues=form.has_issues.data,
                issue_description=form.issue_description.data if form.has_issues.data else None,
                property_id=property.id
            )
            
            db.session.add(image)
            db.session.commit()
            
            flash('Imagem adicionada com sucesso!', 'success')
        else:
            flash('Tipo de arquivo não permitido.', 'error')
    
    return redirect(url_for('home_blueprint.property_detail', id=property.id))

@blueprint.route('/property/<int:property_id>/add-transaction', methods=['POST'])
@login_required
def add_transaction(property_id):
    property = Property.query.get_or_404(property_id)
    form = TransactionForm()
    
    if form.validate_on_submit():
        # Primeiro verificar se temos um comprovante
        document = None
        if form.file.data:
            file = form.file.data
            if file and allowed_file(file.filename, {'pdf', 'jpg', 'jpeg', 'png'}):
                file_path = save_file(file, 'uploads/receipts')
                
                # Criar documento para o comprovante
                document = Document(
                    title=f"Comprovante - {form.description.data or form.category.data}",
                    filename=file.filename,
                    path=file_path,
                    document_type='comprovante',
                    issue_date=form.date.data,
                    property_id=property.id
                )
                
                db.session.add(document)
                db.session.flush()  # Obter ID sem commit
        
        transaction = Transaction(
            date=form.date.data,
            amount=form.amount.data,
            type=form.type.data,
            category=form.category.data,
            description=form.description.data,
            payment_method=form.payment_method.data,
            status=form.status.data,
            recurrence=form.recurrence.data,
            property_id=property.id,
            document_id=document.id if document else None
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Transação adicionada com sucesso!', 'success')
    
    return redirect(url_for('home_blueprint.property_detail', id=property.id))

@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500

# Helper - Extract current page name from request
def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except:
        return None

def init_notifications(app):
    @app.context_processor
    def inject_notifications():
        from flask_login import current_user
        
        if current_user.is_authenticated:
            notifications = Notification.query.filter_by(
                user_id=current_user.id
            ).order_by(Notification.created_at.desc()).all()
            
            grouped_notifications = {
                'urgent': [],
                'high': [],
                'medium': [],
                'low': []
            }
            
            for notification in notifications:
                grouped_notifications[notification.priority].append(notification)
                
            return {'grouped_notifications': grouped_notifications}
        return {'grouped_notifications': {'urgent': [], 'high': [], 'medium': [], 'low': []}}
