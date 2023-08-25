from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class AcoesRealizadas(models.Model):
    nome_acao = models.CharField(max_length=255)
    data_realizacao = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING)
