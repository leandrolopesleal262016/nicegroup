
import os
from .branding import BrandingConfig

class Config(object):
        basedir = os.path.abspath(os.path.dirname(__file__))
    
        # Assets Management
        ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')
    
        # Secret key
        SECRET_KEY = os.getenv('SECRET_KEY', 'S#perS3crEt_007')
    
        # Database
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    
        # Branding
        BRANDING = BrandingConfig

        # Configuração de Upload
        UPLOAD_FOLDER = os.path.join(basedir, '..', 'static', 'uploads', 'logos')
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
class ProductionConfig(Config):
    DEBUG = False
    
    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

class DebugConfig(Config):
    DEBUG = True

# Dicionário de configurações
config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
