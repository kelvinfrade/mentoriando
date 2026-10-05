# Mentoriando

Aplicação web para gestão de mentorados, tarefas, reuniões e horários de atendimento. O projeto utiliza Django, PostgreSQL e templates HTML com Tailwind CSS.

## Sumário

- [Visão geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Requisitos](#requisitos)
- [Configuração local](#configuração-local)
- [Execução](#execução)
- [Testes e qualidade](#testes-e-qualidade)
- [Fluxo de cadastro](#fluxo-de-cadastro)
- [Segurança e privacidade](#segurança-e-privacidade)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Operação e produção](#operação-e-produção)
- [Contribuição](#contribuição)

## Visão geral

O Mentoriando possui dois públicos principais:

- **Mentor:** administra mentorados, navigators, tarefas, reuniões e disponibilidade.
- **Mentorado:** acessa suas tarefas e agenda reuniões por meio do fluxo autorizado.

O sistema segue o padrão MTV do Django e mantém regras de negócio no backend. A interface fornece validações rápidas, mas nenhuma validação de segurança depende exclusivamente do navegador.

## Funcionalidades

- Cadastro com nome completo, username, e-mail, confirmação de e-mail, CPF e celular.
- Validação de CPF e celular no frontend e no backend.
- Bloqueio de duplicidade para username, e-mail, CPF e celular.
- Confirmação de e-mail por link com token de uso único e validade de 24 horas.
- Senhas armazenadas pelo sistema de hash do Django.
- Autenticação multifator TOTP compatível com aplicativos autenticadores.
- Rate limiting para tentativas de login e MFA.
- Detecção de novo dispositivo com alerta por e-mail.
- Revogação de todas as sessões do usuário.
- CPF e celular cifrados em repouso.
- Consentimento explícito para tratamento do CPF.
- Gestão de mentorados, tarefas, reuniões e horários.

## Arquitetura

| Camada | Responsabilidade |
| --- | --- |
| `usuarios` | Cadastro, confirmação de e-mail, login, MFA, sessões e privacidade |
| `mentorados` | Mentorados, tarefas, reuniões, disponibilidade e tokens de acesso |
| `core` | Configurações, middleware, URLs raiz e pontos de entrada WSGI/ASGI |
| `templates` | Layout base e navegação compartilhada |
| `static` | Arquivos estáticos e recursos administrativos |
| PostgreSQL | Persistência por meio do ORM do Django; compatível com Azure Database for PostgreSQL |

As consultas são feitas pelo ORM do Django. O projeto não concatena entrada de usuário em SQL.

## Requisitos

- Python 3.12 ou compatível com Django 5.1.
- Ambiente virtual recomendado.
- Dependências listadas em `requirements.txt`.
- Um backend de e-mail para confirmação de conta e alertas de segurança.

## Configuração local

No Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

No Linux ou macOS:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

As variáveis abaixo podem ser configuradas no ambiente:

| Variável | Uso | Padrão |
| --- | --- | --- |
| `POSTGRES_DB` | Nome do banco PostgreSQL | Sem padrão; obrigatório |
| `POSTGRES_USER` | Usuário PostgreSQL | Sem padrão; obrigatório |
| `POSTGRES_PASSWORD` | Senha PostgreSQL | Sem padrão; obrigatório |
| `POSTGRES_HOST` | Host do servidor Azure, sem `https://` | Sem padrão; obrigatório |
| `POSTGRES_PORT` | Porta PostgreSQL | `5432` |
| `POSTGRES_SSLMODE` | Modo TLS da conexão | `require` |
| `ALLOWED_HOSTS` | Hosts permitidos pelo Django, separados por vírgula | `localhost,127.0.0.1` |
| `SECRET_KEY` | Chave de assinatura e cifragem derivada | Valor definido no arquivo, altere em produção |
| `EMAIL_BACKEND` | Backend de envio de e-mail | Console do Django |
| `DEFAULT_FROM_EMAIL` | Remetente das mensagens | `seguranca@mentoriando.local` |
| `SESSION_COOKIE_SECURE` | Exige HTTPS para cookies de sessão | `True` |
| `CSRF_COOKIE_SECURE` | Exige HTTPS para cookie CSRF | `True` |

Configure as credenciais do PostgreSQL no ambiente da aplicação (no Azure, prefira referências ao Key Vault). Exemplo no PowerShell para desenvolvimento:

```powershell
$env:POSTGRES_DB = "nome-do-banco"
$env:POSTGRES_USER = "usuario-do-banco"
$env:POSTGRES_PASSWORD = "senha-do-banco"
$env:POSTGRES_HOST = "servidor.postgres.database.azure.com"
```

O host deve corresponder ao servidor Azure e a rede/firewall do servidor deve permitir conexões da aplicação.
No Azure App Service, configure `ALLOWED_HOSTS` com o domínio atribuído ao app, por exemplo `mentoriando.azurewebsites.net`.

Para desenvolvimento sem HTTPS, use temporariamente:

```powershell
$env:SESSION_COOKIE_SECURE = "False"
$env:CSRF_COOKIE_SECURE = "False"
```

O backend de e-mail de console imprime o link de confirmação no terminal onde o servidor está rodando.

## Execução

Aplique as migrações:

```bash
python manage.py migrate
```

Inicie o servidor:

```bash
python manage.py runserver 127.0.0.1:8000
```

Acesse:

- Aplicação: <http://127.0.0.1:8000/>
- Cadastro: <http://127.0.0.1:8000/usuarios/cadastro/>
- Login: <http://127.0.0.1:8000/usuarios/login/>

Para criar um administrador:

```bash
python manage.py createsuperuser
```

## Testes e qualidade

Execute as verificações antes de abrir uma alteração:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python -m compileall usuarios core
```

Os testes cobrem, entre outros cenários:

- validação de CPF e celular;
- normalização e proteção de dados pessoais;
- duplicidade de username, e-mail, CPF e celular;
- confirmação e expiração lógica da ativação de e-mail;
- bloqueio de login antes da confirmação;
- MFA e rate limiting.

## Fluxo de cadastro

1. O usuário preenche os dados pessoais, credenciais e consentimento.
2. O frontend valida formato de e-mail, CPF e celular para feedback imediato.
3. O backend repete todas as validações e verifica duplicidades.
4. A conta é criada inativa.
5. Um token aleatório é enviado para o e-mail informado; somente seu hash é armazenado.
6. O usuário acessa o link em até 24 horas.
7. A conta é ativada e pode realizar login.

O celular deve conter 11 dígitos no padrão brasileiro: dois dígitos de DDD, seguidos do nono dígito e mais oito dígitos, por exemplo `(11) 99999-9999`.

## Segurança e privacidade

- Senhas usam os hashers e validadores nativos do Django.
- CPF e celular são cifrados antes da persistência; hashes separados permitem detectar duplicidades sem expor os valores.
- Tokens de confirmação são aleatórios, armazenados somente como hash e expiram.
- Cookies possuem `HttpOnly`, `SameSite=Lax` e configuração `Secure` para HTTPS.
- Sessões podem ser revogadas por meio de **Sair de todos**.
- Login e MFA possuem limite temporário de tentativas por IP e usuário.
- MFA usa TOTP e deve ser ativado em **Segurança**.
- A finalidade do CPF e os direitos do titular estão documentados em [PRIVACIDADE.md](PRIVACIDADE.md) e [TERMOS_DE_USO.md](TERMOS_DE_USO.md).

Antes de publicar, execute a checklist do Django:

```bash
python manage.py check --deploy
```

Em produção, use HTTPS, uma `SECRET_KEY` fora do código, banco gerenciado, backend SMTP, backups cifrados, observabilidade e política de rotação de credenciais.

## Estrutura do projeto

```text
core/              Configuração e entrada do projeto Django
mentorados/        Domínio de mentorados, tarefas e reuniões
usuarios/          Cadastro, autenticação, MFA e privacidade
templates/         Layouts e navegação compartilhada
static/            Arquivos estáticos
manage.py          Comandos administrativos
requirements.txt   Dependências Python fixadas
```

## Operação e produção

- Não use `runserver` como servidor de produção.
- Configure `DEBUG=False` e `ALLOWED_HOSTS` explicitamente.
- O Gunicorn está incluído nas dependências. Configure o comando de inicialização do App Service como `gunicorn --bind=0.0.0.0 --timeout 600 core.wsgi:application`.
- Defina `SECRET_KEY` por variável de ambiente ou secret manager.
- Configure SMTP real para confirmação de e-mail e alertas.
- Use HTTPS para que cookies `Secure` funcionem corretamente.
- Faça backup do banco e do segredo usado para cifragem antes de qualquer migração.
- Revise logs para não registrar CPF, celular, tokens ou senhas.
- Rode migrações durante o deploy e valide com `manage.py check --deploy`.

## Contribuição

1. Crie uma branch para a alteração.
2. Mantenha a mudança focada e preserve as convenções locais.
3. Adicione ou atualize testes para comportamentos alterados.
4. Execute `check`, migrações em modo de verificação e a suíte de testes.
5. Descreva no pull request o problema, a solução, os riscos e como validar.

Não inclua segredos, dados pessoais reais ou o banco de produção no repositório.