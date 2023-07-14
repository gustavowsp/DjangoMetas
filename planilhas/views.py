from django.shortcuts import render,redirect
from django.contrib import messages
import planilhas.viewsfunc.view_incremento as incremento_functions
import planilhas.viewsfunc.view_operador as utils_op
import planilhas.viewsfunc.view_deflatores as utils_deflatores
import openpyxl
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime
from planilhas.models import Carteira


# Create your views here.
def index(request):
    return render(request, 'planilhas/index.html')

def incremento(request):

    if request.method == 'POST':

        carteira = request.POST.get('carteira')

        try:
            carteira_informacoes_object = Carteira.objects.get(cod_cred=carteira,ativa=True) 
        except:
            messages.add_message(request,messages.ERROR, 'A carteira informada está inativa ou é inexistente. Caso exista, contate-nos para adicionarmos esta carteira')
            return render(request, 'planilhas/metas.html')

        # C000
        try:
            #meta_op = request.FILES['meta_mae']
            incremento_meta = request.FILES['meta_filha']
            # Pegamos as duas planilhas
        except:
            messages.add_message(
                request,
                messages.WARNING, 
                "Ops! Você se esqueceu de enviar uma das planilhas"
                )
            return render(request, 'planilhas/metas.html')
            # O usuário não enviou as planilhas e recuperamos algo que não existe, ocasionando em um erro.
        
        # Verificamos que as planilhas de metas foram enviadas.


        # C001
        metas_erradas, planilhas_or_template,  = incremento_functions.informacoes_corretas(
            request,
            #carteira=carteira,
            #meta_op=meta_op,
            meta_arquivo=incremento_meta,
            meta='incremento'
        )
        

        # Verificamos se as planilhas estão corretas e se a carteira existe.

        # R000
        if metas_erradas:
            return render(
                metas_erradas, # Existe um requeste nesta variável.
                planilhas_or_template
            )
        # As metas estavam erradas então vamos retornar um erro

        incremento_meta = openpyxl.load_workbook(incremento_meta)



        # C002
        # Pegando a sheet de dentro da tupla, que foi retornada na função anteior.
        incremento_sheet_dados = planilhas_or_template[0]
        metaop_sheet_dados = planilhas_or_template[1]
    
        # Pegando os valores das planilhas.
        dados_incremento = incremento_functions.recuperar_informacoes_unicas(incremento_sheet_dados,9)
        #dados_operadores = incremento_functions.recuperar_informacoes_unicas(metaop_sheet_dados,22)
        
        competencia = list(dados_incremento.get('COMP'))[0]
        nome_credor = carteira_informacoes_object.nome_cred_padrao

        consulta = incremento_functions.QUERY_META_OPERADORES
        consulta = consulta.replace('$VARIAVEL_COMPETENCIA$',competencia).replace('$VARIAVEL_NOME_CREDOR$',nome_credor)
        itens = incremento_functions.execute_consulta(consulta)
        query_falhou = itens[2]

        if query_falhou:
            incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql
            messages.add_message(
                request,messages.
                ERROR,
                "Ops, algo deu errado. Contate o desenvolvedor, não conseguimos importar sua planilha para o banco de dados"
                )
            return render(request, 'planilhas/metas.html')
        else:
            meta_existente = itens[0].fetchall()
            incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql

        dados_teste_operador = {
            'COMPETENCIA' : set() ,
            'DATA_IMPORT' : set() ,
            'QUEM_IMPORTOU' : set() ,
            'COD_CRED' : set() ,
            'NOME_CREDOR' : set() ,
            'CENTRO_CUSTO' : set() ,
            'COD_FUNC' : set() ,
            'CPF_FUNC' : set() ,
            'NOME_FUNCIONARIO' : set() ,
            'SUPERVISOR' : set() ,
            'FRENTE' : set() ,
            'META_QTDE' : set() ,
            'META_HONORARIOS' : set() ,
            'META_REPASSE' : set() ,
            'META_VALOR' : set() ,
            'META_ATIVA' : set() ,
            'TURNO' : set() ,
            'ATUACAO' : set() ,
            'ESTAGIO' : set() ,
            'DATA_INI' : set() ,
            'DATA_FIN' : set() ,
            'TIPO_MEDICAO' : set() ,
        }
        for linha in meta_existente:
            linha_atual = 0

            for value in dados_teste_operador.values():
                value.add(linha[linha_atual])
                linha_atual += 1

        dados_operadores = dados_teste_operador

        # C003
        # Verificando se há linhas excedentes na planilha
        existem_linhas_excedentes = incremento_functions.existem_linhas_excedentes(incremento_sheet_dados)
        #existem_linhas_excedentes_dois = incremento_functions.existem_linhas_excedentes(metaop_sheet_dados)
        if existem_linhas_excedentes: #or existem_linhas_excedentes_dois:
            messages.add_message(request,messages.ERROR, 'Em sua planilha há linhas que possuem células vazias, preenchas!')
            return render(request,'planilhas/metas.html')

        # C004
        # Comparando os valores de cada coluna chave com a planilha de metas operadores
        metas_erradas = incremento_functions.comparacao_dados(request,dados_incremento,dados_operadores)
        if metas_erradas:
            request = metas_erradas[0]
            template = metas_erradas[1]
            return render(request,template)

        # Verificando se o nome está correto
        palavras_chaves = carteira_informacoes_object.palavras_chaves
        nome_carteira_errado = incremento_functions.validando_nome_carteira(request,palavras_chaves,dados_incremento)
        if nome_carteira_errado:
            return render(request, 'planilhas/metas.html')
        
        # Alterando o nome_cred na planilha para o nome padrão
        total_linhas_pagina = incremento_functions.contar_linhas(incremento_sheet_dados)
        incremento_sheet_dados = incremento_meta['Dados']  
        nome_padrao_credor = carteira_informacoes_object.nome_cred_padrao      
        incremento_functions.padronizando_nome_cartira(incremento_sheet_dados,nome_padrao_credor,total_linhas_pagina)
        
        # Pegando os novos valores, já que alterei acima.
        dados_incremento = incremento_functions.recuperar_informacoes_unicas(incremento_sheet_dados,9)


        # C005 -- Formatando células com valores diferentes de int
        row = (
            dados_incremento['META_1'],
            dados_incremento['META_2'],
            dados_incremento['META_3'],
            dados_incremento['META_4'],
            dados_incremento['META_5'],
            )   
        # Há células com outro valor a não ser int?
        if incremento_functions.existe_valores_incorretos(row):
            
            # Formatando as células incorretas
            incremento_functions.format_number(incremento_sheet_dados) 
            
            name = incremento_functions.gerador_nome()
            path = 'media/planilhas/sua_planilha-'
            incremento_meta.save(f'{path}{name}.xlsx')

            context = {
                'planilha_incorreta_url' : f'{path}{name}.xlsx',
                'path' : 'http://127.0.0.1:8000/'
            }

            messages.add_message(
                request,
                messages.ERROR,
                'Alguns dados contidos na planilhas, não são do tipo correto')
            return render(
                request, 
                'planilhas/metas.html',
                context
            ) 


        carteiras_da_meta = dados_incremento['CARTEIRA']
        competencia_da_meta = dados_incremento['COMP']
       
        puxando_meta_ativa = incremento_functions.criando_query_meta_ativa(
            carteiras_da_meta,
            competencia_da_meta,
            incremento_functions.QUERY_METATIVA_INCREMENTO_META)

        itens = incremento_functions.execute_consulta(puxando_meta_ativa)
        query_falhou = itens[2]

        if query_falhou:
            incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql
            messages.add_message(
                request,messages.
                ERROR,
                "Ops, algo deu errado. Contate o desenvolvedor, não conseguimos importar sua planilha para o banco de dados"
                )
            return render(request, 'planilhas/metas.html')
        else:
            meta_existente = itens[0].fetchall()
            incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql

        # Alterar meta antiga para inativa
        if meta_existente:
            alterando_meta_ativa = incremento_functions.criando_query_meta_ativa(
                carteiras_da_meta,
                competencia_da_meta,
                incremento_functions.ALTERANDO_METATIVA_INCREMENTO_META
                )
            itens = incremento_functions.execute_consulta(alterando_meta_ativa)
            
            importacao_nao_funcionou = itens[2] 
            if importacao_nao_funcionou:
                incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql
                messages.add_message(
                    request,messages.
                    ERROR,
                    "Ops, algo deu errado. Contate o desenvolvedor, não conseguimos alterar meta antiga no banco de dados"
                    )
                return render(request, 'planilhas/metas.html')
            else:
                itens[1].commit() # Confirmando as alterações    
                incremento_functions.desativando(itens[0],itens[1]) # Desativando 



        # C006 - Importando a meta -- Como ativa
        data_planilha_incremento = incremento_functions.get_data_meta_com_duplicatas(incremento_sheet_dados,9)# Pegando os valores da planilha
        consulta = incremento_functions.criando_valors_para_insert(data_planilha_incremento,9)# Criando a consulta -- Parte dos VALUES
        consulta_final = (incremento_functions.INSERT_INCREMENTO_META + consulta)# Juntando a consulta de VALUES com insert -- COMANDO INTO
        itens = incremento_functions.execute_consulta(consulta_final)# Importando para o banco de dados
        
        importacao_nao_funcionou = itens[2] 
        if importacao_nao_funcionou:
            incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql
            messages.add_message(
                request,messages.
                ERROR,
                "Ops, algo deu errado. Contate o desenvolvedor, não conseguimos importar sua planilha para o banco de dados"
                )
            return render(request, 'planilhas/metas.html')
        else:
            itens[1].commit() # Confirmando as alterações    
            incremento_functions.desativando(itens[0],itens[1]) # Desativando


        
        # Deu tudo certo e estamos importando
        messages.add_message(request,messages.SUCCESS, "Importada com sucesso!")
        return render(request, 'planilhas/metas.html')

    return render(request, 'planilhas/metas.html')

