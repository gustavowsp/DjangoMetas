from django.urls import path
from . import views

app_name = 'secao_ajuda'

urlpatterns = [
    path('', views.index, name='home'),
    path('artigo/<int:id_artigo>', views.exibir_aritgo, name='artigo'),
]