from datetime import datetime
from flask_mail import Message
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apps.imoveis.utils import verificar_vencimentos

def verificar_vencimentos():
    # Verificar documentos próximos do vencimento
    documentos = Documento.query.filter(
        Documento.data_vencimento >= datetime.now()
    ).all()
    
    for doc in documentos:
        if (doc.data_vencimento - datetime.now()).days <= 30:
            enviar_alerta_vencimento(doc)

def calcular_performance_imovel(imovel_id):
    receitas = Financeiro.query.filter_by(
        imovel_id=imovel_id, 
        tipo='receita'
    ).all()
    despesas = Financeiro.query.filter_by(
        imovel_id=imovel_id, 
        tipo='despesa'
    ).all()
    
    return sum(r.valor for r in receitas) - sum(d.valor for d in despesas)

def iniciar_agendador():
    scheduler = BackgroundScheduler()
    scheduler.add_job(verificar_vencimentos, 'cron', hour=8)  # Executa todo dia às 8h
    scheduler.start()
