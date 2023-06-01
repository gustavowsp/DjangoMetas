from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'planilhas/index.html')




def deflator(request):
    
    if request.method == 'POST':
        print(request.FILES['valopremio'])
        return render(request, 'planilhas/metaincremento.html')
    
    return render(request, 'planilhas/deflatores.html')


def incremento(request):

    if request.method == 'POST':
        print(request.FILES)
        return render(request, 'planilhas/metaincremento.html')
    
    return render(request, 'planilhas/metaincremento.html')


def valor(request):

    if request.method == 'POST':
        print(request.FILES)
        return render(request, 'planilhas/valorpremio.html')
    
    return render(request, 'planilhas/valorpremio.html')

