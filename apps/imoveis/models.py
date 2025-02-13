from apps.extensions import db
from datetime import datetime

class Imovel(db.Model):
    __tablename__ = 'imovel'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True)
    endereco = db.Column(db.String(200))
    status_ocupacao = db.Column(db.String(50))
    valor_aluguel = db.Column(db.Float)
    area = db.Column(db.Float)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    fotos = db.relationship('Foto', backref='imovel', lazy=True)
    alertas = db.relationship('Alerta', backref='imovel', lazy=True)# ... outros modelos ...

class Foto(db.Model):
    __tablename__ = 'foto'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    caminho = db.Column(db.String(200))
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    imovel_id = db.Column(db.Integer, db.ForeignKey('imovel.id'))

class Alerta(db.Model):
    __tablename__ = 'alerta'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))
    descricao = db.Column(db.String(200))
    data_vencimento = db.Column(db.DateTime)
    status = db.Column(db.String(50))
    imovel_id = db.Column(db.Integer, db.ForeignKey('imovel.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
class ConfiguracaoNotificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo_alerta = db.Column(db.String(50))
    email_destinatario = db.Column(db.String(120))
    antecedencia_dias = db.Column(db.Integer)
    ativo = db.Column(db.Boolean, default=True)

class Documento(db.Model):
    __tablename__ = 'documento'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))
    descricao = db.Column(db.String(200))
    data_emissao = db.Column(db.DateTime)
    data_vencimento = db.Column(db.DateTime)
    arquivo = db.Column(db.String(200))
    imovel_id = db.Column(db.Integer, db.ForeignKey('imovel.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    imovel = db.relationship('Imovel', backref='documentos')

class UserTheme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    primary_color = db.Column(db.String(7))
    secondary_color = db.Column(db.String(7))
    logo_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

from apps.extensions import db
from datetime import datetime

# Existing models...

class Financeiro(db.Model):
    __tablename__ = 'financeiro'
    
    id = db.Column(db.Integer, primary_key=True)
    imovel_id = db.Column(db.Integer, db.ForeignKey('imovel.id'))
    tipo = db.Column(db.String(50))  # receita ou despesa
    valor = db.Column(db.Float)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    descricao = db.Column(db.String(200))
    status = db.Column(db.String(50))  # pago, pendente
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
