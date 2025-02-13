
from flask import Blueprint

blueprint = Blueprint(
    'imoveis_blueprint',
    __name__,
    url_prefix='/imoveis'
)

# Importar modelos antes das rotas
from apps.imoveis.models import Imovel, Foto, Alerta
from apps.imoveis import routes
