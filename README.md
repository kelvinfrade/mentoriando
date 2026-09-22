 # 📘 SistemaGestaoMentorados

Este repositório contém um sistema de gestão de mentorados desenvolvido em **Python** utilizando o framework **Django**, com **Tailwind CSS** para estilização, **SQLite** como banco de dados e **HTML** para as templates. O sistema permite que um mentor crie uma conta, realize login e gerencie seus mentorados. O mentor pode atribuir um "navigator" da equipe para acompanhar de perto as atividades de cada mentorado, criar listas de tarefas e definir horários disponíveis para reuniões. Já o mentorado acessa sua área por meio de um token único, podendo acompanhar suas tarefas e agendar reuniões com o mentor.

O projeto foi desenvolvido durante o evento **PYSTACK WEEK 13**, uma semana de aprendizado com o Caio da **Pythonando**, a maior escola de desenvolvimento web com Python e Django do Brasil.

---

## 🚀 Funcionalidades Extras Implementadas

Além do conteúdo ensinado nas aulas do PYSTACK WEEK 13, implementei as seguintes melhorias no projeto:

- **Verificação de Data:** Adicionei um código em Python para verificar o dia da semana e o mês de uma data, passando os parâmetros corretos para o HTML, facilitando a exibição de informações dinâmicas.
- **Menu Hamburguer Responsivo:** Realizei ajustes no CSS para que o menu hamburguer fosse exibido corretamente em janelas pequenas e dispositivos móveis, melhorando a experiência de navegação.
- **Ajuste de Links:** Corrigi e padronizei os links dos menus em todas as páginas do sistema, garantindo consistência e navegabilidade.
- **Página de Erro 404 Personalizada:** Criei e configurei uma página personalizada para erros 404 (Not Found), exibida quando alguém acessa um link inexistente.
- **Redirecionamento da Raiz:** Configurei um redirecionamento da raiz (`http://127.0.0.1:8000`) para a página de mentorados (`http://127.0.0.1:8000/mentorados/`), otimizando o acesso inicial ao sistema.

---

## 🧠 Conhecimentos Adquiridos

O desenvolvimento deste projeto proporcionou um aprendizado profundo em diversas áreas:

- **Arquitetura de Software:** Entendimento da organização de um projeto web, separando responsabilidades entre frontend e backend.
- **Padrão MTV (Model-Template-View):** Aplicação prática do padrão MTV do Django, compreendendo como models, templates e views interagem para construir um sistema dinâmico.
- **Desenvolvimento Web com Django:** Criação de rotas, manipulação de formulários, integração com banco de dados e gerenciamento de autenticação de usuários.
- **Estilização com Tailwind CSS:** Uso de um framework CSS utilitário para criar interfaces modernas e responsivas de forma eficiente.
- **Gerenciamento de Banco de Dados:** Configuração e uso do SQLite com Django, incluindo migrações e consultas dinâmicas.
- **Boas Práticas:** Adoção de práticas como redirecionamentos, tratamento de erros e responsividade, essenciais para um sistema web robusto e amigável.

---

## ▶️ Como Executar os Códigos

1. **Configurar o Ambiente:**
   - Certifique-se de que o Python está instalado.
   - Crie e ative um ambiente virtual (recomendado):  
     - `python -m venv venv`  
     - No Windows: `venv\Scripts\activate`  
     - No Linux/macOS: `source venv/bin/activate`
   - Instale o Django: `pip install django`.

2. **Configurar o Banco de Dados:**
   - Navegue até a pasta do projeto.
   - Execute as migrações do Django para criar o banco de dados SQLite:  
     - `python manage.py makemigrations`  
     - `python manage.py migrate`

3. **Executar o Sistema:**
   - Inicie o servidor Django: `python manage.py runserver`.
   - O sistema estará disponível em `http://127.0.0.1:8000`.

4. **Acessar o Sistema:**
   - Abra o navegador e acesse `http://127.0.0.1:8000`.
   - Crie uma conta como mentor, faça login e comece a gerenciar mentorados.

---

## 📥 Como Baixar o Repositório

1. Clique no botão verde "Code" no topo da página do GitHub.
2. Selecione "Download ZIP" e extraia o arquivo no seu computador.
3. Ou use o Git: `git clone https://github.com/cstavaresj/SistemaGestaoMentorados.git`

---
