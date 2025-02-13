from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required
from apps.extensions import db
from apps.imoveis.models import Imovel, Alerta, Foto, ConfiguracaoNotificacao, Documento, Financeiro
from sqlalchemy import func
from apps.imoveis import blueprint

@blueprint.route('/')
@login_required
def index():
    imoveis = Imovel.query.all()
    return render_template('imoveis/index.html', imoveis=imoveis)

import os
from werkzeug.utils import secure_filename

@blueprint.route('/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro():
    if request.method == 'POST':
        novo_imovel = Imovel(
            codigo=request.form['codigo'],
            endereco=request.form['endereco'],
            status_ocupacao=request.form['status_ocupacao'],
            valor_aluguel=float(request.form['valor_aluguel']),
            area=float(request.form['area'])
        )
        
        if 'fotos' in request.files:
            fotos = request.files.getlist('fotos')
            for foto in fotos:
                if foto.filename:
                    filename = secure_filename(foto.filename)
                    # Create uploads/imoveis directory if it doesn't exist
                    upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'imoveis')
                    os.makedirs(upload_path, exist_ok=True)
                    # Save the file
                    foto.save(os.path.join(upload_path, filename))
                    nova_foto = Foto(
                        caminho=f'imoveis/{filename}',
                        imovel=novo_imovel
                    )
                    db.session.add(nova_foto)
        
        db.session.add(novo_imovel)
        db.session.commit()
        flash('Imóvel cadastrado com sucesso!', 'success')
        return redirect(url_for('imoveis_blueprint.index'))
        
    return render_template('imoveis/cadastro.html')
@blueprint.route('/detalhes/<int:id>')
@login_required
def detalhes(id):
    imovel = Imovel.query.get_or_404(id)
    return render_template('imoveis/detalhes.html', imovel=imovel)

@blueprint.route('/dashboard')
@login_required
def dashboard():
    # Cálculos das métricas
    total_imoveis = Imovel.query.count()
    imoveis_alugados = Imovel.query.filter_by(status_ocupacao='Alugado').count()
    taxa_ocupacao = (imoveis_alugados / total_imoveis * 100) if total_imoveis > 0 else 0
    
    # Receita total mensal
    receita_mensal = db.session.query(func.sum(Imovel.valor_aluguel))\
        .filter_by(status_ocupacao='Alugado').scalar() or 0
    
    return render_template('imoveis/dashboard.html',
                         total_imoveis=total_imoveis,
                         taxa_ocupacao=taxa_ocupacao,
                         receita_mensal=receita_mensal)

@blueprint.route('/alertas')
@login_required
def alertas():
    alertas_pendentes = Alerta.query.filter_by(status='pendente')\
        .order_by(Alerta.data_vencimento).all()
    return render_template('imoveis/alertas.html', alertas=alertas_pendentes)

@blueprint.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    if request.method == 'POST':
        config = ConfiguracaoNotificacao(
            tipo_alerta=request.form['tipo_alerta'],
            email_destinatario=request.form['email'],
            antecedencia_dias=int(request.form['antecedencia']),
            ativo=True
        )
        db.session.add(config)
        db.session.commit()
        return redirect(url_for('imoveis_blueprint.configuracoes'))
    
    configs = ConfiguracaoNotificacao.query.all()
    return render_template('imoveis/configuracoes.html', configs=configs)

@blueprint.route('/testar-email/<int:config_id>')
@login_required
def testar_email(config_id):
    config = ConfiguracaoNotificacao.query.get_or_404(config_id)
    sucesso, mensagem = enviar_email_teste(config.email_destinatario)
    
    if sucesso:
        flash('Email de teste enviado com sucesso!', 'success')
    else:
        flash(f'Erro ao enviar email: {mensagem}', 'danger')
        
    return redirect(url_for('imoveis_blueprint.configuracoes'))


