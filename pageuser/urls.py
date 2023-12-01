from pageuser import views
from django.urls import path

app_name = 'pagina_usuario'

urlpatterns = [
    path('registar/',views.registro, name='registro'),
    path('',views.login, name='login'),
    path('sair/', views.sair, name='sair'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
