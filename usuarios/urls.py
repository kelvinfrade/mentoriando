from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro, name="cadastro"),
    path('confirmar-email/', views.confirmar_email, name="confirmar_email"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('logout-todos/', views.logout_all, name="logout_all"),
    path('mfa/', views.configurar_mfa, name="configurar_mfa"),
    path('termos/', views.termos, name="termos"),
    path('privacidade/', views.privacidade, name="privacidade"),
]
