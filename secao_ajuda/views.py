from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, Http404
from secao_ajuda.models import Artigo
from django.core.paginator import Paginator
from django.db.models import Q
from secao_ajuda import forms



def is_number(number):

    # Checando se é um número
    try:
        page_index = int(number)
    except:
        page_index = None

    return page_index

# Create your views here.
def index(request):

    artigos = Artigo.objects.all()

    # Criando a paginação
    artigos_paginacao = Paginator(artigos,15)

    # Descobrindo a página desejada 
    page_index = request.GET.get('page',1)

    # Checando se é um número
    page_index = is_number(page_index)

    if not page_index:
        page_index = 1

    if page_index > artigos_paginacao.num_pages:
        page_index = 1

    paginacao = artigos_paginacao.page(page_index)


    context = {
            'artigos' : paginacao,
            'index' : True
        }

    return render(request,'secao_ajuda/busca-artigo.html',context)

def search_posts(request):
    
    
    q = request.GET.get('q','')

    if not q:
        return redirect('secao_ajuda:home')


    artigos = Artigo.objects.filter(
        Q(titulo_artigo__icontains = q) |
        Q(descricao_artigo__icontains = q) 
    )

    # Criando a paginação
    artigos_paginacao = Paginator(artigos,15)

    # Descobrindo a página desejada 
    page_index = request.GET.get('page',1)

    # Checando se é um número
    page_index = is_number(page_index)

    if not page_index:
        page_index = 1

    if page_index > artigos_paginacao.num_pages:
        page_index = 1

    paginacao = artigos_paginacao.page(page_index)


    context = {
        'artigos' : paginacao
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

    artigos_em_destaque = Artigo.objects.all().order_by('-id')

    context = {
        'artigo' : artigo,
        'artigos_em_destaque' : artigos_em_destaque
    }

    return render(request,'secao_ajuda/artigo.html',context)

def create_artigo(request):
    
    form_action = reverse('secao_ajuda:create_artigo')

    if request.method == 'GET':
        form = forms.PostForm()
    else:
        form = forms.PostForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            artigo = form.save()
            
            return redirect('secao_ajuda:artigo', id_artigo=artigo.id)

    context = {
        'form' : form,
        'form_action' : form_action
    }

    return render(request,'secao_ajuda/teste.html', context)

def update_artigo(request,id_artigo):

    form_action = reverse('secao_ajuda:update_artigo', args=(id_artigo,))
    artigo = get_object_or_404(Artigo, id=id_artigo)

    if request.method == 'GET':
        form = forms.PostForm(instance=artigo)
    else:
        form = forms.PostForm(instance=artigo, data=request.POST, files=request.FILES)

        if form.is_valid():
            artigo = form.save()
            
            return redirect('secao_ajuda:artigo', id_artigo=artigo.id)


    context = {
        'form' : form,
        'form_action' : form_action
    }

    return render(request,'secao_ajuda/teste.html', context)

