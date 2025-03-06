from apps.home import blueprint
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from apps import db
from apps.home.models import Property, PropertyImage, Document, Transaction, Alert
from apps.home.forms import PropertyForm, DocumentForm, PropertyImageForm, TransactionForm, UserProfileForm
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
from flask import render_template, request, jsonify
from apps.notifications.models import Notification, NotificationPriority
from apps.services.notification_service import NotificationService
from apps.authentication.models import Users, UserProfile
from sqlalchemy.sql import func

@blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UserProfileForm()
    
    if form.validate_on_submit():
        user = Users.query.get(current_user.id)
        
        # Processar foto de perfil
        if form.profile_image.data and form.profile_image.data.filename:
            # Criar os diretórios se não existirem
            profile_upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
            os.makedirs(profile_upload_folder, exist_ok=True)
            
            # Salvar o arquivo
            profile_filename = secure_filename(form.profile_image.data.filename)
            unique_filename = f"{uuid.uuid4().hex}_{profile_filename}"
            profile_path = os.path.join(profile_upload_folder, unique_filename)
            form.profile_image.data.save(profile_path)
            
            # Armazenar o caminho relativo à pasta static
            user.profile_image = f"uploads/profiles/{unique_filename}"
            print(f"Caminho da imagem de perfil salvo: {user.profile_image}")
        
        # Processar imagem de capa
        if form.cover_image.data and form.cover_image.data.filename:
            # Criar os diretórios se não existirem
            cover_upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'covers')
            os.makedirs(cover_upload_folder, exist_ok=True)
            
            # Salvar o arquivo
            cover_filename = secure_filename(form.cover_image.data.filename)
            unique_filename = f"{uuid.uuid4().hex}_{cover_filename}"
            cover_path = os.path.join(cover_upload_folder, unique_filename)
            form.cover_image.data.save(cover_path)
            
            # Armazenar o caminho relativo à pasta static
            user.cover_image = f"uploads/covers/{unique_filename}"
            print(f"Caminho da imagem de capa salvo: {user.cover_image}")
        
        # Atualizar outros campos
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.phone = form.phone.data
        user.address = form.address.data
        user.city = form.city.data
        user.state = form.state.data
        user.zip_code = form.zip_code.data
        
        # Salvar as alterações
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('home_blueprint.profile'))   
    
   # Preencher formulário com dados existentes
    if not form.is_submitted():
        # Adicionar logs para depuração
        print(f"DEBUG - Carregando dados do usuário: {current_user.username}")
        print(f"DEBUG - First name: {getattr(current_user, 'first_name', 'Não definido')}")
        print(f"DEBUG - Last name: {getattr(current_user, 'last_name', 'Não definido')}")
        print(f"DEBUG - Phone: {getattr(current_user, 'phone', 'Não definido')}")
        
        # Buscar o usuário diretamente do banco de dados para garantir dados atualizados
        fresh_user = db.session.query(Users).get(current_user.id)
        
        # Verificar se os atributos existem antes de tentar acessá-los
        form.first_name.data = getattr(fresh_user, 'first_name', '')
        form.last_name.data = getattr(fresh_user, 'last_name', '')
        form.phone.data = getattr(fresh_user, 'phone', '')
        form.address.data = getattr(fresh_user, 'address', '')
        form.city.data = getattr(fresh_user, 'city', '')
        form.state.data = getattr(fresh_user, 'state', '')
        form.zip_code.data = getattr(fresh_user, 'zip_code', '')
        
        # Mais logs para confirmar quais valores foram carregados
        print(f"DEBUG - Formulário preenchido - Nome: {form.first_name.data}")
        print(f"DEBUG - Formulário preenchido - Sobrenome: {form.last_name.data}")
        print(f"DEBUG - Formulário preenchido - Telefone: {form.phone.data}")

    # Verificar se existem mensagens de erro
    for field, errors in form.errors.items():
        for error in errors:
            print(f"DEBUG - Erro no campo {field}: {error}")

    return render_template(
        'home/profile.html',
        segment='profile',
        form=form
    )

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
    try:
        priority = request.args.get('priority')
        limit = request.args.get('limit', 10, type=int)
        
        # Consultar notificações diretamente usando o modelo
        query = Notification.query.filter_by(user_id=current_user.id)
        
        # Filtrar por prioridade se especificado
        if priority:
            query = query.filter_by(priority=priority)
        
        # Ordenar por data de criação (mais recente primeiro)
        query = query.order_by(Notification.created_at.desc())
        
        # Limitar resultados
        if limit:
            query = query.limit(limit)
        
        # Executar a consulta
        notifications = query.all()
        
        # Serializar para JSON
        result = []
        for n in notifications:
            result.append({
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'priority': n.priority,
                'category': getattr(n, 'category', None),
                'created_at': n.created_at.isoformat() if hasattr(n, 'created_at') else None,
                'is_read': getattr(n, 'is_read', False)
            })
        
        return jsonify(result)
    
    except Exception as e:
        # Log detalhado do erro
        print(f"Erro ao obter notificações: {str(e)}")
        # Retornar erro 500 com mensagem
        return jsonify({"error": "Erro ao buscar notificações"}), 500

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
def properties():
    # Obter o parâmetro de status da URL
    status_filter = request.args.get('status', None)
    
    # Consultar propriedades com filtro de status, se fornecido
    if status_filter:
        properties_list = Property.query.filter_by(status=status_filter, parent_property_id=None).order_by(Property.created_at.desc()).all()
    else:
        properties_list = Property.query.filter_by(parent_property_id=None).order_by(Property.created_at.desc()).all()
    
    return render_template('home/properties.html', 
                          properties=properties_list, 
                          active_status=status_filter)

