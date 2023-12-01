from django.db import models
from django.utils import timezone


# Create your models here.
class Artigo(models.Model):
    titulo_artigo = models.CharField(max_length=255,verbose_name='Titulo do artigo')
    descricao_artigo = models.CharField(max_length=100)
    
    capa_artigo = models.ImageField(upload_to=f'imagens/capas/%Y/%m/%d/',verbose_name='Capa do artigo')
    data_publicacao = models.DateTimeField(default=timezone.now)

    conteudo_artigo = models.TextField()

    def __str__(self) -> str:
        return self.titulo_artigo
    