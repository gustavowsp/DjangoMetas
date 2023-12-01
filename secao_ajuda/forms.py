from django_summernote.widgets import SummernoteWidget
from django import forms 
from secao_ajuda import models

class PostForm(forms.ModelForm):
    
    class Meta:
        model = models.Artigo
        fields = ('titulo_artigo','descricao_artigo','capa_artigo','conteudo_artigo')
        widgets = {
            'conteudo_artigo' : SummernoteWidget()
        }