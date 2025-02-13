# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import Flask, url_for
from importlib import import_module
from apps.extensions import db, init_extensions, login_manager  # Added login_manager import
from apps.tasks import iniciar_agendador
from apps.config.branding import BrandingConfig
from flask_login import current_user
from apps.imoveis.models import UserTheme, Alerta

def register_blueprints(app):
    # Registra autenticação primeiro
    auth = import_module('apps.authentication.routes')
    app.register_blueprint(auth.blueprint)
    
    # Depois os outros blueprints
    home = import_module('apps.home.routes')
    app.register_blueprint(home.blueprint)
    
    from apps.imoveis import blueprint as imoveis_blueprint
    app.register_blueprint(imoveis_blueprint)

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    
    init_extensions(app)
    
    # Configure login manager before blueprints
    login_manager.login_view = 'authentication_blueprint.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    register_blueprints(app)

    @app.context_processor
    def inject_branding():
        from apps.config.branding import BrandingConfig
        branding = BrandingConfig()
        if current_user.is_authenticated:
            theme = UserTheme.query.filter_by(user_id=current_user.id).first()
            if theme:
                branding.PRIMARY_COLOR = theme.primary_color
                branding.SECONDARY_COLOR = theme.secondary_color
                if theme.logo_path:
                    branding.APP_LOGO = url_for('static', filename=f'uploads/logos/{theme.logo_path}')
        return dict(branding=branding)

    @app.context_processor
    def utility_processor():
        notificacoes_nao_lidas = Alerta.query.filter_by(status='pendente').count()
        
        return dict(
            notificacoes_nao_lidas=notificacoes_nao_lidas,
            notificacoes=Alerta.query.filter_by(status='pendente').order_by(Alerta.created_at.desc()).limit(5).all()
        )

    with app.app_context():
        iniciar_agendador()
    
    return app