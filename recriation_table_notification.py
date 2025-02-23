from apps import create_app, db
from apps.config import config_dict
from sqlalchemy import text

app = create_app(config_dict['Debug'])

def recreate_notifications_table():
    with app.app_context():
        try:
            # Drop tabela existente
            with db.engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS notifications"))
                conn.execute(text('DROP TABLE IF EXISTS "Notifications"'))
                conn.commit()
            
            # Criar tabela com a nova estrutura
            create_table_sql = """
            CREATE TABLE notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES Users(id),
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                priority VARCHAR(20) DEFAULT 'normal',
                category VARCHAR(50),
                related_entity_type VARCHAR(50),
                related_entity_id INTEGER,
                is_read BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            with db.engine.connect() as conn:
                conn.execute(text(create_table_sql))
                conn.commit()
            
            print("Tabela de notificações recriada com sucesso!")
            
        except Exception as e:
            print(f"Erro ao recriar tabela: {e}")

if __name__ == "__main__":
    recreate_notifications_table()