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
