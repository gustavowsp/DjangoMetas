from django.db import models
from django.utils import timezone


# Create your models here.
class Artigo(models.Model):
    titulo_artigo = models.CharField(max_length=255,verbose_name='Titulo do artigo')
    descricao_artigo = models.CharField(max_length=100)
    capa_artigo = models.ImageField(upload_to=f'imagens/capas/%Y/%m/%d/',verbose_name='Capa do artigo')
    data_publicacao = models.DateTimeField(default=timezone.now)


    primeiro_texto = models.TextField()
    primeira_imagem =  models.ImageField(null=True, blank=True,upload_to=f'imagens/primeira/%Y/%m/%d/',verbose_name='Primeira imagem') 

    segundo_texto = models.TextField(null=True, blank=True)
    segunda_imagem =  models.ImageField(null=True, blank=True, upload_to=f'imagens/segunda/%Y/%m/%d/',verbose_name='Segunda imagem') 

    em_destaque = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.titulo_artigo
    
# class ArtigosEmDestaque(models.Model):
#     artigo = models.ForeignKey(Artigo, on_delete=models.CASCADE)
#     em_destaque = models.BooleanField(default=False)