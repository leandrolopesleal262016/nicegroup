# generate_tests_notification.py
from apps import create_app, db
from apps.config import config_dict
from apps.authentication.models import Users
from apps.notifications.models import Notification  # Atualizado o caminho da importação
from datetime import datetime

app = create_app(config_dict['Debug'])

def create_test_notifications():
    with app.app_context():
        try:
            # Encontre um usuário para adicionar notificações
            user = Users.query.first()
            
            if not user:
                print("Nenhum usuário encontrado. Crie um usuário primeiro.")
                return
            
            # Limpar notificações existentes
            print("Limpando notificações existentes...")
            Notification.query.delete()
            db.session.commit()
            
            # Exemplos de notificações
            notifications = [
                # Urgentes
                {
                    'title': 'AVCB expirando em 5 dias',
                    'message': 'O Auto de Vistoria do Corpo de Bombeiros do imóvel na Av. Paulista está prestes a expirar.',
                    'priority': 'urgent',
                    'category': 'document',
                    'related_entity_type': 'property'
                },
                {
                    'title': 'Contrato de aluguel expirando amanhã',
                    'message': 'O contrato do inquilino João Silva expira em 24 horas.',
                    'priority': 'urgent',
                    'category': 'contract',
                    'related_entity_type': 'contract'
                },
                
                # Alta Prioridade
                {
                    'title': 'Manutenção pendente há 20 dias',
                    'message': 'A solicitação de reparo de vazamento no teto ainda não foi atendida.',
                    'priority': 'high',
                    'category': 'maintenance',
                    'related_entity_type': 'property'
                },
                {
                    'title': 'Aluguel atrasado em 10 dias',
                    'message': 'O inquilino Maria Souza está com o aluguel atrasado desde 10/02/2023.',
                    'priority': 'high',
                    'category': 'financial',
                    'related_entity_type': 'contract'
                },
                
                # Média Prioridade
                {
                    'title': 'IPTU vence em 30 dias',
                    'message': 'O IPTU do imóvel localizado na Rua Augusta vence no próximo mês.',
                    'priority': 'medium',
                    'category': 'financial',
                    'related_entity_type': 'property'
                },
                {
                    'title': 'Renovação de seguro em breve',
                    'message': 'O seguro do imóvel comercial precisará ser renovado em 45 dias.',
                    'priority': 'medium',
                    'category': 'document',
                    'related_entity_type': 'property'
                },
                
                # Baixa Prioridade
                {
                    'title': 'Leitura de medidores pendente',
                    'message': 'A leitura dos medidores de água está programada para a próxima semana.',
                    'priority': 'low',
                    'category': 'maintenance',
                    'related_entity_type': 'property'
                },
                {
                    'title': 'Atualização de cadastro',
                    'message': 'Recomendamos atualizar os dados cadastrais do imóvel na Vila Madalena.',
                    'priority': 'low',
                    'category': 'document',
                    'related_entity_type': 'property'
                }
            ]
            
            print("Criando novas notificações...")
            for notif_data in notifications:
                notification = Notification(
                    user_id=user.id,
                    title=notif_data['title'],
                    message=notif_data['message'],
                    priority=notif_data['priority'],
                    category=notif_data['category'],
                    related_entity_type=notif_data['related_entity_type'],
                    is_read=False,
                    created_at=datetime.now()
                )
                db.session.add(notification)
            
            db.session.commit()
            print(f"Foram criadas {len(notifications)} notificações de teste para o usuário {user.username}.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar notificações: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_test_notifications()