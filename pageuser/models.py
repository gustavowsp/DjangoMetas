from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Atividade(models.Model):
    nome_atividade = models.CharField(max_length=125)

    def __str__(self) -> str:
        return self.nome_atividade

class AcoesRealizadas(models.Model):

    class Meta:
        verbose_name = 'Ação Realizada'
        verbose_name_plural = 'Ações realizadas'

    acao = models.ForeignKey(Atividade, on_delete=models.DO_NOTHING)
    data_realizacao = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return self.acao.nome_atividade
