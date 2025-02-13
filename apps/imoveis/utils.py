from datetime import datetime, timedelta
from apps.imoveis.models import Documento, Alerta
from apps.imoveis.email_service import enviar_notificacao_vencimento

def verificar_vencimentos():
    # Verifica documentos que vencem em 30 dias
    data_limite = datetime.now() + timedelta(days=30)
    
    documentos_proximos = Documento.query.filter(
        Documento.data_vencimento <= data_limite,
        Documento.data_vencimento > datetime.now()
    ).all()
    
    for doc in documentos_proximos:
        # Cria alerta se não existir
        alerta_existente = Alerta.query.filter_by(
            tipo='documento',
            imovel_id=doc.imovel_id,
            status='pendente'
        ).first()
        
        if not alerta_existente:
            novo_alerta = Alerta(
                tipo='documento',
                descricao=f'Documento {doc.tipo} vence em {doc.data_vencimento.strftime("%d/%m/%Y")}',
                data_vencimento=doc.data_vencimento,
                status='pendente',
                imovel_id=doc.imovel_id
            )
            db.session.add(novo_alerta)
            
            # Enviar email
            destinatarios = ['gestor@gruponice.com.br', 'admin@gruponice.com.br']
            enviar_notificacao_vencimento(novo_alerta, destinatarios)
    
    db.session.commit()

import requests
from datetime import datetime
from apps.extensions import db
from apps.imoveis.models import Alerta

def consultar_cpfl(numero_cliente):
    # CPFL API endpoint
    url = "https://api.cpfl.com.br/consulta"
    
    # API credentials
    headers = {
        "Authorization": "Bearer YOUR_API_TOKEN",
        "Content-Type": "application/json"
    }
    
    # Request payload
    data = {
        "numeroCliente": numero_cliente
    }
    
    try:
        response = requests.get(url, headers=headers, json=data)
        response.raise_for_status()
        
        fatura = response.json()
        
        if fatura['status'] == 'ATRASADA':
            # Create alert for overdue bill
            alerta = Alerta(
                tipo='fatura_energia',
                descricao=f'Fatura de energia atrasada - Valor: R$ {fatura["valor"]}',
                data_vencimento=datetime.strptime(fatura['dataVencimento'], '%Y-%m-%d'),
                status='pendente',
                imovel_id=fatura['imovel_id']
            )
            db.session.add(alerta)
            db.session.commit()
            
        return fatura
        
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
