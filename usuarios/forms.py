import hashlib
import re

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import UserProfile, normalize_cpf, validate_cpf


class CadastroForm(forms.Form):
    nome_completo = forms.CharField(min_length=3, max_length=150)
    username = forms.CharField(min_length=3, max_length=150)
    email = forms.EmailField(max_length=254)
    confirmar_email = forms.EmailField(max_length=254)
    cpf = forms.CharField(max_length=14)
    senha = forms.CharField(widget=forms.PasswordInput)
    confirmar_senha = forms.CharField(widget=forms.PasswordInput)
    consentimento_lgpd = forms.BooleanField(required=True)

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if not re.fullmatch(r'[a-zA-Z0-9_]+', username):
            raise forms.ValidationError('O username deve conter apenas letras, números e underline.')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Já existe um usuário com esse username.')
        return username

    def clean_nome_completo(self):
        nome = ' '.join(self.cleaned_data['nome_completo'].split())
        if len(nome) < 3:
            raise forms.ValidationError('Informe seu nome completo.')
        return nome

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Já existe uma conta com esse e-mail.')
        return email

    def clean_cpf(self):
        cpf = normalize_cpf(self.cleaned_data['cpf'])
        validate_cpf(cpf)
        if UserProfile.objects.filter(cpf_hash=hashlib.sha256(cpf.encode()).hexdigest()).exists():
            raise forms.ValidationError('Já existe uma conta com esse CPF.')
        return cpf

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('email') != cleaned_data.get('confirmar_email', '').strip().lower():
            self.add_error('confirmar_email', 'Os e-mails não coincidem.')
        if cleaned_data.get('senha') != cleaned_data.get('confirmar_senha'):
            self.add_error('confirmar_senha', 'As senhas não coincidem.')
        if cleaned_data.get('senha') and cleaned_data.get('username'):
            try:
                validate_password(cleaned_data['senha'], User(username=cleaned_data['username']))
            except ValidationError as error:
                self.add_error('senha', error)
        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            first_name=self.cleaned_data['nome_completo'],
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['senha'],
        )
        user.is_active = False
        user.save(update_fields=['is_active'])
        profile = UserProfile(user=user)
        profile.cpf = self.cleaned_data['cpf']
        profile.save()
        return user