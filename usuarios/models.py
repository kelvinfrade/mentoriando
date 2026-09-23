import base64
import hashlib
import secrets
from datetime import timedelta

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def _fernet():
	key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
	return Fernet(key)


def normalize_cpf(value):
	return ''.join(character for character in (value or '') if character.isdigit())


def validate_cpf(value):
	cpf = normalize_cpf(value)
	if len(cpf) != 11 or cpf == cpf[0] * 11:
		raise ValidationError('Informe um CPF válido.')

	first_digit = sum(int(cpf[index]) * (10 - index) for index in range(9))
	first_digit = (first_digit * 10 % 11) % 10
	second_digit = sum(int(cpf[index]) * (11 - index) for index in range(10))
	second_digit = (second_digit * 10 % 11) % 10
	if cpf[-2:] != f'{first_digit}{second_digit}':
		raise ValidationError('Informe um CPF válido.')


def normalize_celular(value):
	return ''.join(character for character in (value or '') if character.isdigit())


def validate_celular(value):
	celular = normalize_celular(value)
	if len(celular) != 11 or celular[2] != '9' or celular == celular[0] * 11:
		raise ValidationError('Informe um celular válido com DDD, por exemplo (11) 99999-9999.')


class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	cpf_encrypted = models.TextField()
	cpf_hash = models.CharField(max_length=64, unique=True, db_index=True)
	totp_secret = models.CharField(max_length=64, blank=True)
	mfa_enabled = models.BooleanField(default=False)
	trusted_device_hash = models.CharField(max_length=64, blank=True)
	session_version = models.PositiveIntegerField(default=1)
	email_verified = models.BooleanField(default=False)
	email_verification_token_hash = models.CharField(max_length=64, blank=True)
	email_verification_expires_at = models.DateTimeField(null=True, blank=True)
	celular_encrypted = models.TextField(blank=True)
	celular_hash = models.CharField(max_length=64, blank=True, null=True, unique=True, db_index=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def create_email_verification_token(self):
		token = secrets.token_urlsafe(32)
		self.email_verification_token_hash = hashlib.sha256(token.encode()).hexdigest()
		self.email_verification_expires_at = timezone.now() + timedelta(hours=24)
		self.save(update_fields=['email_verification_token_hash', 'email_verification_expires_at'])
		return token

	def verify_email(self, token):
		if not self.email_verification_token_hash or not self.email_verification_expires_at:
			return False
		if timezone.now() >= self.email_verification_expires_at:
			return False
		if not secrets.compare_digest(
			self.email_verification_token_hash,
			hashlib.sha256(token.encode()).hexdigest(),
		):
			return False
		self.email_verified = True
		self.email_verification_token_hash = ''
		self.email_verification_expires_at = None
		self.user.is_active = True
		self.user.save(update_fields=['is_active'])
		self.save(update_fields=['email_verified', 'email_verification_token_hash', 'email_verification_expires_at'])
		return True

	@property
	def cpf(self):
		try:
			return _fernet().decrypt(self.cpf_encrypted.encode()).decode()
		except InvalidToken as error:
			raise ValidationError('Não foi possível ler o CPF protegido.') from error

	@cpf.setter
	def cpf(self, value):
		normalized = normalize_cpf(value)
		validate_cpf(normalized)
		self.cpf_encrypted = _fernet().encrypt(normalized.encode()).decode()
		self.cpf_hash = hashlib.sha256(normalized.encode()).hexdigest()

	@property
	def celular(self):
		try:
			return _fernet().decrypt(self.celular_encrypted.encode()).decode()
		except InvalidToken as error:
			raise ValidationError('Não foi possível ler o celular protegido.') from error

	@celular.setter
	def celular(self, value):
		normalized = normalize_celular(value)
		validate_celular(normalized)
		self.celular_encrypted = _fernet().encrypt(normalized.encode()).decode()
		self.celular_hash = hashlib.sha256(normalized.encode()).hexdigest()

	@staticmethod
	def device_hash(request):
		value = f'{request.META.get("REMOTE_ADDR", "")}:{request.META.get("HTTP_USER_AGENT", "")}'
		return hashlib.sha256(value.encode()).hexdigest()