@blueprint.route('/notificacoes')
@login_required
def todas_notificacoes():
    page = request.args.get('page', 1, type=int)
    notificacoes = Alerta.query\
        .order_by(Alerta.created_at.desc())\
        .paginate(page=page, per_page=20)
    return render_template('imoveis/notificacoes.html', notificacoes=notificacoes)

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from apps.extensions import db
from apps.imoveis.models import UserTheme
from werkzeug.utils import secure_filename
import os

@blueprint.route('/theme-settings', methods=['GET', 'POST'])
@login_required
def theme_settings():
    if request.method == 'POST':
        try:
            theme = UserTheme.query.filter_by(user_id=current_user.id).first()
            if not theme:
                theme = UserTheme(user_id=current_user.id)
            
            theme.primary_color = request.form['primary_color']
            theme.secondary_color = request.form['secondary_color']
            
            if 'logo' in request.files:
                logo = request.files['logo']
                if logo.filename:
                    filename = secure_filename(f"{current_user.id}_{logo.filename}")
                    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'logos')
                    os.makedirs(upload_path, exist_ok=True)
                    logo.save(os.path.join(upload_path, filename))
                    theme.logo_path = filename
            
            db.session.add(theme)
            db.session.commit()
            flash('Configurações atualizadas com sucesso!', 'success')
            return redirect(url_for('imoveis_blueprint.theme_settings'))
            
        except Exception as e:
            flash(f'Erro ao salvar configurações: {str(e)}', 'danger')
            
    theme = UserTheme.query.filter_by(user_id=current_user.id).first()
    return render_template('imoveis/theme_settings.html', theme=theme)
# Rotas para Documentos
@blueprint.route('/documentos')
@login_required
def lista_documentos():
    documentos = Documento.query.all()
    return render_template('imoveis/documentos/lista.html', documentos=documentos)

@blueprint.route('/documentos/upload', methods=['GET', 'POST'])
@login_required
def upload_documento():
    imoveis = Imovel.query.all()
    
    if request.method == 'POST':
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(request.url)
            
        arquivo = request.files['arquivo']
        if arquivo.filename == '':
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(request.url)
            
        if arquivo:
            filename = secure_filename(arquivo.filename)
            upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'documentos')
            os.makedirs(upload_path, exist_ok=True)
            arquivo.save(os.path.join(upload_path, filename))
            
            novo_documento = Documento(
                tipo=request.form['tipo'],
                descricao=request.form['descricao'],
                arquivo=filename,
                imovel_id=request.form['imovel_id'],
                data_emissao=datetime.strptime(request.form['data_emissao'], '%Y-%m-%d'),
                data_vencimento=datetime.strptime(request.form['data_vencimento'], '%Y-%m-%d') if request.form['data_vencimento'] else None
            )
            
            db.session.add(novo_documento)
            db.session.commit()
            
            flash('Documento cadastrado com sucesso!', 'success')
            return redirect(url_for('imoveis_blueprint.lista_documentos'))
            
    return render_template('imoveis/documentos/upload.html', imoveis=imoveis)# Rotas para Financeiro
@blueprint.route('/financeiro/receitas')
@login_required
def receitas():
    receitas = Financeiro.query.filter_by(tipo='receita').all()
    return render_template('imoveis/financeiro/receitas.html', receitas=receitas)

@blueprint.route('/financeiro/despesas')
@login_required
def despesas():
    despesas = Financeiro.query.filter_by(tipo='despesa').all()
    return render_template('imoveis/financeiro/despesas.html', despesas=despesas)

@blueprint.route('/financeiro/relatorios')
@login_required
def relatorios():
    return render_template('imoveis/financeiro/relatorios.html')

@blueprint.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_imovel(id):
    imovel = Imovel.query.get_or_404(id)
    
    # Exclui as fotos do sistema de arquivos
    for foto in imovel.fotos:
        caminho_foto = os.path.join(current_app.root_path, 'static', 'uploads', foto.caminho)
        if os.path.exists(caminho_foto):
            os.remove(caminho_foto)
    
    db.session.delete(imovel)
    db.session.commit()
    
    flash('Imóvel excluído com sucesso!', 'success')
    return redirect(url_for('imoveis_blueprint.index'))
