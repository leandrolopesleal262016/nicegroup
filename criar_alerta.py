from apps import create_app
from apps.config import config_dict
from apps.imoveis.models import Alerta
from datetime import datetime
from apps.extensions import db

# Inicializa a aplicação
app = create_app(config_dict['Debug'])

# Cria o alerta dentro do contexto da aplicação
with app.app_context():
    novo_alerta = Alerta(
        tipo='documento',
        descricao='Documento próximo do vencimento',
        data_vencimento=datetime.now(),
        status='pendente',
        imovel_id=1
    )
    db.session.add(novo_alerta)
    db.session.commit()
    print("Alerta criado com sucesso!")
