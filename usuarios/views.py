from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib import auth
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import re

from .forms import CadastroForm
from .models import UserProfile
from .utils import get_client_ip
import pyotp

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

@require_http_methods(['GET', 'POST'])
def cadastro(request):
    form = CadastroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        erros_senha = validar_senha(form.cleaned_data['senha'])
        if erros_senha:
            for erro in erros_senha:
                form.add_error('senha', erro)
        else:
            with transaction.atomic():
                user = form.save()
                profile = user.profile
                token = profile.create_email_verification_token()
                link = request.build_absolute_uri(f'{reverse("confirmar_email")}?token={token}&uid={user.pk}')
                send_mail(
                    'Confirme seu e-mail - Mentoriando',
                    f'Olá, {user.first_name}! Confirme seu e-mail acessando: {link}\n\nO link expira em 24 horas.',
                    None,
                    [user.email],
                    fail_silently=False,
                )
            messages.success(request, 'Cadastro iniciado. Verifique seu e-mail para ativar a conta.')
            return redirect('login')
    return render(request, 'cadastro.html', {'form': form})

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        
        ip = get_client_ip(request)
        chave_ip = f'login-falhas-ip:{ip}'
        chave_usuario = f'login-falhas-usuario:{(username or "").strip().lower()}'
        tentativas = max(cache.get(chave_ip, 0), cache.get(chave_usuario, 0))
        
        if tentativas >= 5:
            messages.add_message(request, constants.ERROR, 'Muitas tentativas de login. Aguarde alguns minutos e tente novamente.')
            return redirect('login')
        
        user = authenticate(request, username=username, password=senha)
        
        if user:
            profile = getattr(user, 'profile', None)
            codigo_mfa = (request.POST.get('codigo_mfa') or '').strip()
            if profile and profile.mfa_enabled:
                chave_mfa = f'mfa-falhas:{ip}:{user.pk}'
                falhas_mfa = cache.get(chave_mfa, 0)
                if falhas_mfa >= 5:
                    messages.error(request, 'Muitas tentativas de MFA. Aguarde alguns minutos.')
                    return redirect('login')
                if not re.fullmatch(r'\d{6}', codigo_mfa) or not pyotp.TOTP(profile.totp_secret).verify(codigo_mfa):
                    cache.set(chave_mfa, falhas_mfa + 1, 300)
                    messages.error(request, 'Código MFA inválido ou ausente.')
                    return redirect('login')
                cache.delete(chave_mfa)
            cache.delete(chave_ip)
            cache.delete(chave_usuario)
            auth.login(request, user)
            if profile:
                request.session['session_version'] = profile.session_version
            device_hash = UserProfile.device_hash(request)
            if profile and profile.trusted_device_hash and profile.trusted_device_hash != device_hash:
                send_mail(
                    'Novo acesso detectado',
                    f'Um novo dispositivo acessou sua conta a partir do IP {ip}.',
                    None,
                    [user.email],
                    fail_silently=True,
                )
            if profile:
                profile.trusted_device_hash = device_hash
                profile.save(update_fields=['trusted_device_hash'])
            return redirect('/mentorados/')
        
        # Incrementar contador de tentativas falhas
        cache.set(chave_ip, cache.get(chave_ip, 0) + 1, 300)
        cache.set(chave_usuario, cache.get(chave_usuario, 0) + 1, 300)
        tentativas_restantes = 5 - (tentativas + 1)
        
        if tentativas_restantes > 0:
            messages.add_message(request, constants.ERROR, f'Usuário ou senha inválidos. {tentativas_restantes} tentativa(s) restante(s).')
        else:
            messages.add_message(request, constants.ERROR, 'Muitas tentativas de login. Aguarde alguns minutos e tente novamente.')
        
        return redirect('login')


@require_http_methods(['GET'])
def confirmar_email(request):
    user_id = request.GET.get('uid')
    token = request.GET.get('token', '')
    profile = UserProfile.objects.filter(user_id=user_id).select_related('user').first()
    if profile and profile.verify_email(token):
        messages.success(request, 'E-mail confirmado. Agora você pode entrar na sua conta.')
    else:
        messages.error(request, 'Link de confirmação inválido ou expirado.')
    return redirect('login')

def logout(request):
    auth.logout(request)
    return redirect('login')


@login_required
@require_http_methods(['POST'])
def logout_all(request):
    profile = getattr(request.user, 'profile', None)
    if profile:
        profile.session_version += 1
        profile.save(update_fields=['session_version'])
    auth.logout(request)
    messages.success(request, 'Todas as sessões foram encerradas.')
    return redirect('login')


@require_http_methods(['GET', 'POST'])
def configurar_mfa(request):
    if not request.user.is_authenticated:
        return redirect('login')
    profile = getattr(request.user, 'profile', None)
    if profile is None:
        messages.error(request, 'Seu perfil ainda não possui CPF cadastrado.')
        return redirect('/mentorados/')
    if not profile.totp_secret:
        profile.totp_secret = pyotp.random_base32()
        profile.save(update_fields=['totp_secret'])
    if request.method == 'POST':
        if pyotp.TOTP(profile.totp_secret).verify((request.POST.get('codigo') or '').strip()):
            profile.mfa_enabled = True
            profile.save(update_fields=['mfa_enabled'])
            messages.success(request, 'MFA ativado com sucesso.')
            return redirect('/mentorados/')
        messages.error(request, 'Código MFA inválido.')
    uri_mfa = pyotp.TOTP(profile.totp_secret).provisioning_uri(
        name=request.user.email or request.user.username,
        issuer_name='Mentoriando',
    )
    return render(request, 'mfa.html', {'chave_mfa': profile.totp_secret, 'uri_mfa': uri_mfa})


def termos(request):
    return render(request, 'legal.html', {'titulo': 'Termos de Uso', 'conteudo': [
        'Forneça dados verdadeiros, mantenha sua senha em sigilo e comunique acessos não reconhecidos.',
        'O CPF é usado para identificação da conta e prevenção a fraudes, conforme nossa Política de Privacidade.',
        'O uso do sistema pode ser suspenso em caso de fraude, abuso ou violação destes termos.',
    ]})


def privacidade(request):
    return render(request, 'legal.html', {'titulo': 'Política de Privacidade', 'conteudo': [
        'Coletamos username, e-mail e CPF. O CPF é solicitado para identificação da conta e prevenção a fraudes.',
        'O CPF é cifrado antes de ser armazenado e a senha nunca é armazenada em texto claro.',
        'O titular pode solicitar confirmação, acesso, correção e eliminação quando aplicável.',
        'O consentimento para o tratamento do CPF é solicitado de forma explícita no cadastro.',
    ]})