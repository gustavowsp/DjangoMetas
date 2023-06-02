from django.shortcuts import render
import openpyxl
import pyodbc


# Create your views here.
def index(request):
    return render(request, 'planilhas/index.html')




def valor(request):
    
    if request.method == 'POST':

        #Verificando se a planilhas existe
        try:
            request.FILES['valorpremio'] # Pegando a planilha de valor prêmio
        except:
            return render(request, 'planilhas/valorpremio.html')

        #Começando a tratar a planilha
        planilha = openpyxl.load_workbook(request.FILES['valorpremio'])
        planilha = planilha['Dados']

        for row in planilha.iter_rows(min_row=4):
            print(row[0].value)

        

    else:
        pass

    return render(request, 'planilhas/valorpremio.html')


def incremento(request):

    if request.method == 'POST':
        return render(request, 'planilhas/metaincremento.html')
    
    return render(request, 'planilhas/metaincremento.html')


def deflator(request):

    if request.method == 'POST':
        return render(request, 'planilhas/valorpremio.html')
    
    return render(request, 'planilhas/valorpremio.html')

