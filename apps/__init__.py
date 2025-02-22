# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
import os  # Adicionado para usar no configure_database

db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    # Adicione 'notifications' à lista de módulos
    for module_name in ('authentication', 'home', 'notifications'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        try:
            db.create_all()
        except Exception as e:

            print('> Error: DBMS Exception: ' + str(e) )

            # fallback to SQLite
            basedir = os.path.abspath(os.path.dirname(__file__))
            app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

            print('> Fallback to SQLite ')
            db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


from apps.authentication.oauth import github_blueprint

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)

    app.register_blueprint(github_blueprint, url_prefix="/login")
    
    register_blueprints(app)
    configure_database(app)
    # No arquivo apps/__init__.py - dentro da função create_app(config)

    # Adicione este trecho antes do return app
    @app.context_processor
    def inject_notification_counts():
        from flask_login import current_user
        if current_user.is_authenticated:
            from apps.models.notification import Notification, NotificationPriority
            # Contar notificações não lidas por prioridade
            unread_urgent = Notification.query.filter_by(
                user_id=current_user.id,
                is_read=False,
                priority=NotificationPriority.URGENT
            ).count()
            
            unread_high = Notification.query.filter_by(
                user_id=current_user.id,
                is_read=False,
                priority=NotificationPriority.HIGH
            ).count()
            
            unread_total = Notification.query.filter_by(
                user_id=current_user.id,
                is_read=False
            ).count()
            
            return {
                'unread_urgent_count': unread_urgent,
                'unread_high_count': unread_high,
                'unread_count': unread_total
            }
        return {}    
    
    return app
    
