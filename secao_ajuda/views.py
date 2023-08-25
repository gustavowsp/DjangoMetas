from django.shortcuts import render
from django.http import HttpResponse, Http404
from secao_ajuda.models import Artigo

    
# Create your views here.
def index(request):

    artigos = Artigo.objects.filter(em_destaque=True)

    context = {
        'artigos' : artigos
    }

    return render(request,'secao_ajuda/busca-artigo.html',context)

def exibir_aritgo(request,id_artigo):

    artigo = None
    try:
        artigo = Artigo.objects.get(id=id_artigo)
    except:
        ...

    if not artigo:
        raise Http404('O usuário pesquisou um artigo inexistente no banco de dados')

    artigos_em_destaque = Artigo.objects.all().filter(em_destaque=True).order_by('-id')

    context = {
        'artigo' : artigo,
        'artigos_em_destaque' : artigos_em_destaque
    }

    return render(request,'secao_ajuda/artigo.html',context)