# Adicione esta rota ao arquivo apps/home/routes.py

@blueprint.route('/transactions')
@login_required
def transactions():
    # Buscar todas as transações e ordená-las por data (mais recentes primeiro)
    transactions_list = Transaction.query.order_by(Transaction.date.desc()).all()
    
    # Contar o total de transações para paginação
    total_transactions = Transaction.query.count()
    
    # Buscar todos os imóveis para o modal de adicionar transação
    properties_list = Property.query.filter_by(owner_id=current_user.id).all()
    
    # Inicializar o formulário de transação
    transaction_form = TransactionForm()
    
    return render_template('home/transactions.html',
                           segment='transactions',
                           transactions=transactions_list,
                           total_transactions=total_transactions,
                           properties=properties_list,
                           transaction_form=transaction_form)

# Adicione esta rota para lidar com a adição de transações a partir da página de transações
@blueprint.route('/add-transaction', methods=['POST'])
@login_required
def add_global_transaction():
    form = TransactionForm()
    property_id = request.form.get('property_id')
    
    if form.validate_on_submit() and property_id:
        try:
            # Verificar se o imóvel selecionado existe e pertence ao usuário
            property = Property.query.filter_by(id=property_id, owner_id=current_user.id).first()
            if not property:
                flash('Imóvel não encontrado ou não autorizado.', 'error')
                return redirect(url_for('home_blueprint.transactions'))
            
            # Processar o comprovante se foi enviado
            document = None
            if form.file.data and form.file.data.filename != '':
                file = form.file.data
                if allowed_file(file.filename, {'pdf', 'jpg', 'jpeg', 'png'}):
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
            
            # Criar a transação com os dados do formulário
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
            
            # Adicionar e salvar no banco de dados
            db.session.add(transaction)
            db.session.commit()
            
            flash('Transação adicionada com sucesso!', 'success')
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao adicionar transação: {str(e)}")
            flash(f'Erro ao adicionar transação: {str(e)}', 'error')
    else:
        # Se houver erros no formulário, exibir mensagens
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Erro no campo {getattr(form, field).label.text}: {error}', 'error')
    
    return redirect(url_for('home_blueprint.transactions'))

@blueprint.route('/property/add', methods=['GET', 'POST'])
@login_required
def add_property():
    form = PropertyForm()
    if form.validate_on_submit():
        try:
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
            
            # Registrar ação (opcional)
            print(f"Propriedade criada: ID {property.id} por usuário {current_user.username}")
            
            return redirect(url_for('home_blueprint.properties'))
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao adicionar imóvel: {str(e)}")
            flash('Erro ao adicionar imóvel. Por favor, tente novamente.', 'danger')
    
    # Se houver erros no formulário, mostrar mensagens
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Erro no campo {getattr(form, field).label.text}: {error}', 'danger')
    
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

# Função corrigida para adicionar transações

@blueprint.route('/property/<int:property_id>/add-transaction', methods=['POST'])
@login_required
def add_transaction(property_id):
    property = Property.query.get_or_404(property_id)
    form = TransactionForm()
    
    if form.validate_on_submit():
        try:
            # Primeiro verificar se temos um comprovante
            document = None
            if form.file.data and form.file.data.filename != '':
                file = form.file.data
                if allowed_file(file.filename, {'pdf', 'jpg', 'jpeg', 'png'}):
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
            
            # Criar a transação com os dados do formulário
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
            
            # Adicionar e salvar no banco de dados
            db.session.add(transaction)
            db.session.commit()
            
            flash('Transação adicionada com sucesso!', 'success')
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao adicionar transação: {str(e)}")
            flash(f'Erro ao adicionar transação: {str(e)}', 'error')
    else:
        # Se houver erros no formulário, exibir mensagens
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Erro no campo {getattr(form, field).label.text}: {error}', 'error')
    
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
