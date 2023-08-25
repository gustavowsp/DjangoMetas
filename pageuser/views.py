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

    print('Começando a query...')
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
        ultimo_nome = nome[1].capitalize()

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
    else:
        messages.add_message(request,messages.ERROR,'Usuário ou senha não existem...')
        return render(request, 'pageuser/login.html')

    messages.add_message(request,messages.SUCCESS,'Você está autenticado!!')
    return render(request, 'pageuser/login.html')