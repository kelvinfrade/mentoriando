from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import RequestFactory, SimpleTestCase, TestCase

from .forms import CadastroForm
from .models import UserProfile
from .utils import get_client_ip
import pyotp


class ClientIPTests(SimpleTestCase):
	def setUp(self):
		self.factory = RequestFactory()

	def test_uses_first_forwarded_ip(self):
		request = self.factory.get(
			'/',
			HTTP_X_FORWARDED_FOR='203.0.113.8, 10.0.0.1',
			REMOTE_ADDR='169.254.129.1',
		)
		self.assertEqual(get_client_ip(request), '203.0.113.8')

	def test_falls_back_to_remote_addr_without_forwarded_ip(self):
		request = self.factory.get('/', REMOTE_ADDR='169.254.129.1')
		self.assertEqual(get_client_ip(request), '169.254.129.1')


class CadastroTests(TestCase):
	def setUp(self):
		cache.clear()

	def dados_validos(self, **overrides):
		dados = {
			'nome_completo': 'Pessoa Teste',
			'username': 'novo_usuario',
			'email': 'pessoa@example.com',
			'confirmar_email': 'pessoa@example.com',
			'cpf': '529.982.247-25',
			'celular': '(11) 99999-9999',
			'senha': 'SenhaForte!123',
			'confirmar_senha': 'SenhaForte!123',
			'consentimento_lgpd': 'on',
		}
		dados.update(overrides)
		return dados

	def test_cadastro_cria_email_hash_e_cpf_cifrado(self):
		form = CadastroForm(self.dados_validos())
		self.assertTrue(form.is_valid(), form.errors)
		user = form.save()

		profile = UserProfile.objects.get(user=user)
		self.assertEqual(user.email, 'pessoa@example.com')
		self.assertEqual(user.first_name, 'Pessoa Teste')
		self.assertFalse(user.is_active)
		self.assertFalse(profile.email_verified)
		self.assertNotEqual(profile.cpf_encrypted, '52998224725')
		self.assertEqual(profile.cpf, '52998224725')
		self.assertNotEqual(profile.celular_encrypted, '11999999999')
		self.assertEqual(profile.celular, '11999999999')
		self.assertTrue(user.check_password('SenhaForte!123'))
		self.assertNotEqual(user.password, 'SenhaForte!123')

	def test_cpf_invalido_e_email_diferente_sao_rejeitados(self):
		form = CadastroForm(self.dados_validos(cpf='111.111.111-11', celular='11999999999', confirmar_email='outra@example.com'))
		self.assertFalse(form.is_valid())
		self.assertIn('cpf', form.errors)
		self.assertIn('confirmar_email', form.errors)

	def test_celular_invalido_e_rejeitado(self):
		form = CadastroForm(self.dados_validos(celular='(11) 8888-9999'))
		self.assertFalse(form.is_valid())
		self.assertIn('celular', form.errors)

	def test_username_email_e_cpf_duplicados_sao_rejeitados(self):
		original = CadastroForm(self.dados_validos())
		self.assertTrue(original.is_valid(), original.errors)
		original.save()
		duplicado = CadastroForm(self.dados_validos(username='outro_usuario'))
		self.assertFalse(duplicado.is_valid())
		self.assertIn('email', duplicado.errors)
		self.assertIn('cpf', duplicado.errors)
		self.assertIn('celular', duplicado.errors)
		duplicado_username = CadastroForm(self.dados_validos(email='outra@example.com', confirmar_email='outra@example.com'))
		self.assertFalse(duplicado_username.is_valid())
		self.assertIn('username', duplicado_username.errors)

	def test_confirmacao_de_email_ativa_a_conta(self):
		form = CadastroForm(self.dados_validos())
		self.assertTrue(form.is_valid(), form.errors)
		user = form.save()
		profile = user.profile
		token = profile.create_email_verification_token()
		response = self.client.get(f'/usuarios/confirmar-email/?uid={user.pk}&token={token}')
		self.assertRedirects(response, '/usuarios/login/')
		user.refresh_from_db()
		profile.refresh_from_db()
		self.assertTrue(user.is_active)
		self.assertTrue(profile.email_verified)
		self.assertFalse(profile.email_verification_token_hash)

	def test_conta_nao_confirmada_nao_pode_fazer_login(self):
		form = CadastroForm(self.dados_validos())
		self.assertTrue(form.is_valid(), form.errors)
		user = form.save()
		response = self.client.post('/usuarios/login/', {
			'username': user.username,
			'senha': 'SenhaForte!123',
		})
		self.assertRedirects(response, '/usuarios/login/')
		self.assertNotIn('_auth_user_id', self.client.session)

	def test_consentimento_lgpd_e_obrigatorio(self):
		form = CadastroForm(self.dados_validos(consentimento_lgpd=False))
		self.assertFalse(form.is_valid())
		self.assertIn('consentimento_lgpd', form.errors)

	def test_login_bloqueia_apos_cinco_falhas_por_ip(self):
		User.objects.create_user(username='usuario', password='SenhaForte!123', email='pessoa@example.com')
		for _ in range(5):
			response = self.client.post('/usuarios/login/', {'username': 'usuario', 'senha': 'errada'})
		self.assertRedirects(response, '/usuarios/login/')
		response = self.client.post('/usuarios/login/', {'username': 'usuario', 'senha': 'SenhaForte!123'})
		self.assertRedirects(response, '/usuarios/login/')
		self.assertNotIn('_auth_user_id', self.client.session)

	def test_login_exige_codigo_mfa_valido(self):
		user = User.objects.create_user(username='mfa_user', password='SenhaForte!123', email='mfa@example.com')
		profile = UserProfile(user=user, totp_secret=pyotp.random_base32(), mfa_enabled=True)
		profile.cpf = '52998224725'
		profile.save()

		response = self.client.post('/usuarios/login/', {'username': 'mfa_user', 'senha': 'SenhaForte!123'})
		self.assertRedirects(response, '/usuarios/login/')
		self.assertNotIn('_auth_user_id', self.client.session)

		codigo = pyotp.TOTP(profile.totp_secret).now()
		response = self.client.post('/usuarios/login/', {
			'username': 'mfa_user',
			'senha': 'SenhaForte!123',
			'codigo_mfa': codigo,
		})
		self.assertRedirects(response, '/mentorados/')
		self.assertEqual(str(user.pk), self.client.session['_auth_user_id'])
