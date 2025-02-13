from apps import create_app
from apps.config import config_dict
from apps.authentication.models import Users
from apps.extensions import db

app = create_app(config_dict['Debug'])

with app.app_context():
    # Cria o usuário
    user = Users(
        username="Leandro Leal",
        email="seu@email.com",
        password="5510"
    )
    db.session.add(user)
    db.session.commit()
    print("Usuário criado com sucesso!")
