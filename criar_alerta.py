from apps import create_app
from apps.config import config_dict
from apps.imoveis.models import Alerta, Imovel
from datetime import datetime, timedelta
from apps.extensions import db

# Inicializa a aplicação
app = create_app(config_dict['Debug'])

# Cria os alertas dentro do contexto da aplicação
with app.app_context():
    # Obter o imóvel pelo ID
    imovel = Imovel.query.get(1)
    
    # Alerta para documento próximo do vencimento (hoje)
    novo_alerta_hoje = Alerta(
        tipo='documento',
        descricao='Documento próximo do vencimento',
        data_vencimento=datetime.now(),
        status='pendente',        
        codigo='17022200'
    )
    db.session.add(novo_alerta_hoje)
    
    # Alerta para documento que vence no dia seguinte
    novo_alerta_amanha = Alerta(
        tipo='documento',
        descricao='Documento vence amanhã',
        data_vencimento=datetime.now() + timedelta(days=1),
        status='pendente',        
        codigo='17022211'
    )
    db.session.add(novo_alerta_amanha)
    
    # Alerta para documento que já venceu
    novo_alerta_vencido = Alerta(
        tipo='documento',
        descricao='Documento já vencido',
        data_vencimento=datetime.now() - timedelta(days=1),
        status='pendente',        
        codigo='17022278'
    )
    db.session.add(novo_alerta_vencido)
    
    # Alerta adicional para documento que vence no dia seguinte
    novo_alerta_amanha_extra = Alerta(
        tipo='documento',
        descricao='Outro documento vence amanhã',
        data_vencimento=datetime.now() + timedelta(days=1),
        status='pendente',        
        codigo='17022200'
    )
    db.session.add(novo_alerta_amanha_extra)
    
    # Alerta adicional para documento que já venceu
    novo_alerta_vencido_extra = Alerta(
        tipo='documento',
        descricao='Outro documento já vencido',
        data_vencimento=datetime.now() - timedelta(days=1),
        status='pendente',        
        codigo='17022255'
    )
    db.session.add(novo_alerta_vencido_extra)
    
    db.session.commit()
    print("Alertas criados com sucesso!")