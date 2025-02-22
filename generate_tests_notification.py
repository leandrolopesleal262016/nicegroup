# generate_tests_notification.py
from apps import create_app, db
from apps.config import config_dict
from apps.models.notification import Notification, NotificationPriority
from apps.authentication.models import Users
import random
from datetime import datetime, timedelta

app = create_app(config_dict['Debug'])

# Definição da função principal para evitar conflitos de inicialização
def create_test_notifications():
    with app.app_context():
        # Encontre um usuário para adicionar notificações
        user = Users.query.first()
        
        if not user:
            print("Nenhum usuário encontrado. Crie um usuário primeiro.")
            return
        
        # Exemplos de notificações
        notifications = [
            # Notificações Urgentes
            {
                'title': 'AVCB expirando em 5 dias',
                'message': 'O Auto de Vistoria do Corpo de Bombeiros do imóvel na Av. Paulista está prestes a expirar.',
                'priority': NotificationPriority.URGENT,
                'category': 'documentação'
            },
            {
                'title': 'Contrato de aluguel expirando amanhã',
                'message': 'O contrato do inquilino João Silva expira em 24 horas.',
                'priority': NotificationPriority.URGENT,
                'category': 'contratos'
            },
            
            # Notificações Alta Prioridade
            {
                'title': 'Manutenção pendente há 20 dias',
                'message': 'A solicitação de reparo de vazamento no teto ainda não foi atendida.',
                'priority': NotificationPriority.HIGH,
                'category': 'manutenção'
            },
            {
                'title': 'Aluguel atrasado em 10 dias',
                'message': 'O inquilino Maria Souza está com o aluguel atrasado desde 10/02/2023.',
                'priority': NotificationPriority.HIGH,
                'category': 'financeiro'
            },
            
            # Notificações Média Prioridade
            {
                'title': 'IPTU vence em 30 dias',
                'message': 'O IPTU do imóvel localizado na Rua Augusta vence no próximo mês.',
                'priority': NotificationPriority.MEDIUM,
                'category': 'impostos'
            },
            {
                'title': 'Renovação de seguro em breve',
                'message': 'O seguro do imóvel comercial precisará ser renovado em 45 dias.',
                'priority': NotificationPriority.MEDIUM,
                'category': 'documentação'
            },
            
            # Notificações Baixa Prioridade
            {
                'title': 'Leitura de medidores pendente',
                'message': 'A leitura dos medidores de água está programada para a próxima semana.',
                'priority': NotificationPriority.LOW,
                'category': 'utilitários'
            },
            {
                'title': 'Atualização de cadastro',
                'message': 'Recomendamos atualizar os dados cadastrais do imóvel na Vila Madalena.',
                'priority': NotificationPriority.LOW,
                'category': 'administrativo'
            }
        ]
        
        # Criar notificações com datas variadas
        for i, notif_data in enumerate(notifications):
            # Cria datas variadas nos últimos 30 dias
            days_ago = random.randint(0, 30)
            created_date = datetime.utcnow() - timedelta(days=days_ago)
            
            notification = Notification(
                user_id=user.id,
                title=notif_data['title'],
                message=notif_data['message'],
                priority=notif_data['priority'],
                category=notif_data['category'],
                created_at=created_date,
                is_read=random.choice([True, False]) if days_ago > 5 else False
            )
            
            db.session.add(notification)
        
        db.session.commit()
        print(f"Foram criadas {len(notifications)} notificações de teste para o usuário {user.username}.")

if __name__ == "__main__":
    create_test_notifications()