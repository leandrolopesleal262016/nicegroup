# resolver_tabela_notificacoes.py
import sys
import os
from sqlalchemy import text, inspect

# Adiciona o diretório raiz ao path do Python
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from apps import create_app, db
from apps.config import config_dict
from apps.models.notification import Notification

app = create_app(config_dict['Debug'])

def resolver_tabela_notificacoes():
    with app.app_context():
        try:
            print("Verificando tabelas existentes no banco de dados...")
            
            inspector = inspect(db.engine)
            tabelas = inspector.get_table_names()
            print(f"Tabelas encontradas: {tabelas}")
            
            # Remover ambas as possíveis tabelas
            with db.engine.begin() as conn:
                # Excluir tabela com nome minúsculo
                conn.execute(text("DROP TABLE IF EXISTS notifications"))
                print("Tabela 'notifications' (minúsculo) removida ou não existia.")
                
                # Verificar se existe tabela com N maiúsculo
                if '"Notifications"' in tabelas:
                    conn.execute(text('DROP TABLE IF EXISTS "Notifications"'))
                    print('Tabela "Notifications" (maiúsculo) removida.')
            
            # Recriando a tabela
            print("\nTabela definida no modelo Notification:")
            print(f"Nome da tabela: {Notification.__tablename__}")
            
            # Criar a tabela
            try:
                Notification.__table__.create(db.engine)
                print(f"Tabela '{Notification.__tablename__}' criada com sucesso.")
                
                # Verificar colunas da tabela
                inspector = inspect(db.engine)
                colunas = [c['name'] for c in inspector.get_columns(Notification.__tablename__)]
                print(f"Colunas: {colunas}")
            except Exception as e:
                print(f"Erro ao criar tabela: {e}")
            
        except Exception as e:
            print(f"Erro durante o processo: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    resolver_tabela_notificacoes()