from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib import auth
import re

# Create your views here.

def validar_senha(senha):
    """
    Valida a senha com critérios de segurança.
    Retorna uma lista de erros encontrados.
    """
    erros = []
    
    if len(senha) < 8:
        erros.append('A senha deve ter no mínimo 8 caracteres.')
    
    if not re.search(r'[A-Z]', senha):
        erros.append('A senha deve conter pelo menos uma letra maiúscula.')
    
    if not re.search(r'[a-z]', senha):
        erros.append('A senha deve conter pelo menos uma letra minúscula.')
    
    if not re.search(r'[0-9]', senha):
        erros.append('A senha deve conter pelo menos um número.')
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?~`]', senha):
        erros.append('A senha deve conter pelo menos um caractere especial (!@#$%^&*...).')
    
    return erros

def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if not username or not username.strip():
            messages.add_message(request, constants.ERROR, 'O campo username é obrigatório.')
            return redirect('/usuarios/cadastro/')
        
        username = username.strip()
        
        if len(username) < 3:
            messages.add_message(request, constants.ERROR, 'O username deve ter no mínimo 3 caracteres.')
            return redirect('/usuarios/cadastro/')
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            messages.add_message(request, constants.ERROR, 'O username deve conter apenas letras, números e underline.')
            return redirect('/usuarios/cadastro/')
        
        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, 'Senha e Confirmar Senha devem ser iguais.')
            return redirect('/usuarios/cadastro/')
        
        # Validação de complexidade de senha
        erros_senha = validar_senha(senha)
        if erros_senha:
            for erro in erros_senha:
                messages.add_message(request, constants.ERROR, erro)
            return redirect('/usuarios/cadastro/')
        
        users = User.objects.filter(username=username)
        
        if users.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um usuário com esse username.')
            return redirect('/usuarios/cadastro/')
        
        User.objects.create_user(
            username=username,
            password=senha
        )
        
        messages.add_message(request, constants.SUCCESS, 'Conta criada com sucesso! Faça login para continuar.')
        return redirect('/usuarios/login/')

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        
        # Proteção contra brute-force: limita tentativas por sessão
        tentativas = request.session.get('login_tentativas', 0)
        
        if tentativas >= 5:
            messages.add_message(request, constants.ERROR, 'Muitas tentativas de login. Aguarde alguns minutos e tente novamente.')
            return redirect('login')
        
        user = authenticate(request, username=username, password=senha)
        
        if user:
            # Resetar contador de tentativas ao fazer login com sucesso
            request.session['login_tentativas'] = 0
            auth.login(request, user)
            return redirect('/mentorados/')
        
        # Incrementar contador de tentativas falhas
        request.session['login_tentativas'] = tentativas + 1
        tentativas_restantes = 5 - (tentativas + 1)
        
        if tentativas_restantes > 0:
            messages.add_message(request, constants.ERROR, f'Usuário ou senha inválidos. {tentativas_restantes} tentativa(s) restante(s).')
        else:
            messages.add_message(request, constants.ERROR, 'Muitas tentativas de login. Aguarde alguns minutos e tente novamente.')
        
        return redirect('login')

def logout(request):
    auth.logout(request)
    return redirect('login')