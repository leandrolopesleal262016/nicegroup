# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from sqlalchemy.orm import relationship
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from apps import db, login_manager
from apps.authentication.util import hash_pass
from sqlalchemy.sql import func

class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True)
    email         = db.Column(db.String(64), unique=True)
    password      = db.Column(db.LargeBinary)
    first_name    = db.Column(db.String(64), nullable=True)
    last_name     = db.Column(db.String(64), nullable=True)
    phone         = db.Column(db.String(20), nullable=True)
    address       = db.Column(db.String(128), nullable=True)
    city          = db.Column(db.String(64), nullable=True)
    state         = db.Column(db.String(2), nullable=True)
    zip_code      = db.Column(db.String(10), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    cover_image   = db.Column(db.String(255), nullable=True)
    oauth_github  = db.Column(db.String(100), nullable=True)
    
    # Método para obter o nome completo
    @property
    def full_name(self):
        profile = UserProfile.query.filter_by(user_id=self.id).first()
        if profile and profile.first_name and profile.last_name:
            return f"{profile.first_name} {profile.last_name}"
        return self.username
    
    # Método para obter o caminho da imagem de perfil
    # @property
    # def profile_image(self):
    #     profile = UserProfile.query.filter_by(user_id=self.id).first()
    #     if profile and profile.profile_image_path:
    #         return profile.profile_image_path
    #     return "/static/assets/img/team/profile-picture-3.jpg"  # Imagem padrão
    
    # # Método para obter o caminho da imagem de capa
    # @property
    # def cover_image(self):
    #     profile = UserProfile.query.filter_by(user_id=self.id).first()
    #     if profile and profile.cover_image_path:
    #         return profile.cover_image_path
    #     return "/static/assets/img/profile-cover.jpg"  # Imagem padrão

class UserProfile(db.Model):
    __tablename__ = 'UserProfiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    zip_code = db.Column(db.String(10))
    profile_image_path = db.Column(db.String(255))
    cover_image_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    user = db.relationship('Users', backref=db.backref('profile', uselist=False))

@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id", ondelete="cascade"), nullable=False)
    user = db.relationship(Users)
