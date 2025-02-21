# Nice Group - Sistema de Gerenciamento de Ativos Imobiliários

Um sistema PWA (Progressive Web App) completo para gerenciamento eficiente de ativos imobiliários, com recursos online e offline, notificações automáticas e análises financeiras detalhadas.

![Dashboard](path_to_screenshot.png)

## Características Principais

- **Interface Responsiva**: Design adaptativo para dispositivos móveis e desktop
- **Gerenciamento Completo de Imóveis**: Cadastro, monitoramento e relatórios
- **Sistema de Documentação**: Organize documentos com alertas de vencimento
- **Controle Financeiro**: Acompanhe receitas, despesas e rentabilidade
- **Recursos PWA**: Funciona offline e pode ser instalado como aplicativo
- **Notificações Automáticas**: Alertas para vencimentos e manutenções
- **Gestão de Imagens**: Upload com marcação de problemas na propriedade

## Tecnologias Utilizadas

- **Backend**: Flask (Python) com SQLAlchemy ORM
- **Frontend**: Volt Dashboard (Bootstrap 5)
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **PWA Features**: Service Workers, Manifest, Push Notifications
- **Hospedagem**: PythonAnywhere

## Instalação e Configuração

### Pré-requisitos

- Python 3.7+ instalado
- Pip (gerenciador de pacotes Python)
- Git

### Passos para Instalação

1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/nice-group-imoveis.git
cd nice-group-imoveis
```

2. Crie e ative um ambiente virtual
```bash
python -m venv venv
# No Windows
venv\Scripts\activate
# No Linux/Mac
source venv/bin/activate
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente (opcional)
```bash
# No Windows (PowerShell)
$env:SECRET_KEY="sua-chave-secreta"
$env:DEBUG="True"

# No Linux/Mac
export SECRET_KEY="sua-chave-secreta"
export DEBUG="True"
```

5. Inicialize o banco de dados
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Execute a aplicação
```bash
python run.py
```

7. Acesse a aplicação no navegador
```
http://localhost:5000
```

## Estrutura do Projeto

```
flask-volt-dashboard-master/
├── apps/
│   ├── home/
│   │   ├── models.py         # Modelos para imóveis, documentos, transações
│   │   ├── forms.py          # Formulários de cadastro
│   │   ├── routes.py         # Rotas da aplicação
│   │   ├── notifications.py  # Sistema de notificação
│   │   └── __init__.py
│   ├── authentication/       # Autenticação de usuários
│   ├── static/
│   │   ├── assets/           # CSS, JS, imagens
│   │   ├── service-worker.js # Para funcionalidade offline (PWA)
│   │   ├── manifest.json     # Configuração PWA
│   │   └── offline.html      # Página offline
│   ├── templates/
│   │   ├── home/
│   │   │   ├── index.html            # Dashboard principal
│   │   │   ├── properties.html       # Lista de imóveis
│   │   │   ├── property_form.html    # Formulário de cadastro
│   │   │   └── property_detail.html  # Detalhes do imóvel
│   │   ├── layouts/
│   │   └── includes/
│   └── __init__.py          # Inicialização da aplicação
├── migrations/              # Migrações do banco de dados
├── requirements.txt         # Dependências do projeto
└── run.py                   # Script para executar a aplicação
```

## Recursos da Aplicação

### Gestão de Imóveis
- Cadastro de imóveis com informações detalhadas
- Acompanhamento de status (alugado, vago, em reforma)
- Gerenciamento de condomínios com múltiplas unidades
- Controle de contratos de locação

### Sistema de Documentação
- Upload e categorização de documentos
- Controle de vencimentos (AVCB, CNDs, contratos)
- Alertas automáticos para documentos a expirar
- Visualização direta de documentos no sistema

### Controle Financeiro
- Registro de receitas e despesas por imóvel
- Cálculo automático de rentabilidade
- Projeção de retorno sobre investimento
- Reajustes automáticos baseados em índices (IGPM, IPCA)

### PWA e Funcionamento Offline
- Instalável como aplicativo em dispositivos móveis
- Acesso a dados mesmo sem conexão à internet
- Sincronização automática quando online
- Interface otimizada para dispositivos móveis

## Configuração para Produção

Para ambientes de produção, recomendamos:

1. Migrar para PostgreSQL:
```python
# Configurar variáveis de ambiente
export DB_ENGINE="postgresql"
export DB_NAME="nice_group_db"
export DB_USERNAME="seu_usuario"
export DB_PASS="sua_senha"
export DB_HOST="localhost"
export DB_PORT="5432"
```

2. Configurar HTTPS para maior segurança
3. Configurar um servidor WSGI como Gunicorn
4. Utilizar um proxy reverso como Nginx

## Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Faça push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Contato

Nice Group - [contato@nicegroup.com.br](mailto:contato@nicegroup.com.br)

## Agradecimentos

- [Volt Dashboard](https://github.com/themesberg/volt-bootstrap-5-dashboard) por fornecer o tema base
- [Flask](https://flask.palletsprojects.com/) pelo framework web
- [SQLAlchemy](https://www.sqlalchemy.org/) pelo ORM poderoso

---

Desenvolvido por [Seu Nome/Empresa] para Nice Group © 2025