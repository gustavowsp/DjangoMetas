from django.urls import path
from . import views

app_name = 'secao_ajuda'

urlpatterns = [
    path('', views.index, name='home'),
    path('search/', views.search_posts, name='busca'),
    path('artigo/<int:id_artigo>/read/', views.exibir_aritgo, name='artigo'),
    path('artigo/create/', views.create_artigo, name='create_artigo'),
    path('artigo/<int:id_artigo>/update/', views.update_artigo, name='update_artigo'),
]