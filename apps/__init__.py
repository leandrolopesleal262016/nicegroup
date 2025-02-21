# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from flask_apscheduler import APScheduler

scheduler = APScheduler()

def init_scheduler(app):
    scheduler.init_app(app)
    scheduler.start()
    
    # Agende as tarefas
    from apps.home.notifications import check_expiring_documents
    
    # Verificar documentos expirados todos os dias à meia-noite
    scheduler.add_job(
        id='check_expiring_documents',
        func=check_expiring_documents,
        trigger='cron',
        hour=0,
        minute=0
    )

db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('authentication', 'home'):
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
    init_scheduler(app)  # Adicione esta linha
    return app
