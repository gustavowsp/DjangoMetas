from django.shortcuts import render
from django.http import HttpResponse, Http404
from secao_ajuda.models import Artigo

    
# Create your views here.
def index(request):
    return HttpResponse('Página inicial da seção de ajuda')

def exibir_aritgo(request,id_artigo):

    artigo = None
    try:
        artigo = Artigo.objects.get(id=id_artigo)
    except:
        ...

    if not artigo:
        raise Http404('O usuário pesquisou um artigo inexistente no banco de dados')


    titulo_artigo = artigo.titulo_artigo
    return HttpResponse(f'<h1 style="text-align: center; font-family: sans-serif; margin-top:150px;">{titulo_artigo}</h1>')