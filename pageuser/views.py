from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout,authenticate
from django.contrib.auth import login as login_django
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.contrib import messages
from pageuser.utils import consultas
from planilhas.viewsfunc import view_incremento as incremento_functions
import time
from pageuser.models import AcoesRealizadas,Atividade
import calendar
import datetime


def discover_month() -> str:

    # Descobrindo o mês atual
    mes = datetime.datetime.now().month

    meses_existentes = {
        1 : 'janeiro',
        2 : 'fevereiro',
        3 : 'março',
        4 : 'abril',
        5 : 'maio',
        6 : 'junho',    
        7 : 'julho',
        8 : 'agosto',
        9 : 'setembro',
        10 : 'outubro',
        11 : 'novembro',
        12 : 'dezembro',
    }
    
    return meses_existentes[mes].capitalize()

def dias_do_mes() -> list:

    # Descobrindo data atual
    data_atual = datetime.datetime.now()
    mes, ano = data_atual.month, data_atual.year
    dia_atual = data_atual.day


    # Descobrindo o total de dias da data atual
    monthRange = calendar.monthrange(ano,mes)
    
    # Criando uma lista com os dias
    dias = {
        1 : {}
    }

    for dia in range(monthRange[1]):
        

        if dia+1 == dia_atual:
            dias[dia+1] = {
                'tag' : 'dia_atual'
            }
        else:   
            dias[dia+1] = {}

    return dias

def get_ativades_nao_feitas(usuario):  

    def data_inicio_fim_mes() -> tuple:

        # Descobrindo o mês atual
        data = datetime.datetime.now()
        year,month = data.year, data.month
        dia = calendar.monthrange(year,month)[1]

        data_inicio = datetime.date(year,month,1)
        data_fim = datetime.date(year,month,dia)

        return data_inicio,data_fim

    atividades_existentes = Atividade.objects.all()

    data_inicio, data_fim = data_inicio_fim_mes()
    acoes_feitas = AcoesRealizadas.objects.filter(data_realizacao__range=(data_inicio, data_fim), usuario=usuario)

    acoes_nao_feitas = []

    for atividade in atividades_existentes:
        
        atividade_foi_realizada = False

        # Passando em cada ação
        for acao_feita in acoes_feitas:
            
            # Encontrou ação parou o for de cima
            if acao_feita.acao == atividade:
                atividade_foi_realizada = True        
                break
        
        if not atividade_foi_realizada:
            acoes_nao_feitas.append(atividade)

    return acoes_nao_feitas


def criando_condicao_in(dados:list) -> str:

    tamnho_da_lista = len(dados)
    condicao_where = "("
    
    informacao_atual = 1
    for dado in dados:

        if tamnho_da_lista == informacao_atual:
            condicao_where += f" '{dado}' "
            continue

        condicao_where += f" '{dado}', "
        informacao_atual += 1

    condicao_where += ")"
    return condicao_where 

def formatar_data(data:str) -> str:
    
    data_formatada = data

    while '-' in data_formatada:
        data_formatada = data_formatada.replace('-','')

    return data_formatada


# Create your views here.
def registro(request):
    
    if not request.user.is_staff :
        messages.add_message(request,messages.INFO,'Você precisa ser um super usuário para entrar naquela página...')
        return redirect('pagina_usuario:login') 
    
    if request.method == 'GET':
        return render(request, 'pageuser/registrar.html')


    usuarios_registrados = User.objects.all()
    cpfs_de_users_registrados = list()

    # Recuperando todos os cpfs registrados
    for usuario in usuarios_registrados:
        cpf_user = usuario.username
        
        # Caso o username não seja um cpf, provavelmente é um superuser então não vamos fazer nada
        if not cpf_user.isdigit():
            continue

        cpfs_de_users_registrados.append(cpf_user)

    if cpfs_de_users_registrados:
        consulta = consultas.QUERY_FUNCIONARIOS + criando_condicao_in(cpfs_de_users_registrados)
    else:
        consulta = consultas.QUERY_FUNCIONARIOS_SEM_CPF

    # Realizando uma query pelos novos funcionários
    itens = incremento_functions.execute_consulta(consulta)
    query_falhou = itens[2]

    if query_falhou:
        incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql
        messages.add_message(
            request,messages.
            ERROR,
            "Ops, algo deu errado. Contate o desenvolvedor, não conseguimos importar sua planilha para o banco de dados"
            )
        return HttpResponse('Deu pau')
    else:
        dados_funcionarios = itens[0].fetchall()
        incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql
        print('Query finalizada...')

    novos_usuarios = []
    usuarios_criados = 0
    for tupla_com_dados in dados_funcionarios:
        novo_usuario = User()

        nome = tupla_com_dados[0].split(' ')
        primeiro_nome = nome[0].capitalize()
        ultimo_nome = ' '.join(nome[1:]).capitalize()
        cpf_user = tupla_com_dados[1]
                
        novo_usuario.username = cpf_user
        novo_usuario.first_name = primeiro_nome
        novo_usuario.last_name = ultimo_nome
        novo_usuario.password = make_password(cpf_user)

        novos_usuarios.append(novo_usuario)
        usuarios_criados += 1
        print(f'Total de usuáriso criados: {usuarios_criados}')
    
    # Registrando vários instâncias no banco de dados
    User.objects.bulk_create(novos_usuarios)

    messages.add_message(request,messages.SUCCESS,'Usuários cadastrados!')
    return render(request, 'pageuser/registrar.html')

def sair(request):
    
    if not request.user.is_authenticated :
        messages.add_message(request,messages.INFO,'Você precisa estar logado para entrar naquela página...')
        return redirect('pagina_usuario:login') 
    
    logout(request)

    messages.add_message(request,messages.SUCCESS,'Você está offline')

    return redirect('pagina_usuario:login') 

def login(request):
    
    if request.method == 'GET':
        return render(request, 'pageuser/login.html')
    
    if request.user.is_authenticated:
        return redirect('pagina_usuario:login')

    cpf_usuario = request.POST.get('cpf')
    username = cpf_usuario
    password = cpf_usuario

    user = authenticate(username=username,password=password)

    if user:
        login_django(request,user)
        messages.success(request,'Você foi autenticado!')
        return redirect('pagina_usuario:dashboard')
    
    else:
        messages.add_message(request,messages.ERROR,'Usuário ou senha não existem...')
        return render(request, 'pageuser/login.html')

    messages.add_message(request,messages.SUCCESS,'Você está autenticado!!')
    return render(request, 'pageuser/login.html')

def dashboard(request):

    if not request.user.is_authenticated:
        messages.add_message(request,messages.INFO,'Você precisa estar autenticado para entrar em sua dashboard')
        return redirect('pagina_usuario:login')
    
    usuario = request.user

    acoes_feitas = AcoesRealizadas.objects.filter(usuario=usuario).order_by('-data_realizacao')

    print(dias_do_mes())

    context = {
        'acoes_feitas' : acoes_feitas,
        'usuario' : usuario,
        'calendario' : {
            'mes' : discover_month(),
            'dias_do_mes' : dias_do_mes()
        },
        'pendencias' : get_ativades_nao_feitas(usuario)
    }

    return render(
        request,
        'pageuser/dashuser.html',
        context
    )    
