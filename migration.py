# add_columns.py
from apps import create_app, db
from apps.config import config_dict
from sqlalchemy import text

app = create_app(config_dict['Debug'])

def add_columns():
    with app.app_context():
        columns = [
            "first_name TEXT", 
            "last_name TEXT", 
            "phone TEXT", 
            "address TEXT", 
            "city TEXT", 
            "state TEXT", 
            "zip_code TEXT", 
            "profile_image TEXT", 
            "cover_image TEXT"
        ]
        
        with db.engine.connect() as conn:
            for column in columns:
                try:
                    conn.execute(text(f"ALTER TABLE Users ADD COLUMN {column}"))
                    print(f"Coluna {column.split()[0]} adicionada com sucesso!")
                except Exception as e:
                    print(f"Erro ao adicionar coluna {column.split()[0]}: {str(e)}")
            conn.commit()
            print("Migração concluída!")

if __name__ == "__main__":
    add_columns()