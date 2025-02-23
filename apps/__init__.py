# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from sqlalchemy import case
import os

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
            print('> Error: DBMS Exception: ' + str(e))

            # fallback to SQLite
            basedir = os.path.abspath(os.path.dirname(__file__))
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

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

    @app.context_processor
    def inject_notifications():
        from flask_login import current_user
        if current_user.is_authenticated:
            from apps.notifications.models import Notification

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
            
            # Adicionar contagens específicas
            unread_urgent_count = len([n for n in notifications if n.priority == 'urgent' and not n.is_read])
            unread_high_count = len([n for n in notifications if n.priority == 'high' and not n.is_read])
            unread_count = len([n for n in notifications if not n.is_read])
                
            return {
                'grouped_notifications': grouped_notifications,
                'unread_urgent_count': unread_urgent_count,
                'unread_high_count': unread_high_count,
                'unread_count': unread_count
            }
        return {
            'grouped_notifications': {'urgent': [], 'high': [], 'medium': [], 'low': []},
            'unread_urgent_count': 0,
            'unread_high_count': 0,
            'unread_count': 0
        }
    
    return app
