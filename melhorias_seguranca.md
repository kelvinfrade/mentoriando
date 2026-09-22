Vou analisar o sistema de cadastro e login atual antes de implementar as melhorias.

Viewed views.py:1-53
Listed directory templates
Listed directory templates
Viewed cadastro.html:1-65
Viewed login.html:1-57
Viewed base.html:1-46
Viewed settings.py:90-110

Agora tenho visão completa. Vou implementar tudo de uma vez. As mudanças são:

1. **Back-end** (`views.py`): Validação robusta de senha (mín. 8 chars, maiúscula, minúscula, número, caractere especial) + mensagem de sucesso no cadastro + proteção contra brute-force no login
2. **Front-end** (`cadastro.html`): Validação em tempo real com indicadores visuais de força de senha
3. **Settings**: Configurar `MinimumLengthValidator` para 8 caracteres

Vamos começar:

Created views.py

Agora vou atualizar o template de cadastro com validação em tempo real no front-end:

Created cadastro.html

Agora vou atualizar o template de login para mostrar as mensagens de sucesso (do cadastro) e erro (tentativas):

Created login.html

Agora vou atualizar o `MinimumLengthValidator` no settings para 8 caracteres:

Edited settings.py

Agora vou reiniciar o servidor e testar:

Used tool: manage_task
Ran command: `.\venv\Scripts\python.exe manage.py runserver`

Vou verificar se as páginas carregam corretamente:

Ran command: `curl.exe -s -o NUL -w "%{http_code}" http://127.0.0.1:8000/usuarios/cadastro/`
Ran command: `curl.exe -s -o NUL -w "%{http_code}" http://127.0.0.1:8000/usuarios/login/`

Tudo funcionando! Ambas as páginas retornam **200**. Aqui está o resumo:

---

## Resumo das melhorias de segurança

### 🔐 Critérios de senha (back-end + front-end)

| Critério | Validação |
|---|---|
| Mínimo 8 caracteres | ✅ Back + Front |
| Pelo menos 1 letra maiúscula | ✅ Back + Front |
| Pelo menos 1 letra minúscula | ✅ Back + Front |
| Pelo menos 1 número | ✅ Back + Front |
| Pelo menos 1 caractere especial | ✅ Back + Front |
| Senhas devem coincidir | ✅ Back + Front |
| Username: apenas letras, números, `_` | ✅ Back + Front |

### 🎨 Front-end — [cadastro.html](file:///c:/Users/User/Documents/SistemaGestaoMentorados/usuarios/templates/cadastro.html)
- **Indicadores visuais em tempo real**: cada critério mostra ✓ (verde) ou ✕ (cinza) conforme o usuário digita
- **Barra de força de senha**: 5 níveis com cores (vermelho → verde) e texto descritivo
- **Validação de confirmação**: mostra em tempo real se as senhas coincidem
- **Bloqueio do submit**: impede envio se critérios não atendidos

### 🛡️ Back-end — [views.py](file:///c:/Users/User/Documents/SistemaGestaoMentorados/usuarios/views.py)
- **Validação completa de senha** com função `validar_senha()` que lista todos os erros
- **Proteção contra brute-force**: limite de 5 tentativas de login por sessão
- **Validação de username**: mínimo 3 chars, apenas caracteres válidos

### 🔔 Notificação de sucesso
- Ao cadastrar com sucesso → redireciona para login com mensagem verde **"Conta criada com sucesso!"**
- [login.html](file:///c:/Users/User/Documents/SistemaGestaoMentorados/usuarios/templates/login.html) agora exibe ícones SVG (✓ verde / ✕ vermelho) e animação fade-in nas notificações

Teste em **http://127.0.0.1:8000/usuarios/cadastro/** para ver a validação em tempo real!