from apps import db
from sqlalchemy.sql import func
from datetime import datetime
from flask_login import UserMixin
from apps.authentication.models import Users

class Property(db.Model):
    __tablename__ = 'Properties'
    
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Float, nullable=False)  # tamanho em m²
    property_type = db.Column(db.String(50), nullable=False)  # casa, apartamento, terreno, etc.
    status = db.Column(db.String(20), nullable=False, default="disponível")  # alugado, desocupado, em reforma
    rent_value = db.Column(db.Float, nullable=True)  # valor de locação
    iptu = db.Column(db.Float, nullable=True)  # valor do IPTU
    condominium_fee = db.Column(db.Float, nullable=True)  # valor do condomínio
    description = db.Column(db.Text, nullable=True)
    is_condominium = db.Column(db.Boolean, default=False)  # se é um condomínio com múltiplas unidades
    parent_property_id = db.Column(db.Integer, db.ForeignKey('Properties.id'), nullable=True)  # para unidades de condomínio
    adjustment_index = db.Column(db.String(10), nullable=True)  # IGPM ou IPCA
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    owner_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    owner = db.relationship('Users', backref='properties')
    documents = db.relationship('Document', backref='property', lazy=True)
    transactions = db.relationship('Transaction', backref='property', lazy=True)
    units = db.relationship('Property', backref=db.backref('parent', remote_side=[id]))
    images = db.relationship('PropertyImage', backref='property', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Property {self.address}>'

class PropertyImage(db.Model):
    __tablename__ = 'PropertyImages'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    has_issues = db.Column(db.Boolean, default=False)  # se tem problemas marcados
    issue_description = db.Column(db.Text, nullable=True)  # descrição dos problemas
    issue_coordinates = db.Column(db.String(100), nullable=True)  # coordenadas x,y onde o problema foi marcado
    uploaded_at = db.Column(db.DateTime, default=func.now())
    
    property_id = db.Column(db.Integer, db.ForeignKey('Properties.id'), nullable=False)
    
    def __repr__(self):
        return f'<PropertyImage {self.filename}>'

class Document(db.Model):
    __tablename__ = 'Documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # AVCB, CND, contrato, etc.
    issue_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)  # data de vencimento, se aplicável
    description = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=func.now())
    
    property_id = db.Column(db.Integer, db.ForeignKey('Properties.id'), nullable=False)
    
    def __repr__(self):
        return f'<Document {self.title}>'
    
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < datetime.now().date()
        return False
    
    def days_to_expiry(self):
        if self.expiry_date:
            delta = self.expiry_date - datetime.now().date()
            return delta.days
        return None

class Transaction(db.Model):
    __tablename__ = 'Transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # receita ou despesa
    category = db.Column(db.String(50), nullable=False)  # aluguel, manutenção, impostos, etc.
    description = db.Column(db.Text, nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default="pendente")  # pendente, pago, atrasado
    recurrence = db.Column(db.String(20), nullable=True)  # mensal, anual, única
    created_at = db.Column(db.DateTime, default=func.now())
    
    property_id = db.Column(db.Integer, db.ForeignKey('Properties.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('Documents.id'), nullable=True)  # comprovante associado
    document = db.relationship('Document')
    
    def __repr__(self):
        return f'<Transaction {self.type} {self.amount}>'

class Alert(db.Model):
    __tablename__ = 'Alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # vencimento, manutenção, reajuste
    status = db.Column(db.String(20), default="não lido")  # não lido, lido, resolvido
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())
    read_at = db.Column(db.DateTime, nullable=True)
    
    property_id = db.Column(db.Integer, db.ForeignKey('Properties.id'), nullable=True)
    property = db.relationship('Property')
    document_id = db.Column(db.Integer, db.ForeignKey('Documents.id'), nullable=True)
    document = db.relationship('Document')
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    user = db.relationship('Users')
    
    def __repr__(self):
        return f'<Alert {self.title}>'