from django.db import models


class Carteira(models.Model):
    cod_cred = models.CharField(max_length=255)
    palavras_chaves = models.CharField(max_length=255)
    centro_custo = models.CharField(max_length=255)
    nome_cred_padrao = models.CharField(max_length=255)
    nome_carteira = models.CharField(
        max_length=255,
        verbose_name='Nome')
    ativa = models.BooleanField(
        default=True,
        verbose_name='Credor ativo')
    
    
    def __str__(self):
        return self.nome_carteira
