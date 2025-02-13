from flask_mail import Message
from apps.extensions import mail

def enviar_notificacao_vencimento(alerta, destinatarios):
    subject = f'ALERTA: {alerta.tipo.upper()} - Vencimento Próximo'
    
    html_content = f"""
    <h2>Sistema de Gestão Patrimonial - NICE</h2>
    <p>Um novo alerta foi gerado:</p>
    <ul>
        <li><strong>Tipo:</strong> {alerta.tipo}</li>
        <li><strong>Descrição:</strong> {alerta.descricao}</li>
        <li><strong>Vencimento:</strong> {alerta.data_vencimento.strftime('%d/%m/%Y')}</li>
        <li><strong>Imóvel:</strong> {alerta.imovel.codigo}</li>
    </ul>
    <p>Por favor, acesse o sistema para mais detalhes.</p>
    """
    
    msg = Message(
        subject=subject,
        recipients=destinatarios,
        html=html_content
    )
    
    mail.send(msg)

def enviar_email_teste(email_destino):
    subject = 'Teste de Configuração - Sistema NICE'
    
    html_content = """
    <h2>Teste de Configuração - Sistema de Gestão Patrimonial NICE</h2>
    <p>Este é um email de teste para validar as configurações do sistema.</p>
    <p>Se você recebeu este email, significa que as configurações estão corretas!</p>
    <hr>
    <p><small>Email enviado automaticamente pelo sistema.</small></p>
    """
    
    msg = Message(
        subject=subject,
        recipients=[email_destino],
        html=html_content
    )
    
    try:
        mail.send(msg)
        return True, "Email de teste enviado com sucesso!"
    except Exception as e:
        return False, f"Erro ao enviar email: {str(e)}"
