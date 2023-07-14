from django.db import models

# Create your models here.
class Artigo(models.Model):
    titulo_artigo = models.CharField(max_length=255,verbose_name='Titulo do artigo')
    descricao_artigo = models.CharField(max_length=100)
    capa_artigo = models.ImageField(upload_to=f'imagens/capas/%Y/%m/%d/',verbose_name='Capa do artigo')
    
    primeiro_texto = models.TextField()
    primeira_imagem =  models.ImageField(null=True, blank=True,upload_to=f'imagens/primeira/%Y/%m/%d/',verbose_name='Capa do artigo') 

    segundo_texto = models.TextField(null=True, blank=True)
    segunda_imagem =  models.ImageField(null=True, blank=True, upload_to=f'imagens/segunda/%Y/%m/%d/',verbose_name='Capa do artigo') 


    def __str__(self) -> str:
        return self.titulo_artigo