def valor(request):
    messages.add_message(request,messages.INFO,"Estamos desenvolvendo esta página ainda... ")
    return redirect('planilhas:HomePage') 

def deflator(request):  

    if request.method == 'POST':

        carteira = request.POST.get('carteira')
        # C000
        try:
            meta_op = request.FILES['meta_filha']
            # Pegamos as duas planilhas
        except:
            messages.add_message(
                request,
                messages.WARNING, 
                "Ops! Você se esqueceu de enviar uma das planilhas"
                )
            return render(request, 'planilhas/metas.html')
            # O usuário não enviou as planilhas e recuperamos algo que não existe, ocasionando em um erro.
        

        # C001
        metas_erradas, planilhas_or_template,  = incremento_functions.informacoes_corretas(
            request,
            #carteira=carteira,
            meta_arquivo=meta_op,
            meta='deflatores'
        )
        # Verificamos se as planilhas estão corretas e se a carteira existe.

        # R000
        if metas_erradas:
            return render(
                metas_erradas, # Existe um requeste nesta variável.
                planilhas_or_template
            )
        # As metas estavam erradas então vamos retornar um erro



        # C002
        # Pegando a sheet de dentro da tupla, que foi retornada na função anteior.
        meta_sheet_dados = planilhas_or_template[0]
        meta_op = openpyxl.load_workbook(meta_op)
        meta_sheet_dados = meta_op['Dados']
    
        # C003
        # Verificando se há linhas excedentes na planilha
        existem_linhas_excedentes = incremento_functions.existem_linhas_excedentes(meta_sheet_dados)
        if existem_linhas_excedentes:
            messages.add_message(request,messages.ERROR, 'Em sua planilha há linhas que possuem células vazias, preenchas!')
            return render(request,'planilhas/metas.html')
        
        ############## COMEÇO ALGORITMO
        competencias = set()
        for linha_da_coll_comp in meta_sheet_dados.iter_rows(min_col=1,max_col=1, min_row=4):
            
            valor_celula = linha_da_coll_comp[0].value 

            if not valor_celula:
                break

            competencia = valor_celula
            if len(competencia) != 7:
                messages.add_message(request, messages.WARNING, 'Comptência está no formatato errado, o correto é "2023-01" ')
                return render(request, 'planilhas/metas.html')
            comeco,meio,fim  = competencia [-2:],competencia[4:5],competencia[0:4]

            comptencia_formato_correto = True if comeco.isdigit() and '-' in meio and fim.isdigit() else False
            if not comptencia_formato_correto:
                messages.add_message(request, messages.WARNING, 'Os valores contidos na competência estão incorretos')
                return render(request, 'planilhas/metas.html')

            competencias.add(valor_celula)
        if len(competencias) > 1:
            messages.add_message(request, messages.WARNING, 'Existem mais de uma competência em sua planilha. Apenas uma competência é permitida')
            return render(request, 'planilhas/metas.html')


        try:
            informacao_carteira_object = Carteira.objects.get(cod_cred=carteira,ativa=True) 
        except:
            messages.add_message(request,messages.ERROR, 'A carteira informada está inativa ou é inexistente. Caso exista, contate-nos para adicionarmos esta carteira')
            return render(request, 'planilhas/metas.html')
        
        cod_cred_carteira           = informacao_carteira_object.cod_cred
        nome_padrao_carteira        = informacao_carteira_object.nome_cred_padrao
        palavras_chaves_carteira    =  informacao_carteira_object.palavras_chaves
        while True:
            palavras_chaves_carteira = palavras_chaves_carteira.replace('-',' ')
            if not '-' in palavras_chaves_carteira:
                palavras_chaves_carteira = palavras_chaves_carteira.split()
                break


        for celula in meta_sheet_dados.iter_rows(min_row=4, min_col=3, max_col=3):
            valor_celula = str(celula[0].value).strip()

            if not valor_celula ==  cod_cred_carteira:

                messages.add_message(request,messages.ERROR, 'Você selecionou a carteira incorreta... O cod cred selecionado é diferente da planiha')
                return render(request, 'planilhas/metas.html')

        for celula in meta_sheet_dados.iter_rows(min_row=4, min_col=4, max_col=4):
            valor_celula = celula[0].value
            valor_celula = str(valor_celula).strip().lower()

            for palavra in palavras_chaves_carteira:
                
                if palavra not in valor_celula:
                    messages.add_message(request,messages.ERROR, 'O nome do credor existente na planilha está incorreto, verifique!')
                    return render(request, 'planilhas/metas.html')

            celula[0].value = nome_padrao_carteira

        lista_cpfs = set()
        dados_funcionario = {

        }

        # Adicionando cpfs na lista de cpfs 
        for looping_h in meta_sheet_dados.iter_rows(min_row=4, max_col=7, min_col=7):
            cpf = str(looping_h[0].value).strip().lower()
            
            if cpf == 'none':
                break

            tamanho_cpf = len(cpf)
            if tamanho_cpf == 10:
                cpf = '0' + cpf
                looping_h[0].value = cpf
            elif tamanho_cpf == 9:
                cpf = '00' + cpf
                looping_h[0].value = cpf
            elif tamanho_cpf == 8:
                cpf = '000' + cpf
                looping_h[0].value = cpf
            elif tamanho_cpf == 7:
                cpf = '0000' + cpf
                looping_h[0].value = cpf
                
            lista_cpfs.add(cpf)

            dados_funcionario[cpf] = {
                'cpfs_query'                :   '',
                'nome_func_query'           :   '' ,
                'matricula_func_query'      :   '', 
            }

        consulta = utils_deflatores.QUERY_FUNCIONARIOS
        cpfs_iterados = 1

        # Passando cada cpf para a consulta, assim formando uma query
        for cpf in lista_cpfs:
            
            if cpfs_iterados == len(lista_cpfs):
                consulta += f"'{cpf}'"
            else:
                consulta += f"'{cpf}',"

            cpfs_iterados += 1
        
        consulta += ')'
        itens =  incremento_functions.execute_consulta(consulta)

        # Verificando se a importação funcionou e caso funcione, vamos recuperar as informações da query
        importacao_nao_funcionou = itens[2] 
        if importacao_nao_funcionou:
            incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql
            messages.add_message(
                request,messages.
                ERROR,
                "Ops, algo deu errado. Contate o desenvolvedor, não conseguimos importar sua planilha para o banco de dados"
                )
            return render(request, 'planilhas/metas.html')
        else:
            cpfs = itens[0].fetchall() # Confirmando as alterações    
            incremento_functions.desativando(itens[0],itens[1]) # Desativando
        
        for dados_func in cpfs:

            cpf_    = dados_func[1]
            nome_   = dados_func[0]
            codigo_ = dados_func[2] 

            dados_funcionario[cpf_]['cpfs_query'] = cpf_
            dados_funcionario[cpf_]['nome_func_query']  = nome_
            dados_funcionario[cpf_]['matricula_func_query'] = codigo_
        
        for linha in meta_sheet_dados.iter_rows(min_row=4, min_col=5, max_col=8):
            nome_func = str(linha[1].value).strip().lower()
            cpf_func=   str(linha[2].value).strip().lower()

            dados_dos_funcionarios =    dados_funcionario[cpf_func]
            cpf_func_query         =    str(dados_dos_funcionarios['cpfs_query']).strip().lower()
            nome_func_query        =    str(dados_dos_funcionarios['nome_func_query']).strip().lower() 

            if not nome_func in nome_func_query:
                messages.add_message(request,messages.ERROR, 'Alguns nomes de funcionários estão incorretos.')
                return render(request,'planilhas/metas.html')
            
            if not cpf_func in cpf_func_query:
                messages.add_message(request,messages.ERROR, 'Alguns nomes de funcionários estão incorretos.')
                return render(request,'planilhas/metas.html')

            linha[3].value = dados_dos_funcionarios['matricula_func_query']

        data_atual = str(datetime.now())
        data_atual = data_atual[:-3]
        usuario = 'USUARIO_TESTE'

        for linha in meta_sheet_dados.iter_rows(min_row=4, min_col=13, max_col=14):
            linha[0].value = usuario
            linha[1].value = data_atual
    

        dados = incremento_functions.get_data_meta_com_duplicatas(meta_sheet_dados,max_col=14)
        dados_arrumados = list()
        for valor in dados:
            valor.append(usuario) # Adicionando quem importou como p nultimo
            valor.append(data_atual) # Adicionando a data da importação como último
            dados_arrumados.append(valor)


            # Adicionando os campos DATA IMPORT E QUEM_IMPORTOU VIA PYTHON
            # Essses campos não existem na planilha, já na tabela existem.
            # O valor é igual à um campo já existente na planilha, então apenas vamos copiar e colar
            
        valores_insert = incremento_functions.criando_valors_para_insert(dados_arrumados,16)
        insert_consulta = utils_deflatores.INSERT_META
        consulta = insert_consulta + valores_insert

        meta_op.save('testezao.xlsx')


        itens = incremento_functions.execute_consulta(consulta)
        importacao_nao_funcionou = itens[2] 
        if importacao_nao_funcionou:
            incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql
            print(consulta)
            messages.add_message(
                request,messages.
                ERROR,
                "Ops, algo deu errado. Contate o desenvolvedor, não conseguimos importar sua planilha para o banco de dados"
                )
            return render(request, 'planilhas/metas.html')
        else:
            try:
                query_meta = itens[0].commit() # Confirmando as alterações    
            except:
                incremento_functions.desativando(itens[0],itens[1]) # Desativando

    messages.add_message(request,messages.SUCCESS, 'Meta importada com sucesso')
    return render(request, 'planilhas/metas.html')
        
