from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SelectField, BooleanField, DateField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileField, FileAllowed

class PropertyForm(FlaskForm):
    address = StringField('Endereço', validators=[DataRequired()])
    size = FloatField('Tamanho (m²)', validators=[DataRequired()])
    property_type = SelectField('Tipo de Imóvel', choices=[
        ('casa', 'Casa'),
        ('apartamento', 'Apartamento'),
        ('sala_comercial', 'Sala Comercial'),
        ('galpao', 'Galpão'),
        ('terreno', 'Terreno'),
        ('outros', 'Outros')
    ], validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('disponível', 'Disponível'),
        ('alugado', 'Alugado'),
        ('desocupado', 'Desocupado'),
        ('em reforma', 'Em Reforma')
    ], validators=[DataRequired()])
    rent_value = FloatField('Valor do Aluguel (R$)', validators=[Optional()])
    iptu = FloatField('IPTU Anual (R$)', validators=[Optional()])
    condominium_fee = FloatField('Taxa de Condomínio (R$)', validators=[Optional()])
    description = TextAreaField('Descrição', validators=[Optional()])
    is_condominium = BooleanField('É um condomínio com múltiplas unidades?')
    adjustment_index = SelectField('Índice de Reajuste', choices=[
        ('', 'Selecione um índice'),
        ('IGPM', 'IGPM'),
        ('IPCA', 'IPCA')
    ], validators=[Optional()])

class DocumentForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    document_type = SelectField('Tipo de Documento', choices=[
        ('contrato', 'Contrato de Locação'),
        ('avcb', 'AVCB/CLB'),
        ('cnd', 'Certidão Negativa de Débitos'),
        ('escritura', 'Escritura'),
        ('nota_fiscal', 'Nota Fiscal'),
        ('conta', 'Conta de Consumo'),
        ('comprovante', 'Comprovante de Pagamento'),
        ('outros', 'Outros')
    ], validators=[DataRequired()])
    file = FileField('Arquivo', validators=[
        DataRequired(),
        FileAllowed(['pdf', 'jpg', 'png'], 'Somente PDF, JPG ou PNG')
    ])
    issue_date = DateField('Data de Emissão', validators=[Optional()])
    expiry_date = DateField('Data de Vencimento', validators=[Optional()])
    description = TextAreaField('Descrição', validators=[Optional()])

class PropertyImageForm(FlaskForm):
    file = FileField('Imagem', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'png'], 'Somente JPG ou PNG')
    ])
    description = StringField('Descrição', validators=[Optional()])
    has_issues = BooleanField('Tem problemas?')
    issue_description = TextAreaField('Descrição do Problema', validators=[Optional()])
    issue_coordinates = StringField('Coordenadas do Problema', validators=[Optional()])

class TransactionForm(FlaskForm):
    date = DateField('Data', validators=[DataRequired()])
    amount = FloatField('Valor (R$)', validators=[DataRequired()])
    type = SelectField('Tipo', choices=[
        ('receita', 'Receita'),
        ('despesa', 'Despesa')
    ], validators=[DataRequired()])
    category = SelectField('Categoria', choices=[
        ('aluguel', 'Aluguel'),
        ('condominio', 'Condomínio'),
        ('iptu', 'IPTU'),
        ('manutencao', 'Manutenção'),
        ('conta_luz', 'Conta de Luz'),
        ('conta_agua', 'Conta de Água'),
        ('conta_gas', 'Conta de Gás'),
        ('conta_internet', 'Internet'),
        ('seguro', 'Seguro'),
        ('outros', 'Outros')
    ], validators=[DataRequired()])
    description = TextAreaField('Descrição', validators=[Optional()])
    payment_method = SelectField('Método de Pagamento', choices=[
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao', 'Cartão de Crédito/Débito'),
        ('transferencia', 'Transferência Bancária'),
        ('boleto', 'Boleto'),
        ('outros', 'Outros')
    ], validators=[Optional()])
    status = SelectField('Status', choices=[
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('atrasado', 'Atrasado')
    ], validators=[DataRequired()])
    recurrence = SelectField('Recorrência', choices=[
        ('unica', 'Única'),
        ('mensal', 'Mensal'),
        ('anual', 'Anual')
    ], validators=[DataRequired()])
    file = FileField('Comprovante', validators=[
        Optional(),
        FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'Somente PDF, JPG ou PNG')
    ])