def meta_operador(request):


    if request.method == 'POST':

        carteira = request.POST.get('carteira')
        # C000
        try:
            meta_op = request.FILES['meta_filha']
            # Pegamos as duas planilhas
        except:
            messages.add_message(
                request,
                messages.WARNING, 
                "Ops! Você se esqueceu de enviar uma das planilhas"
                )
            return render(request, 'planilhas/metas.html')
            # O usuário não enviou as planilhas e recuperamos algo que não existe, ocasionando em um erro.
        

        # C001
        metas_erradas, planilhas_or_template,  = incremento_functions.informacoes_corretas(
            request,
            #carteira=carteira,
            meta_arquivo=meta_op,
            meta='operadores'
        )
        # Verificamos se as planilhas estão corretas e se a carteira existe.

        # R000
        if metas_erradas:
            return render(
                metas_erradas, # Existe um requeste nesta variável.
                planilhas_or_template
            )
        # As metas estavam erradas então vamos retornar um erro



        # C002
        # Pegando a sheet de dentro da tupla, que foi retornada na função anteior.
        meta_sheet_dados = planilhas_or_template[0]
        meta_op = openpyxl.load_workbook(meta_op)



        # C002
        # Pegando a sheet de dentro da tupla, que foi retornada na função anteior.
        meta_sheet_dados = planilhas_or_template[0]
    
    
        # C003
        # Verificando se há linhas excedentes na planilha
        existem_linhas_excedentes = incremento_functions.existem_linhas_excedentes(meta_sheet_dados)
        if existem_linhas_excedentes:
            messages.add_message(request,messages.ERROR, 'Em sua planilha há linhas que possuem células vazias, preenchas!')
            return render(request,'planilhas/metas.html')
        
        ############## COMEÇO ALGORITMO
        competencias = set()
        for linha_da_coll_comp in meta_sheet_dados.iter_rows(min_col=1,max_col=1, min_row=4):
            
            valor_celula = linha_da_coll_comp[0].value 

            if not valor_celula:
                break

            competencia = valor_celula
            if len(competencia) != 7:
                messages.add_message(request, messages.WARNING, 'Comptência está no formatato errado, o correto é "2023-01" ')
                return render(request, 'planilhas/metas.html')
            comeco,meio,fim  = competencia [-2:],competencia[4:5],competencia[0:4]

            comptencia_formato_correto = True if comeco.isdigit() and '-' in meio and fim.isdigit() else False
            if not comptencia_formato_correto:
                messages.add_message(request, messages.WARNING, 'Os valores contidos na competência estão incorretos')
                return render(request, 'planilhas/metas.html')

            competencias.add(valor_celula)
        if len(competencias) > 1:
            messages.add_message(request, messages.WARNING, 'Existem mais de uma competência em sua planilha. Apenas uma competência é permitida')
            return render(request, 'planilhas/metas.html')


        data_atual = str(datetime.now())
        data_atual = data_atual[:-3]

        meta_sheet_dados = meta_op['Dados']
        for linha_da_coll_dataimport in meta_sheet_dados.iter_rows(min_col=2,max_col=2, min_row=4):
            
            if  linha_da_coll_dataimport[0].value: 
                linha_da_coll_dataimport[0].value = data_atual

        #TODO: Recuperar qual usuário esta importando
        usuario_nome = 'USUARIO_TESTE' 

        for linha_da_coll_quemimporta in meta_sheet_dados.iter_rows(min_col=3,max_col=3, min_row=4):
            if linha_da_coll_quemimporta[0].value:
                linha_da_coll_quemimporta[0].value = usuario_nome

        try:
            informacao_carteira_object = Carteira.objects.get(cod_cred=carteira,ativa=True) 
        except:
            messages.add_message(request,messages.ERROR, 'A carteira informada está inativa ou é inexistente. Caso exista, contate-nos para adicionarmos esta carteira')
            return render(request, 'planilhas/metas.html')


        palavras_chaves_carteira    =   informacao_carteira_object.palavras_chaves

        # formatando palavras chaves
        while True:
            palavras_chaves_carteira = palavras_chaves_carteira.replace('-',' ')

            if not '-' in palavras_chaves_carteira:
                break
        cod_cred_carteira           =   informacao_carteira_object.cod_cred
        palavras_chaves_carteira    = str(palavras_chaves_carteira).split()
        centro_custo_carteira       =   informacao_carteira_object.centro_custo
        nome_cred_padrao            =   informacao_carteira_object.nome_cred_padrao  


        for linha_looping_df in meta_sheet_dados.iter_rows(min_col=4, max_col=6, min_row=4):
            cod_cred_planilha = str(linha_looping_df[0].value)
            nome_credor_planilha = str(linha_looping_df[1].value).lower().strip()

            if cod_cred_planilha == 'None' or cod_cred_planilha == None:
                break

            if cod_cred_planilha != cod_cred_carteira:
                messages.add_message(request,messages.WARNING, 'Você selecionou a carteira incorreta... O cod cred selecionado é diferente da planiha')
                return render(request, 'planilhas/metas.html')

            for palavra in palavras_chaves_carteira:
                if palavra not in nome_credor_planilha:
                    messages.add_message(request,messages.WARNING, 'Você selecionou a carteira incorreta... O nome do credor selecionado é diferente da planiha')
                    return render(request, 'planilhas/metas.html')


            linha_looping_df[1].value = nome_cred_padrao

        for looping_jk in meta_sheet_dados.iter_rows(min_col=10,max_col=11, min_row=4):
            supervisor = looping_jk[0].value
            frente = looping_jk[1].value

            if not frente and not supervisor:
                continue

            if  not type(frente) == str:  
                messages.add_message(request,messages.WARNING, 'Não se pode preencher uma célula apenas com numeros na coluna de FRENTEs')  
                return render(request, 'planilhas/metas.html')
            if not type(supervisor) == str:
                messages.add_message(request,messages.WARNING, 'Não se pode preencher uma célula apenas com numeros na coluna de Supervisores')  
                return render(request, 'planilhas/metas.html')

        for looping_lo in meta_sheet_dados.iter_rows(min_col=12,max_col=15, min_row=4):
            meta_qtd,meta_honorarios,meta_repasse,meta_valor = looping_lo[0].value, looping_lo[1].value, looping_lo[2].value,looping_lo[3].value

            if not meta_qtd or not meta_honorarios or not meta_repasse or not meta_valor:
                continue

            meta_incorreta = True if type(meta_qtd) == str or type(meta_honorarios) == str or type( meta_repasse) == str or type(meta_valor) == str else False
            if meta_incorreta:
                messages.add_message(request,messages.WARNING, 'As metas devem totalmente numéricas, não pode haver caracteres')  
                return render(request, 'planilhas/metas.html')
            
        for looping_q in meta_sheet_dados.iter_rows(min_row=4, max_col=17, min_col=17):
            turno = str(looping_q[0].value).lower().strip()
            
            if turno == 'none':
                break


            turno_possibilidades = (
                'integral',
                'manha',
                'manhã',
                'tarde',
            )

            turno_incorreto = False if turno not in turno_possibilidades else True
            if not turno_incorreto:
                messages.add_message(request,messages.WARNING, 'Há erros na coluna de turnos')  
                return render(request, 'planilhas/metas.html')

        for looping_r in meta_sheet_dados.iter_rows(min_row=4, max_col=18, min_col=18):
            atuacao = looping_r[0].value

            if atuacao == None or str(atuacao).strip == 'None':
                break


            if type(atuacao) != str:
                messages.add_message(request,messages.WARNING, 'Há erros na coluna de atuação')  
                return render(request, 'planilhas/metas.html')                
 
        for looping_s in meta_sheet_dados.iter_rows(min_row=4, max_col=19, min_col=19):
            estagio = str(looping_s[0].value).lower().strip()
            
            if estagio == 'none':
                break

            estagio_possibilidades = (
                'estágio',
                'estagio',
                'amigável',
                'amigavel',
            )
            if estagio not in estagio_possibilidades:
                messages.add_message(request,messages.WARNING, 'Há erros na coluna de estagios')  
                return render(request, 'planilhas/metas.html')                
 

        contador_linha = 4

        colunas = {
            'META_QTDE'        :       'L',
            'META_HONORARIOS'  :       'M',
            'META_REPASSE'     :       'N',
            'META_VALOR'       :       'O',
        }
        for lopping_v in meta_sheet_dados.iter_rows(min_row=4,max_col=22,min_col=22):
            
            tipo_medicao = str(lopping_v[0].value).upper().strip()
            
            if tipo_medicao == 'NONE':
                break

            coluna_informada = colunas[tipo_medicao]
            linha_atual = str(contador_linha)

            celula_atual = coluna_informada + linha_atual
            celula_atual = meta_sheet_dados[celula_atual].value

            if type(celula_atual) != int:
                messages.add_message(request,messages.WARNING, 'Apenas se pode inserir inteiros nas metas!')  
                return render(request, 'planilhas/metas.html')   
                
            celula_correta = True if celula_atual and celula_atual != 0 else False
            if not celula_correta:
                messages.add_message(request,messages.WARNING, 'Você preencheu a coluna de tipo_medicao com um valor e inseriu o valor da meta em outra...')  
                return render(request, 'planilhas/metas.html')                  


            
            celulas = (
                'L' + linha_atual,
                'M' + linha_atual,
                'N' + linha_atual,
                'O' + linha_atual,
            )
            valores_preenchidos = 0
            for celula in celulas:

                valor_celula = meta_sheet_dados[celula].value

                if int(valor_celula) != 0:
                    valores_preenchidos += 1

            contador_linha += 1

            if valores_preenchidos != 1:
                messages.add_message(request,messages.WARNING, 'Você pode preencher apenas um valor das quatro colunas de meta.')  
                return render(request, 'planilhas/metas.html')   

        competencia = list(competencias)[0]
        
        ano = competencia[0:4]
        mes = competencia[5:]


        data_comeco = f'{mes}-01-{ano}'
        data_final  = f'{mes}-28-{ano}'

        for looping_tu in meta_sheet_dados.iter_rows(min_row=4, min_col=20, max_col=21):
            if looping_tu[0].value == None:
                break

            looping_tu[0].value = data_comeco
            looping_tu[1].value = data_final

        
        # Criando consulta 
        quantidade_cpf = 0
        lista_cpfs = set()
        nome_funcs = []

        # Adicionando cpfs na lista de cpfs 
        for looping_h in meta_sheet_dados.iter_rows(min_row=4, max_col=9, min_col=8):
            cpf = str(looping_h[0].value).strip().lower()
            if cpf == 'none':
                break

            nome_func = looping_h[1].value.strip().lower()

            quantidade_cpf += 1

            if len(cpf) == 10:
                cpf = '0' + cpf
                looping_h[0].value = cpf
            elif len(cpf) == 9:
                cpf = '00' + cpf
                looping_h[0].value = cpf
                
            lista_cpfs.add(cpf)
            
            nome_funcs.append(nome_func)

        consulta = utils_op.QUERY_FUNCIONARIOS
        cpfs_iterados = 1

        # Passando cada cpf para a consulta, assim formando uma query
        for cpf in lista_cpfs:
            
            if cpfs_iterados == len(lista_cpfs):
                consulta += f"'{cpf}'"
            else:
                consulta += f"'{cpf}',"

            cpfs_iterados += 1
        
        consulta += ')'
        itens =  incremento_functions.execute_consulta(consulta)

        # Verificando se a importação funcionou e caso funcione, vamos recuperar as informações da query
        importacao_nao_funcionou = itens[2] 
        if importacao_nao_funcionou:
            incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql
            messages.add_message(
                request,messages.
                ERROR,
                "Ops, algo deu errado. Contate o desenvolvedor, não conseguimos importar sua planilha para o banco de dados"
                )
            return render(request, 'planilhas/metas.html')
        else:
            cpfs = itens[0].fetchall() # Confirmando as alterações    
            incremento_functions.desativando(itens[0],itens[1]) # Desativando

        cpfs_funcionarios_query = set()
        nome_funcionarios_query = list()

        # Passando os valores(nome e cpf) da consulta para as estruturas de dados acima
        for valor in cpfs:
            nome    =   valor[0].strip().lower()
            cpf     =   valor[1].strip().lower()
            

            cpfs_funcionarios_query.add(cpf)
            nome_funcionarios_query.append(nome)

        for cpfs in lista_cpfs:
            #print(f'{cpfs}')
            if cpfs not in cpfs_funcionarios_query:
        
                messages.add_message(request,messages.WARNING, 'Há cpfs---------- de funcionários que estão incorretos em sua planilha')
                return render(request, 'planilhas/metas.html')


        for nome in nome_funcs:
            if nome not in nome_funcionarios_query:
                messages.add_message(request,messages.WARNING, 'Há nomes de funcionários que estão incorretos em sua planilha')
                return render(request, 'planilhas/metas.html')
        
        # Preenchendo a coluna meta ativa
        for celula in meta_sheet_dados.iter_rows(min_row=4,min_col=16, max_col=16):
            valor_celula = celula[0].value

            if valor_celula == None:
                break

            celula[0].value = 'SIM'
        
        query_metaoperadores =  utils_op.QUERY_META
        where_metaoperadores =  f"COMPETENCIA = '{competencia}' AND "
        where_metaoperadores += f"NOME_CREDOR = '{nome_cred_padrao}' "

        query_metaoperadores += where_metaoperadores       

        itens = incremento_functions.execute_consulta(query_metaoperadores)
        importacao_nao_funcionou = itens[2] 
        if importacao_nao_funcionou:
            incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql
            messages.add_message(
                request,messages.
                ERROR,
                "Ops, algo deu errado. Contate o desenvolvedor, não conseguimos importar sua planilha para o banco de dados"
                )
            return render(request, 'planilhas/metas.html')
        else:
            query_meta = itens[0].fetchall() # Confirmando as alterações    
            incremento_functions.desativando(itens[0],itens[1]) # Desativando
 
        if len(query_meta) != 0:
            update_metaoperadors = utils_op.UPDATE_META
            update_metaoperadors += where_metaoperadores

            itens = incremento_functions.execute_consulta(update_metaoperadors)
            
            importacao_nao_funcionou = itens[2] 
            if importacao_nao_funcionou:
                incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql
                messages.add_message(
                    request,messages.
                    ERROR,
                    "Ops, algo deu errado. Contate o desenvolvedor, não conseguimos alterar meta antiga no banco de dados"
                    )
                return render(request, 'planilhas/metas.html')
            else:
                itens[1].commit() # Confirmando as alterações    
                incremento_functions.desativando(itens[0],itens[1]) # Desativando 

        dados = incremento_functions.get_data_meta_com_duplicatas(meta_sheet_dados,max_col=22)
        valores_insert = incremento_functions.criando_valors_para_insert(dados,22)
        insert_consulta = utils_op.INSERT_META
        consulta = insert_consulta + valores_insert


        itens = incremento_functions.execute_consulta(consulta)
        importacao_nao_funcionou = itens[2] 
        if importacao_nao_funcionou:
            incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql
            print(consulta)
            messages.add_message(
                request,messages.
                ERROR,
                "Ops, algo deu errado. Contate o desenvolvedor, não conseguimos importar sua planilha para o banco de dados"
                )
            return render(request, 'planilhas/metas.html')
        else:
            try:
                query_meta = itens[0].commit() # Confirmando as alterações    
            except:
                incremento_functions.desativando(itens[0],itens[1]) # Desativando

        meta_op.save('testezao.xlsx')

        messages.add_message(request,messages.SUCCESS,'Meta importada com sucesso!')
        return render(request, 'planilhas/metas.html')
    
    return render(request, 'planilhas/metas.html')
 

